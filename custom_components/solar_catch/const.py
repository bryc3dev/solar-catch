"""Constants for Solar Catch."""

DOMAIN = "solar_catch"
PLATFORMS = ["sensor", "switch", "number", "time"]

CONF_POWER_ENTITY = "power_entity"
CONF_APPLIANCE_SWITCH = "appliance_switch"
CONF_APPLIANCE_POWER_ENTITY = "appliance_power_entity"
CONF_APPLIANCE_POWER_W = "appliance_power_w"
CONF_START_THRESHOLD_W = "start_threshold_w"
CONF_ABOVE_THRESHOLD_SECONDS = "above_threshold_seconds"
CONF_BELOW_THRESHOLD_SECONDS = "below_threshold_seconds"
CONF_MIN_RUNTIME_MINUTES = "min_runtime_minutes"
CONF_START_TIME = "start_time"
CONF_END_TIME = "end_time"
CONF_ENABLED = "enabled"

DEFAULTS = {
    CONF_APPLIANCE_POWER_ENTITY: "",
    CONF_APPLIANCE_POWER_W: 3600.0,
    CONF_START_THRESHOLD_W: 1200.0,
    CONF_ABOVE_THRESHOLD_SECONDS: 120,
    CONF_BELOW_THRESHOLD_SECONDS: 120,
    CONF_MIN_RUNTIME_MINUTES: 120,
    CONF_START_TIME: "09:00:00",
    CONF_END_TIME: "17:00:00",
    CONF_ENABLED: True,
}
