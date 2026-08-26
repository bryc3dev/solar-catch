"""Time entities for Solar Catch."""
from __future__ import annotations

from datetime import time

from homeassistant.components.time import TimeEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_END_TIME, CONF_START_TIME, DOMAIN
from .coordinator import SolarCatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SolarCatchTime(coordinator, entry, CONF_START_TIME, "Start"),
            SolarCatchTime(coordinator, entry, CONF_END_TIME, "End"),
        ]
    )


class SolarCatchTime(CoordinatorEntity[SolarCatchCoordinator], TimeEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SolarCatchCoordinator, entry: ConfigEntry, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_name = name
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title or "Solar Catch",
            "manufacturer": "Solar Catch",
        }

    @property
    def native_value(self) -> time:
        value = str(self.coordinator.get_setting(self._key) or "00:00:00")
        parts = value.split(":")
        return time(int(parts[0]), int(parts[1]), int(parts[2]) if len(parts) > 2 else 0)

    async def async_set_value(self, value: time) -> None:
        await self.coordinator.async_set_setting(self._key, value.strftime("%H:%M:%S"))
