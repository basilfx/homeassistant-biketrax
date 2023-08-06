# Changelog

## v1.1.0
Released 06 August 2023

Highlights:
* Fixed: deprecated call to update entity state.
* Added: configured debug logging from within HASS.
* Updated: upgrade to aiobiketrax v1.1.0.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v1.0.0...v1.1.0).

## v1.0.0
Released 12 June 2023

Highlights:
* Fixed: compatibility with Home Assistant 2023.5 and later.
* Added: additional entities.
* Improved: use estimated battery level (similar to official app).
* Improved: log warning when subscription has ended.
* Updated: upgrade to aiobiketrax v1.0.0.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.5.0...v1.0.0).

## v0.5.0
Released 10 December 2022

Highlights:
* Added: sensor states for statistics support.
* Added: proper support for native units that can be configured via HASS.
* Fixed: upgrade to aiobiketrax v0.5.0 for solving WebSocket connection issues.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.4.0...v0.5.0).

## v0.4.0
Released 30 October 2022

Highlights:
* Updated: aiobiketrax v0.4.0 for exposing additional data.
* Improved: migrate alarm switch to an alarm control panel (breaking change).
* Fixed: read-only mode not persisted.
* Fixed: unit conversion for imperial units.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.3.0...v0.4.0).

## v0.3.0
Released 16 October 2022

Highlights:
* Updated: aiobiketrax v0.3.0 to address several API issues.
* Updated: reduce device data polling from 5 minutes to 15 minutes (does not affect WebSocket updates).
* Fixed: proper unit system check.
* Improved: login feedback in case of authentication, connection or device issues.
* Improved: increased logging.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.2.1...v0.3.0).

This release supersedes v0.2.2a1.

## v0.2.1
Released 27 August 2022

Highlights:
* Updated: aiobiketrax v0.2.1 to fix an issue with the websocket reconnect.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.2.0...v0.2.1).

## v0.2.0
Released 10 August 2022

Highlights:
* Updated: aiobiketrax v0.2.0 to address several API issues.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/v0.1.0...v0.2.0).

## v0.1.0
Released 8 July 2022

Highlights:
* Initial release.

The full list of commits can be found [here](https://github.com/basilfx/homeassistant-biketrax/compare/31fe9562d51c170a10d4f8956a37359a1d8879b3...v0.1.0).
