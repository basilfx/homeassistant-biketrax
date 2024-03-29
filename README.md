# Home Assistant BikeTrax
Custom component for the PowUnity BikeTrax integration for Home Assistant.

## Introduction
This custom components adds support for the
[PowUnity BikeTrax](https://powunity.com/) GPS tracker.

[<img src="docs/images/screenshot.png" alt="Overview screenshot.">](docs/images/screenshot.png)

## Features
* Multi-device support
* Live updates
* Ability to control alarm, tracking and stolen-state.

## Installation

### HACS
This is the preferred method of installation.

- Search for this integration and install it.
- Restart Home Assistant.

### Manual
- Download the contents of this repository.
- Copy the `custom_components` folder to your configuration folder. If you
  already have one, then merge its contents.
- Restart Home Assistant.

## Configuration
Add a new integration using the web interface, and follow the configuration steps.

You can also click the button below to get started.

[![Open your Home Assistant instance and start setting up a new integration.](https://my.home-assistant.io/badges/config_flow_start.svg)](https://my.home-assistant.io/redirect/config_flow_start/?domain=biketrax)

### Debug logging
Additional logging can be enabled from the Home Assistant integrations page.
Simply enable debug logging to see additional logging of this integration.

If you ever need to share your logs, be sure to remove sensitive data such as
email addresses, identifiers and serial numbers.

## Known issues

### Read-only mode
When read-only mode is enabled, the switches and alarm do not reflect this mode
properly. For example, if you try to toggle device tracking, it will eventually
restore to its previous state.

I do not really know how to handle this properly, without changing the entity
type.

### Alarm control panel
The current alarm control panel component in Home Assistant does not reflect
the supported features properly. In addition, 'arm home' and 'arm away' have an
odd meaning for a device alarm. Because of this 'bug', both modes for arming
the alarm are implemented.

See https://github.com/nielsfaber/alarmo/issues/384 for more information.

### Stolen mode
When this integration was first introduced, there was a toggle in the PowUnity
app to mark your bike as stolen. In the background, this toggled an attribute.

This functionality seems to be removed from the PowUnity app, or but behind a
an additional subscription. However, the entity is still provided by this
integration, because it is unknonw if it is a removed feature, or only
available with an additional subscription.

## References
This custom component builds on top of
[aiobiketrax](https://github.com/basilfx/aiobiketrax).

### Development version
If you ever need to use a newer version of `aiobiketrax` with this integration,
you can edit `custom_components/biketrax/manifest.json` and adapt the
requirements section to point to a newer version:

```json
"requirements": [
  "aiobiketrax @ git+https://github.com/basilfx/aiobiketrax.git@master"
]
```

Shut-down Home Assistant, remove the old dependency and then restart
Home Assistant. The latest version will be fetched from GitHub directly.

Removing a dependency depends on your installation. In a supervised
installation, you can try the following:

```bash
docker exec -it homeassistant bash
pip uninstall aiobiketrax
```

## Contributing
See the [`CONTRIBUTING.md`](CONTRIBUTING.md) file.

## License
See the [`LICENSE.md`](LICENSE.md) file (MIT license).

## Disclaimer
Use this library at your own risk. I cannot be held responsible for any
damages.

This page and its content is not affiliated with PowUnity.
