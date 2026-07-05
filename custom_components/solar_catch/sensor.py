"""Sensors for Solar Catch."""
from __future__ import annotations

from homeassistant.components.sensor import SensorDeviceClass, SensorEntity, SensorStateClass
from homeassistant.const import UnitOfPower, UnitOfTime
from homeassistant.core import HomeAssistant
from homeassistant.config_entries import ConfigEntry
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN
from .coordinator import SolarCatchCoordinator


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry, async_add_entities) -> None:
    coordinator: SolarCatchCoordinator = hass.data[DOMAIN][entry.entry_id]
    async_add_entities(
        [
            SolarCatchStatusSensor(coordinator, entry),
            SolarCatchModeSensor(coordinator, entry),
            SolarCatchRuntimeSensor(coordinator, entry),
            SolarCatchRemainingRuntimeSensor(coordinator, entry),
            SolarCatchLatestStartSensor(coordinator, entry),
            SolarCatchDecisionPowerSensor(coordinator, entry),
            SolarCatchAboveForSensor(coordinator, entry),
            SolarCatchBelowForSensor(coordinator, entry),
        ]
    )


class SolarCatchBaseSensor(CoordinatorEntity[SolarCatchCoordinator], SensorEntity):
    _attr_has_entity_name = True

    def __init__(self, coordinator: SolarCatchCoordinator, entry: ConfigEntry, key: str, name: str) -> None:
        super().__init__(coordinator)
        self._key = key
        self._attr_unique_id = f"{entry.entry_id}_{key}"
        self._attr_name = name
        self._attr_device_info = {
            "identifiers": {(DOMAIN, entry.entry_id)},
            "name": entry.title or "Solar Catch",
            "manufacturer": "Solar Catch",
        }


class SolarCatchStatusSensor(SolarCatchBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "status", "Status")

    @property
    def native_value(self):
        return self.coordinator.data.status


class SolarCatchModeSensor(SolarCatchBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "mode_sensor", "Mode status")

    @property
    def native_value(self):
        return self.coordinator.data.mode


class SolarCatchRuntimeSensor(SolarCatchBaseSensor):
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES
    _attr_state_class = SensorStateClass.TOTAL_INCREASING

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "runtime_today", "Runtime today")

    @property
    def native_value(self):
        return round(self.coordinator.data.runtime_today_min, 1)


class SolarCatchRemainingRuntimeSensor(SolarCatchBaseSensor):
    _attr_native_unit_of_measurement = UnitOfTime.MINUTES

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "remaining_runtime", "Remaining runtime")

    @property
    def native_value(self):
        return round(self.coordinator.data.remaining_runtime_min, 1)


class SolarCatchLatestStartSensor(SolarCatchBaseSensor):
    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "latest_start", "Latest start time")

    @property
    def native_value(self):
        return self.coordinator.data.latest_start_time


class SolarCatchDecisionPowerSensor(SolarCatchBaseSensor):
    _attr_native_unit_of_measurement = UnitOfPower.WATT
    _attr_device_class = SensorDeviceClass.POWER
    _attr_state_class = SensorStateClass.MEASUREMENT

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "decision_power", "Decision power")

    @property
    def native_value(self):
        value = self.coordinator.data.decision_power_w
        return None if value is None else round(value, 0)


class SolarCatchAboveForSensor(SolarCatchBaseSensor):
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "above_for", "Above threshold for")

    @property
    def native_value(self):
        return self.coordinator.data.above_for_s


class SolarCatchBelowForSensor(SolarCatchBaseSensor):
    _attr_native_unit_of_measurement = "s"

    def __init__(self, coordinator, entry):
        super().__init__(coordinator, entry, "below_for", "Below threshold for")

    @property
    def native_value(self):
        return self.coordinator.data.below_for_s
