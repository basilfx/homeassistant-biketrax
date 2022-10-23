"""Coordinator for BikeTrax."""
from __future__ import annotations

import logging
from datetime import timedelta

from aiobiketrax import Account, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .const import CONF_READ_ONLY, DOMAIN

SCAN_INTERVAL_DEVICE = timedelta(minutes=15)
SCAN_INTERVAL_TRIPS = timedelta(hours=1)
SCAN_INTERVAL_SUBSCRIPTION = timedelta(hours=12)

_LOGGER = logging.getLogger(__name__)


class BikeTraxDataUpdateCoordinator(DataUpdateCoordinator):
    account: Account
    read_only: bool

    def __init__(
        self, hass: HomeAssistant, account: Account, entry: ConfigEntry, **kwargs
    ) -> None:
        """Initialize account-wide BikeTrax data update coordinator."""
        self.account = account
        self.read_only = entry.options.get(CONF_READ_ONLY, False)

        super().__init__(hass, _LOGGER, **kwargs)


class DeviceDataUpdateCoordinator(BikeTraxDataUpdateCoordinator):
    """Class to manage fetching BikeTrax data."""

    def __init__(
        self, hass: HomeAssistant, account: Account, entry: ConfigEntry
    ) -> None:
        """Initialize account-wide BikeTrax device update coordinator."""
        super().__init__(
            hass,
            account,
            entry,
            name=f"{DOMAIN}-{entry.data['username']}-device",
            update_interval=SCAN_INTERVAL_DEVICE,
        )

    async def _async_update_data(self) -> None:
        """Fetch data from BikeTrax."""
        _LOGGER.debug("Device data coordinator updating.")

        try:
            last_updated = {
                device.id: device.last_updated for device in self.account.devices
            }

            await self.account.update_devices()

            for device in self.account.devices:
                if device.last_updated == last_updated.get(device.id):
                    _LOGGER.debug(
                        "Not updating position for device %s because it has not changed.",
                        device.id,
                    )
                    continue

                await device.update_position()
        except exceptions.BikeTraxError as err:
            raise UpdateFailed(
                f"A BikeTrax error occurred while updating the devices: {err}"
            ) from err

    def start_background_task(self):
        """Start the websocket task."""

        def _on_update():
            _LOGGER.debug("Device data update received.")
            self.async_set_updated_data(None)

        self.account.start(on_update=_on_update)

    async def stop_background_task(self):
        """Stop the websocket task"""
        await self.account.stop()


class TripDataUpdateCoordinator(BikeTraxDataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, account: Account, entry: ConfigEntry
    ) -> None:
        """Initialize account-wide BikeTrax trip update coordinator."""
        super().__init__(
            hass,
            account,
            entry,
            name=f"{DOMAIN}-{entry.data['username']}-trip",
            update_interval=SCAN_INTERVAL_TRIPS,
        )

    async def _async_update_data(self) -> None:
        """Fetch data from BikeTrax."""
        _LOGGER.debug("Trip data coordinator updating.")

        try:
            for device in self.account.devices:
                await device.update_trips()
        except exceptions.BikeTraxError as err:
            raise UpdateFailed(
                f"A BikeTrax error occurred while updating the trips: {err}"
            ) from err


class SubscriptionDataUpdateCoordinator(BikeTraxDataUpdateCoordinator):
    def __init__(
        self, hass: HomeAssistant, account: Account, entry: ConfigEntry
    ) -> None:
        """Initialize account-wide BikeTrax subscription update coordinator."""
        super().__init__(
            hass,
            account,
            entry,
            name=f"{DOMAIN}-{entry.data['username']}-subscription",
            update_interval=SCAN_INTERVAL_SUBSCRIPTION,
        )

    async def _async_update_data(self) -> None:
        """Fetch data from BikeTrax."""
        _LOGGER.debug("Subscription data coordinator updating.")

        try:
            for device in self.account.devices:
                await device.update_subscription()
        except exceptions.BikeTraxError as err:
            raise UpdateFailed(
                f"A BikeTrax error occurred while updating the subscription data: {err}"
            ) from err
