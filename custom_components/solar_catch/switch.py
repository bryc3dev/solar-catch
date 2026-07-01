"""Switches for Solar Catch."""
from __future__ import annotations

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_ENABLED, DOMAIN
from .coordinator import SolarCatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SolarCatchEnableSwitch(coordinator, entry)])


class SolarCatchEnableSwitch(CoordinatorEntity[SolarCatchCoordinator], SwitchEntity):
    _attr_has_entity_name = True
    _attr_name = "Enabled"

    def __init__(self, coordinator: SolarCatchCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_enabled"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": "Solar Catch",
            "manufacturer": "Solar Catch",
        }

    @property
    def is_on(self) -> bool:
        return bool(self.coordinator.get_setting(CONF_ENABLED))

    async def async_turn_on(self, **kwargs) -> None:
        await self.coordinator.async_set_setting(CONF_ENABLED, True)

    async def async_turn_off(self, **kwargs) -> None:
        await self.coordinator.async_set_setting(CONF_ENABLED, False)
