"""Switches for Solar Catch."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ENABLED, CONF_TOP_UP_ENABLED, DOMAIN
from .coordinator import SolarCatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([
        SolarCatchSwitch(coordinator, entry, CONF_ENABLED, "Enabled"),
        SolarCatchSwitch(coordinator, entry, CONF_TOP_UP_ENABLED, "Top Up"),
    ])


class SolarCatchSwitch(CoordinatorEntity[SolarCatchCoordinator], SwitchEntity):
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
    def is_on(self) -> bool:
        return bool(self.coordinator.get_setting(self._key))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_setting(self._key, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_setting(self._key, False)
