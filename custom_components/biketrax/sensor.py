"""Support for reading device status from BikeTrax."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import cast

from aiobiketrax import Device
from homeassistant.components.sensor import DOMAIN as SENSOR_DOMAIN
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    CONF_UNIT_SYSTEM_IMPERIAL,
    LENGTH_KILOMETERS,
    LENGTH_MILES,
    PERCENTAGE,
    SPEED_KILOMETERS_PER_HOUR,
    SPEED_MILES_PER_HOUR,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.typing import StateType
from homeassistant.util.distance import convert as distance_convert
from homeassistant.util.speed import convert as speed_convert
from homeassistant.util.unit_system import UnitSystem

from . import BikeTraxBaseEntity
from .const import DATA_DEVICE, DATA_SUBSCRIPTION, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator


@dataclass
class BikeTraxRequiredKeysMixin:
    """Mixin for required keys."""

    coordinator: str


@dataclass
class BikeTraxSensorEntityDescription(
    SensorEntityDescription, BikeTraxRequiredKeysMixin
):
    """Describes BikeTrax sensor entity."""

    imperial_conversion: Callable[[float], float] | float | None = None
    unit_metric: str | None = None
    unit_imperial: str | None = None


SENSOR_TYPES: tuple[BikeTraxSensorEntityDescription, ...] = (
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.BATTERY,
        key="battery_level",
        name="Battery level",
        unit_imperial=PERCENTAGE,
        unit_metric=PERCENTAGE,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        icon="mdi:speedometer",
        imperial_conversion=lambda val: distance_convert(
            val, LENGTH_MILES, LENGTH_KILOMETERS
        ),
        key="total_distance",
        name="Total distance",
        unit_imperial=LENGTH_MILES,
        unit_metric=LENGTH_KILOMETERS,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        icon="mdi:speedometer",
        imperial_conversion=lambda val: speed_convert(
            val, SPEED_MILES_PER_HOUR, SPEED_KILOMETERS_PER_HOUR
        ),
        key="speed",
        name="Current speed",
        unit_imperial=SPEED_MILES_PER_HOUR,
        unit_metric=SPEED_KILOMETERS_PER_HOUR,
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_SUBSCRIPTION,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:license",
        key="subscription_until",
        name="Subscription until",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        icon="mdi:state-machine",
        key="status",
        name="Device status",
    ),
    BikeTraxSensorEntityDescription(
        coordinator=DATA_DEVICE,
        device_class=SensorDeviceClass.TIMESTAMP,
        icon="mdi:clock",
        key="last_updated",
        name="Last updated",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax sensors from config entry."""

    coordinators: dict[str, BikeTraxDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        BikeTraxSensor(
            coordinators[description.coordinator],
            device,
            description,
            hass.config.units,
        )
        for description in SENSOR_TYPES
        for device in coordinators[description.coordinator].account.devices
    ]

    async_add_entities(entities)


class BikeTraxSensor(BikeTraxBaseEntity, SensorEntity):
    """Representation of a BikeTrax device sensor."""

    entity_description: BikeTraxSensorEntityDescription

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
        description: BikeTraxSensorEntityDescription,
        unit_system: UnitSystem,
    ) -> None:
        """Initialize BikeTrax device sensor."""
        super().__init__(coordinator, device)

        self.entity_id = (
            f"{SENSOR_DOMAIN}.{DOMAIN}_{description.key}_{device.id}"
        )
        self.entity_description = description

        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{device.id}-{description.key}"

        if unit_system.name == CONF_UNIT_SYSTEM_IMPERIAL:
            self._attr_native_unit_of_measurement = description.unit_imperial
        else:
            self._attr_native_unit_of_measurement = description.unit_metric

    @property
    def native_value(self) -> StateType:
        state = cast(
            StateType, getattr(self.device, self.entity_description.key)
        )

        if (
            self.entity_description.imperial_conversion
            and not self.hass.config.units.is_metric
        ):
            return self.entity_description.imperial_conversion(state)

        return state
