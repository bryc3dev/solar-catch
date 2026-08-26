"""Number entities for Solar Catch."""
from __future__ import annotations

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    CONF_ABOVE_THRESHOLD_SECONDS,
    CONF_APPLIANCE_POWER_W,
    CONF_BELOW_THRESHOLD_SECONDS,
    CONF_MIN_RUNTIME_MINUTES,
    CONF_START_THRESHOLD_W,
    DOMAIN,
)
from .coordinator import SolarCatchCoordinator


NUMBER_DESCRIPTIONS = [
    (CONF_START_THRESHOLD_W, "Start threshold", UnitOfPower.WATT, -10000, 20000, 50),
    (CONF_ABOVE_THRESHOLD_SECONDS, "Above time", "s", 0, 3600, 10),
    (CONF_BELOW_THRESHOLD_SECONDS, "Below time", "s", 0, 3600, 10),
    (CONF_MIN_RUNTIME_MINUTES, "Min runtime", UnitOfTime.MINUTES, 0, 720, 5),
    (CONF_APPLIANCE_POWER_W, "Fallback draw", UnitOfPower.WATT, 0, 20000, 50),
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SolarCatchNumber(coordinator, entry, *desc) for desc in NUMBER_DESCRIPTIONS])


class SolarCatchNumber(CoordinatorEntity[SolarCatchCoordinator], NumberEntity):
    _attr_has_entity_name = True
    _attr_mode = NumberMode.BOX

    def __init__(self, coordinator: SolarCatchCoordinator, entry: ConfigEntry, key: str, name: str, unit: str, minimum: float, maximum: float, step: float) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_native_unit_of_measurement = unit
        self._attr_native_min_value = minimum
        self._attr_native_max_value = maximum
        self._attr_native_step = step
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title or "Solar Catch",
            "manufacturer": "Solar Catch",
        }

    @property
    def native_value(self) -> float:
        return float(self.coordinator.get_setting(self._key) or 0)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_set_setting(self._key, value)
