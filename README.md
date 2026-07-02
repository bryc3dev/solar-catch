# Solar Catch

Solar Catch is a simple Home Assistant custom integration for catching spare solar/export power and running a controlled appliance, such as an electric hot-water relay.

This is an early build intended to get the basic bones working.

## Current logic

Solar Catch expects the selected excess power sensor to read:

- **positive** when exporting / excess power is available
- **negative** when importing / shortfall

If your meter is the opposite sign, create an inverted template sensor and use that in Solar Catch.

Basic control:

- If decision power is above the start threshold for the configured above-threshold time, turn the appliance on.
- Once the appliance is on, if decision power is below the start threshold for the configured below-threshold time, turn it off.
- Below-threshold timing only starts while the appliance is on.
- If the minimum daily runtime will not be reached by the end time, force the appliance on.
- Solar Catch will not start the appliance before the start time.

When the appliance is already on, Solar Catch adds the appliance draw back onto the raw excess/import sensor to estimate the excess that existed before the appliance turned on.

If an appliance power sensor is mapped, Solar Catch uses that live value. If not, it uses the configured fallback draw.

## Example

Hot water relay:

- Raw excess before start: `1400 W`
- Appliance draw: `3600 W`
- Raw excess after start: about `-2200 W`
- Decision power while running: `-2200 + 3600 = 1400 W`

This avoids immediately switching back off just because the appliance consumed the export.

## Settings

During setup/options, choose:

- Excess power sensor
- Appliance switch
- Optional appliance power sensor
- Fallback appliance draw
- Start power threshold
- Above threshold time
- Below threshold time
- Minimum daily runtime
- Start time
- End time

## Suggested starting settings for hot water

- Fallback appliance draw: `3600 W`
- Start threshold: `1200 W`
- Above time: `120 s`
- Below time: `180 s`
- Minimum runtime: `120 min`
- Start: `09:00`
- End: `17:00`

## Entities created

- `switch.solar_catch_enabled`
- `number.solar_catch_fallback_draw`
- `number.solar_catch_start_threshold`
- `number.solar_catch_above_time`
- `number.solar_catch_below_time`
- `number.solar_catch_min_runtime`
- `time.solar_catch_start`
- `time.solar_catch_end`
- `sensor.solar_catch_status`
- `sensor.solar_catch_mode`
- `sensor.solar_catch_runtime_today`
- `sensor.solar_catch_remaining_runtime`
- `sensor.solar_catch_raw_excess_power`
- `sensor.solar_catch_decision_power`
- `sensor.solar_catch_appliance_draw`
- `sensor.solar_catch_above_threshold_for`
- `sensor.solar_catch_below_threshold_for`
- `sensor.solar_catch_latest_start_time`

Installation through HACS as a custom repository
1. Create a GitHub repository with this folder structure.
2. In HACS, open the three-dot menu.
3. Choose Custom repositories.
4. Add the repository URL.
5. Select category Integration.
6. Install Solar Catch.
7. Restart Home Assistant.
8. Add the integration from Settings → Devices & services → Add integration → Solar Catch.


## Notes

This is not a replacement for the hot-water cylinder thermostat, over-temperature protection, or a correctly rated contactor/relay.

Version `0.1.2` changes:

- Added optional appliance power sensor mapping.
- Uses live appliance draw for decision power when available.
- Runtime counts active draw if appliance power sensor is mapped.
- Below-threshold timer only runs while the appliance is on.
- Shortened control entity names to improve the default device controls card.
- Added setup/options descriptions explaining that the excess sensor must be positive on export.
