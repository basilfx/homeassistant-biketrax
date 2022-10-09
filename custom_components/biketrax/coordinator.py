"""Coordinator for BikeTrax."""
from __future__ import annotations

import logging
from datetime import timedelta

from aiobiketrax import Account, exceptions
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed
from httpx import HTTPError, TimeoutException

from .const import CONF_READ_ONLY, DOMAIN

SCAN_INTERVAL_DEVICE = timedelta(seconds=300)
SCAN_INTERVAL_TRIPS = timedelta(hours=1)
SCAN_INTERVAL_SUBSCRIPTION = timedelta(hours=12)

_LOGGER = logging.getLogger(__name__)


class BikeTraxDataUpdateCoordinator(DataUpdateCoordinator):
    account: Account


class DeviceDataUpdateCoordinator(BikeTraxDataUpdateCoordinator):
    """Class to manage fetching BikeTrax data."""

    def __init__(
        self, hass: HomeAssistant, account: Account, entry: ConfigEntry
    ) -> None:
        """Initialize account-wide BikeTrax data update coordinator."""
        self.account = account
        self.read_only = entry.options[CONF_READ_ONLY]

        super().__init__(
            hass,
            _LOGGER,
            name=f"{DOMAIN}-{entry.data['username']}-device",
            update_interval=SCAN_INTERVAL_DEVICE,
        )

    async def _async_update_data(self) -> None:
        """Fetch data from BikeTrax."""
        _LOGGER.debug("Device data coordinator updating.")

        try:
            await self.account.update_devices()

            for device in self.account.devices:
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
        """Initialize account-wide BikeTrax data update coordinator."""
        self.account = account
        self.read_only = entry.options[CONF_READ_ONLY]

        super().__init__(
            hass,
            _LOGGER,
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
        """Initialize account-wide BikeTrax data update coordinator."""
        self.account = account
        self.read_only = entry.options[CONF_READ_ONLY]

        super().__init__(
            hass,
            _LOGGER,
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
