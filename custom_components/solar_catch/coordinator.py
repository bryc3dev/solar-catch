"""Controller/coordinator for Solar Catch."""
from __future__ import annotations

import logging
from dataclasses import dataclass
from datetime import date, datetime, time, timedelta
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.const import STATE_UNAVAILABLE, STATE_UNKNOWN
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import (
    CONF_ABOVE_THRESHOLD_SECONDS,
    CONF_APPLIANCE_POWER_W,
    CONF_APPLIANCE_SWITCH,
    CONF_BELOW_THRESHOLD_SECONDS,
    CONF_ENABLED,
    CONF_END_TIME,
    CONF_MIN_RUNTIME_MINUTES,
    CONF_POWER_ENTITY,
    CONF_START_THRESHOLD_W,
    CONF_START_TIME,
    DEFAULTS,
    DOMAIN,
)

_LOGGER = logging.getLogger(__name__)

_UNAVAILABLE = {STATE_UNAVAILABLE, STATE_UNKNOWN, "none", ""}
_OFF_STATES = {"off", "false", "False", "0"}
_UNIT_MULTIPLIERS = {"w": 1.0, "kw": 1000.0, "mw": 1_000_000.0}


@dataclass
class SolarCatchState:
    status: str = "Starting"
    mode: str = "startup"
    raw_power_w: float | None = None
    decision_power_w: float | None = None
    runtime_today_min: float = 0.0
    remaining_runtime_min: float = 0.0
    latest_start_time: str | None = None
    above_for_s: int = 0
    below_for_s: int = 0
    enabled: bool = True


