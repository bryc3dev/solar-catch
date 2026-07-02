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
    CONF_END_TIME,
    CONF_MIN_RUNTIME_MINUTES,
    CONF_POWER_ENTITY,
    CONF_START_THRESHOLD_W,
    CONF_START_TIME,
    DEFAULTS,
    DOMAIN,
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
    }
    return vol.Schema(schema)


class SolarCatchConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Solar Catch."""

    VERSION = 1

    async def async_step_user(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            await self.async_set_unique_id("solar_catch")
            self._abort_if_unique_id_configured()
            return self.async_create_entry(title="Solar Catch", data=user_input)

        return self.async_show_form(step_id="user", data_schema=_schema())

    @staticmethod
    def async_get_options_flow(config_entry: config_entries.ConfigEntry):
        return SolarCatchOptionsFlow()


class SolarCatchOptionsFlow(config_entries.OptionsFlow):
    """Options flow for Solar Catch."""

    async def async_step_init(self, user_input: dict[str, Any] | None = None):
        if user_input is not None:
            return self.async_create_entry(title="", data=user_input)
        defaults = {**self.config_entry.data, **self.config_entry.options}
        return self.async_show_form(step_id="init", data_schema=_schema(defaults))
