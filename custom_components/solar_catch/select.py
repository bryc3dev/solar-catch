"""Select entities for Solar Catch."""
from __future__ import annotations

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import CONF_CONTROL_MODE, DOMAIN, MODE_LABELS, MODE_OPTIONS, MODE_VALUES
from .coordinator import SolarCatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities([SolarCatchModeSelect(coordinator, entry)])


class SolarCatchModeSelect(CoordinatorEntity[SolarCatchCoordinator], SelectEntity):
    _attr_has_entity_name = True
    _attr_name = "Mode"
    _attr_options = [MODE_LABELS[o] for o in MODE_OPTIONS]

    def __init__(self, coordinator: SolarCatchCoordinator, entry: ConfigEntry) -> None:
        super().__init__(coordinator)
        self._attr_unique_id = f"{entry.entry_id}_{CONF_CONTROL_MODE}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title or "Solar Catch",
            "manufacturer": "Solar Catch",
        }

    @property
    def current_option(self) -> str:
        return MODE_LABELS.get(str(self.coordinator.get_setting(CONF_CONTROL_MODE)), MODE_LABELS[MODE_OPTIONS[0]])

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_set_setting(CONF_CONTROL_MODE, MODE_VALUES.get(option, MODE_OPTIONS[0]))
