"""Config flow for Solar Catch."""
from __future__ import annotations

from typing import Any

import voluptuous as vol
from homeassistant import config_entries
from homeassistant.helpers import selector

from .const import (
    CONF_ABOVE_THRESHOLD_SECONDS,
    CONF_APPLIANCE_POWER_ENTITY,
    CONF_APPLIANCE_POWER_W,
    CONF_APPLIANCE_SWITCH,
    CONF_BELOW_THRESHOLD_SECONDS,
    CONF_CONTROL_MODE,
    CONF_ENABLED,
    CONF_END_TIME,
    CONF_MIN_RUNTIME_MINUTES,
    CONF_POWER_ENTITY,
    CONF_START_THRESHOLD_W,
    CONF_START_TIME,
    CONF_TOP_UP_ENABLED,
    DEFAULTS,
    DOMAIN,
    MODE_LABELS,
    MODE_OPTIONS,
)


def _schema(defaults: dict[str, Any] | None = None) -> vol.Schema:
    defaults = {**DEFAULTS, **(defaults or {})}
    schema: dict[Any, Any] = {
        vol.Required(CONF_POWER_ENTITY, default=defaults.get(CONF_POWER_ENTITY, "")): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_APPLIANCE_SWITCH, default=defaults.get(CONF_APPLIANCE_SWITCH, "")): selector.EntitySelector(
            selector.EntitySelectorConfig(domain=["switch", "input_boolean"])
        ),
        vol.Optional(CONF_APPLIANCE_POWER_ENTITY, default=defaults.get(CONF_APPLIANCE_POWER_ENTITY, "")): selector.EntitySelector(
            selector.EntitySelectorConfig(domain="sensor")
        ),
        vol.Required(CONF_APPLIANCE_POWER_W, default=float(defaults[CONF_APPLIANCE_POWER_W])): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=20000, step=50, unit_of_measurement="W", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_START_THRESHOLD_W, default=float(defaults[CONF_START_THRESHOLD_W])): selector.NumberSelector(
            selector.NumberSelectorConfig(min=-10000, max=20000, step=50, unit_of_measurement="W", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_ABOVE_THRESHOLD_SECONDS, default=int(defaults[CONF_ABOVE_THRESHOLD_SECONDS])): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=3600, step=10, unit_of_measurement="s", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_BELOW_THRESHOLD_SECONDS, default=int(defaults[CONF_BELOW_THRESHOLD_SECONDS])): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=3600, step=10, unit_of_measurement="s", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_MIN_RUNTIME_MINUTES, default=int(defaults[CONF_MIN_RUNTIME_MINUTES])): selector.NumberSelector(
            selector.NumberSelectorConfig(min=0, max=720, step=5, unit_of_measurement="min", mode=selector.NumberSelectorMode.BOX)
        ),
        vol.Required(CONF_START_TIME, default=str(defaults[CONF_START_TIME])): selector.TimeSelector(),
        vol.Required(CONF_END_TIME, default=str(defaults[CONF_END_TIME])): selector.TimeSelector(),
        vol.Required(CONF_ENABLED, default=bool(defaults[CONF_ENABLED])): selector.BooleanSelector(),
        vol.Required(CONF_TOP_UP_ENABLED, default=bool(defaults[CONF_TOP_UP_ENABLED])): selector.BooleanSelector(),
        vol.Required(CONF_CONTROL_MODE, default=str(defaults[CONF_CONTROL_MODE])): selector.SelectSelector(
            selector.SelectSelectorConfig(options=[MODE_LABELS[o] for o in MODE_OPTIONS], mode=selector.SelectSelectorMode.DROPDOWN)
        ),
    }
    return vol.Schema(schema)


def _normalize_user_input(user_input: dict[str, Any]) -> dict[str, Any]:
    data = dict(user_input)
    # The select in the options/config form displays friendly labels. Store the raw mode key.
    label_to_mode = {v: k for k, v in MODE_LABELS.items()}
    mode = data.get(CONF_CONTROL_MODE)
    if mode in label_to_mode:
        data[CONF_CONTROL_MODE] = label_to_mode[mode]
    return data


class SolarCatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Catch."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            data = _normalize_user_input(user_input)
            title = "Solar Catch"
            switch = data.get(CONF_APPLIANCE_SWITCH)
            if switch:
                title = f"Solar Catch {switch.split('.')[-1].replace('_', ' ').title()}"
            return self.async_create_entry(title=title, data=data)

        return self.async_show_form(step_id="user", data_schema=_schema())

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SolarCatchOptionsFlow()


class SolarCatchOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Solar Catch."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=_normalize_user_input(user_input))
        defaults = {**self.config_entry.data, **self.config_entry.options}
        # Show a friendly label for mode in the options form.
        defaults[CONF_CONTROL_MODE] = MODE_LABELS.get(defaults.get(CONF_CONTROL_MODE), MODE_LABELS[MODE_OPTIONS[0]])
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))
