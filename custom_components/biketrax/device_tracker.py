"""Device tracker for BikeTrax devices."""

from __future__ import annotations

import logging
from typing import Literal

from aiobiketrax import Device
from homeassistant.components.device_tracker import SOURCE_TYPE_GPS
from homeassistant.components.device_tracker.config_entry import TrackerEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BikeTraxBaseEntity
from .const import ATTR_ALTITUDE, ATTR_COURSE, ATTR_SPEED, DATA_DEVICE, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax tracker from config entry."""
    coordinator: BikeTraxDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][DATA_DEVICE]
    entities: list[BikeTraxDeviceTracker] = []

    for device in coordinator.account.devices:
        entities.append(BikeTraxDeviceTracker(coordinator, device))

        if not device.is_tracking_enabled:
            _LOGGER.info(
                "Tracking is (currently) disabled for device %s (%s), defaulting to "
                "unknown",
                device.id,
                device.name,
            )

    async_add_entities(entities)


class BikeTraxDeviceTracker(BikeTraxBaseEntity, TrackerEntity):
    """Representation of a BikeTrax device tracker."""

    _attr_force_update = False
    _attr_icon = "mdi:bike"

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator, device)

        self._attr_unique_id = device.id
        self._attr_name = device.name

    @property
    def battery_level(self) -> int | None:
        """Return the battery level of the device."""
        return self.device.battery_level

    @property
    def latitude(self) -> float | None:
        """Return latitude value of the device."""
        return self.device.latitude if self.device.is_tracking_enabled else None

    @property
    def longitude(self) -> float | None:
        """Return longitude value of the device."""
        return self.device.longitude if self.device.is_tracking_enabled else None

    @property
    def location_accuracy(self) -> int:
        return self.device.accuracy if self.device.is_tracking_enabled else 0

    @property
    def source_type(self) -> Literal["gps"]:
        """Return the source type, e.g. gps or router, of the device."""
        return SOURCE_TYPE_GPS

    @property
    def extra_state_attributes(self):
        """Return device specific attributes."""
        attrs = {}

        if self.device.is_tracking_enabled:
            attrs[ATTR_ALTITUDE] = self.device.altitude
            attrs[ATTR_COURSE] = self.device.altitude
            attrs[ATTR_SPEED] = self.device.speed

        return attrs
