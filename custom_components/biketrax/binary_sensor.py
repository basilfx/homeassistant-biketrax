"""Binary sensor entities for BikeTrax devices."""

from __future__ import annotations

from dataclasses import dataclass
from typing import cast

from aiobiketrax import Device
from homeassistant.components.binary_sensor import DOMAIN as BINARY_SENSOR_DOMAIN
from homeassistant.components.binary_sensor import (
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BikeTraxBaseEntity
from .const import DATA_DEVICE, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator


@dataclass
class BikeTraxRequiredKeysMixin:
    """Mixin for required keys."""

    coordinator: str


@dataclass
class BikeTraxBinarySensorEntityDescription(
    BinarySensorEntityDescription, BikeTraxRequiredKeysMixin
):
    """Describes BikeTrax binary_sensor entity."""


SENSOR_TYPES: tuple[BikeTraxBinarySensorEntityDescription, ...] = (
    BikeTraxBinarySensorEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_guarded",
        name="Alarm enabled",
        icon="mdi:shield-lock",
    ),
    BikeTraxBinarySensorEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_alarm_triggered",
        name="Alarm triggered",
        icon="mdi:alarm-light",
    ),
    BikeTraxBinarySensorEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_auto_guarded",
        name="Auto alarm enabled",
        icon="mdi:account-lock",
    ),
    BikeTraxBinarySensorEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_charging",
        name="Charging",
        icon="mdi:battery-charging",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax binary sensors from config entry."""

    coordinators: dict[str, BikeTraxDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        BikeTraxBinarySensor(coordinators[description.coordinator], device, description)
        for description in SENSOR_TYPES
        for device in coordinators[description.coordinator].account.devices
    ]

    async_add_entities(entities)


class BikeTraxBinarySensor(BikeTraxBaseEntity, BinarySensorEntity):
    """Representation of a BikeTrax device binary sensor."""

    entity_description: BikeTraxBinarySensorEntityDescription

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
        description: BikeTraxBinarySensorEntityDescription,
    ) -> None:
        """Initialize sensor."""
        super().__init__(coordinator, device)

        self.entity_description = description
        self.entity_id = (
            f"{BINARY_SENSOR_DOMAIN}.{DOMAIN}_{description.key}_{device.id}"
        )

        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{device.id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return True if the binary sensor is on."""
        return cast(bool, getattr(self.device, self.entity_description.key))
