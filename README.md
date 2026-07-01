# Solar Catch

Solar Catch is a small Home Assistant custom integration for controlling a fixed-load appliance from excess solar power.

This first version is deliberately basic. It is intended as the bones for a forecast-aware hot-water controller.

## What v0.1 does

- Creates a Solar Catch device in Home Assistant.
- Lets you select:
  - an excess-power sensor
  - an appliance switch/relay
- Creates configurable entities for:
  - appliance power draw
  - start power threshold
  - above-threshold time
  - below-threshold time
  - minimum daily runtime
  - start time
  - end time
  - enabled switch
- Turns the appliance on when decision power has been above threshold for the configured time.
- Turns the appliance off when decision power has been below threshold for the configured time.
- Forces the appliance on if it is not going to reach the minimum daily runtime by the end time.

## Power sensor convention

The selected power sensor should use:

- positive = excess/export available
- negative = import/shortfall

Units of W, kW, and MW are automatically converted to watts.

## Important control detail

When the appliance is ON, Solar Catch adds the configured appliance power draw back onto the live power sensor value before deciding whether the threshold is still met.

Example:

- export before hot water: `1400 W`
- hot water draw: `3600 W`
- power sensor after hot water starts: `-2200 W`
- Solar Catch decision power: `-2200 + 3600 = 1400 W`

This prevents the relay from immediately turning off just because the load it switched on consumed the available excess.

## Installation through HACS as a custom repository

1. Create a GitHub repository with this folder structure.
2. In HACS, open the three-dot menu.
3. Choose **Custom repositories**.
4. Add the repository URL.
5. Select category **Integration**.
6. Install **Solar Catch**.
7. Restart Home Assistant.
8. Add the integration from **Settings → Devices & services → Add integration → Solar Catch**.

## Manual install

Copy this folder:

```text
custom_components/solar_catch
```

into your Home Assistant config directory:

```text
/config/custom_components/solar_catch
```

Restart Home Assistant, then add the integration from the UI.

## Current limitations

- Runtime tracking resets if Home Assistant restarts during the day.
- Only one Solar Catch instance is allowed in this first skeleton.
- No forecast planning yet.
- No separate stop threshold yet.
- No manual boost yet.

## Planned next steps

- Persist runtime across restarts.
- Add separate start and stop thresholds.
- Add forecast-aware waiting.
- Add Solcast forecast input.
- Add manual boost button.
- Add safety/fault sensor handling.