class SolarCatchCoordinator(DataUpdateCoordinator[SolarCatchState]):
    """Simple hot-water/excess-power controller."""

    def __init__(self, hass: HomeAssistant, entry: ConfigEntry) -> None:
        self.entry = entry
        self.settings: dict[str, Any] = {**DEFAULTS, **entry.data, **entry.options}
        self._last_tick: datetime | None = None
        self._runtime_day: date | None = None
        self._runtime_today = timedelta()
        self._above_since: datetime | None = None
        self._below_since: datetime | None = None
        self._last_controlled_action: str | None = None
        self._state = SolarCatchState(enabled=bool(self.settings.get(CONF_ENABLED, True)))

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}_{entry.entry_id}",
            update_interval=timedelta(seconds=30),
        )

    def get_setting(self, key: str) -> Any:
        return self.settings.get(key, DEFAULTS.get(key))

    async def async_set_setting(self, key: str, value: Any) -> None:
        self.settings[key] = value
        new_options = {**self.entry.options, key: value}
        self.hass.config_entries.async_update_entry(self.entry, options=new_options)
        await self.async_request_refresh()

    def _parse_time(self, value: str | time | None, fallback: str) -> time:
        if isinstance(value, time):
            return value
        value = value or fallback
        parts = str(value).split(":")
        return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)

    def _read_power_w(self, entity_id: str | None) -> float | None:
        if not entity_id:
            return None
        state = self.hass.states.get(entity_id)
        if state is None or state.state in _UNAVAILABLE:
            return None
        try:
            value = float(state.state)
        except (TypeError, ValueError):
            return None
        unit = str(state.attributes.get("unit_of_measurement", "W")).lower().strip()
        return value * _UNIT_MULTIPLIERS.get(unit, 1.0)

    def _switch_is_on(self) -> bool:
        entity_id = self.get_setting(CONF_APPLIANCE_SWITCH)
        state = self.hass.states.get(entity_id) if entity_id else None
        return bool(state and state.state not in _OFF_STATES and state.state not in _UNAVAILABLE)

    async def _turn_on(self, reason: str) -> None:
        entity_id = self.get_setting(CONF_APPLIANCE_SWITCH)
        if not entity_id or self._switch_is_on():
            return
        await self.hass.services.async_call(
            entity_id.split(".")[0],
            "turn_on",
            {"entity_id": entity_id},
            blocking=False,
        )
        self._last_controlled_action = f"on: {reason}"
        _LOGGER.info("Solar Catch turned ON %s: %s", entity_id, reason)

    async def _turn_off(self, reason: str) -> None:
        entity_id = self.get_setting(CONF_APPLIANCE_SWITCH)
        if not entity_id or not self._switch_is_on():
            return
        await self.hass.services.async_call(
            entity_id.split(".")[0],
            "turn_off",
            {"entity_id": entity_id},
            blocking=False,
        )
        self._last_controlled_action = f"off: {reason}"
        _LOGGER.info("Solar Catch turned OFF %s: %s", entity_id, reason)

    async def _async_update_data(self) -> SolarCatchState:
        now = datetime.now()
        if self._last_tick is None:
            delta = timedelta()
        else:
            delta = now - self._last_tick
        self._last_tick = now

        if self._runtime_day != now.date():
            self._runtime_day = now.date()
            self._runtime_today = timedelta()
            self._above_since = None
            self._below_since = None

        enabled = bool(self.get_setting(CONF_ENABLED))
        appliance_on = self._switch_is_on()
        if appliance_on:
            self._runtime_today += delta

        raw_power = self._read_power_w(self.get_setting(CONF_POWER_ENTITY))
        appliance_power = float(self.get_setting(CONF_APPLIANCE_POWER_W) or 0)
        threshold = float(self.get_setting(CONF_START_THRESHOLD_W) or 0)
        above_seconds = int(self.get_setting(CONF_ABOVE_THRESHOLD_SECONDS) or 0)
        below_seconds = int(self.get_setting(CONF_BELOW_THRESHOLD_SECONDS) or 0)
        min_runtime_min = float(self.get_setting(CONF_MIN_RUNTIME_MINUTES) or 0)
        start_time = self._parse_time(self.get_setting(CONF_START_TIME), DEFAULTS[CONF_START_TIME])
        end_time = self._parse_time(self.get_setting(CONF_END_TIME), DEFAULTS[CONF_END_TIME])
        start_dt = datetime.combine(now.date(), start_time)
        end_dt = datetime.combine(now.date(), end_time)
        if end_dt <= start_dt:
            end_dt += timedelta(days=1)

        target_runtime = timedelta(minutes=min_runtime_min)
        remaining_runtime = max(target_runtime - self._runtime_today, timedelta())
        latest_start = end_dt - remaining_runtime
        in_window = start_dt <= now <= end_dt
        can_start = now >= start_dt
        force_run = enabled and can_start and remaining_runtime > timedelta() and now >= latest_start
        complete = self._runtime_today >= target_runtime

        # If the appliance is already on, raw grid/export power includes its draw.
        # Add the configured appliance draw back in so threshold decisions use
        # the estimated excess that existed before/without the appliance.
        decision_power = None if raw_power is None else raw_power + (appliance_power if appliance_on else 0.0)

        if decision_power is None:
            self._above_since = None
            self._below_since = None
            status = "Power sensor unavailable"
            mode = "sensor_unavailable"
        else:
            if decision_power >= threshold:
                self._above_since = self._above_since or now
                self._below_since = None
            else:
                self._below_since = self._below_since or now
                self._above_since = None

            above_for = int((now - self._above_since).total_seconds()) if self._above_since else 0
            below_for = int((now - self._below_since).total_seconds()) if self._below_since else 0

            if not enabled:
                status = "Disabled"
                mode = "disabled"
            elif complete:
                status = f"Complete: runtime {self._runtime_today.total_seconds()/60:.0f} min reached"
                mode = "complete"
                await self._turn_off("daily minimum runtime reached")
            elif not can_start:
                status = f"Waiting for start time {start_time.strftime('%H:%M')}"
                mode = "before_start"
            elif force_run:
                status = f"Forced run: {remaining_runtime.total_seconds()/60:.0f} min remaining before end time"
                mode = "forced_run"
                await self._turn_on("latest start time reached")
            elif appliance_on and below_for >= below_seconds:
                status = f"Below threshold for {below_for}s; turning off"
                mode = "below_threshold"
                await self._turn_off("below threshold timer elapsed")
            elif (not appliance_on) and in_window and above_for >= above_seconds:
                status = f"Above threshold for {above_for}s; turning on"
                mode = "above_threshold"
                await self._turn_on("above threshold timer elapsed")
            elif appliance_on:
                status = f"Running: decision power {decision_power:.0f}W, runtime {self._runtime_today.total_seconds()/60:.0f} min"
                mode = "running"
            else:
                status = f"Waiting: decision power {decision_power:.0f}W / threshold {threshold:.0f}W"
                mode = "waiting"

        state = SolarCatchState(
            status=status,
            mode=mode,
            raw_power_w=raw_power,
            decision_power_w=decision_power,
            runtime_today_min=self._runtime_today.total_seconds() / 60,
            remaining_runtime_min=remaining_runtime.total_seconds() / 60,
            latest_start_time=latest_start.strftime("%H:%M:%S"),
            above_for_s=int((now - self._above_since).total_seconds()) if self._above_since else 0,
            below_for_s=int((now - self._below_since).total_seconds()) if self._below_since else 0,
            enabled=enabled,
        )
        self._state = state
        return state
