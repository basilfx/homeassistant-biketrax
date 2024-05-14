"""The BikeTrax integration."""

from __future__ import annotations

from asyncio import Event

from aiobiketrax import Account, Device
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_PASSWORD,
    CONF_USERNAME,
    EVENT_HOMEASSISTANT_STOP,
    Platform,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers import aiohttp_client
from homeassistant.helpers.entity import DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DATA_DEVICE, DATA_SUBSCRIPTION, DATA_TRIP, DOMAIN
from .coordinator import (
    BikeTraxDataUpdateCoordinator,
    DeviceDataUpdateCoordinator,
    SubscriptionDataUpdateCoordinator,
    TripDataUpdateCoordinator,
)

PLATFORMS = [
    Platform.ALARM_CONTROL_PANEL,
    Platform.BINARY_SENSOR,
    Platform.DEVICE_TRACKER,
    Platform.SENSOR,
    Platform.SWITCH,
]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up BikeTrax from a config entry."""

    # Setup an BikeTrax account instance.
    account = Account(
        entry.data[CONF_USERNAME],
        entry.data[CONF_PASSWORD],
        aiohttp_client.async_get_clientsession(hass),
    )

    # Set up data coordinators per account/config entry. There are three
    # coordinators: one for the (push-capable) devices, one for the trips and
    # one for the subscription information. The last two will be updates less
    # frequently.
    device_coordinator = DeviceDataUpdateCoordinator(
        hass,
        account,
        entry,
    )
    trip_coordinator = TripDataUpdateCoordinator(
        hass,
        account,
        entry,
    )
    subscription_coordinator = SubscriptionDataUpdateCoordinator(
        hass,
        account,
        entry,
    )

    await device_coordinator.async_config_entry_first_refresh()
    await trip_coordinator.async_config_entry_first_refresh()
    await subscription_coordinator.async_config_entry_first_refresh()

    hass.data.setdefault(DOMAIN, {})
    hass.data[DOMAIN][entry.entry_id] = {
        DATA_DEVICE: device_coordinator,
        DATA_TRIP: trip_coordinator,
        DATA_SUBSCRIPTION: subscription_coordinator,
    }

    # Start the websocket background task.
    device_coordinator.start_background_task()

    async def _stop(event: Event) -> None:
        await device_coordinator.stop_background_task()

    entry.async_on_unload(hass.bus.async_listen_once(EVENT_HOMEASSISTANT_STOP, _stop))

    # Set up all platforms.
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)

    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    if unload_ok := await hass.config_entries.async_unload_platforms(entry, PLATFORMS):
        coordinators = hass.data[DOMAIN].pop(entry.entry_id)

        # Stop the websocket background task.
        await coordinators[DATA_DEVICE].stop_background_task()

    return unload_ok


class BikeTraxBaseEntity(CoordinatorEntity[BikeTraxDataUpdateCoordinator]):
    """Common base for BikeTrax entities."""

    coordinator: BikeTraxDataUpdateCoordinator

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize entity."""
        super().__init__(coordinator)

        self.device = device

        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, str(self.device.id))},
            model=device.name,
            name=device.name,
        )

    async def async_added_to_hass(self) -> None:
        """When entity is added to hass."""
        await super().async_added_to_hass()
        self._handle_coordinator_update()
