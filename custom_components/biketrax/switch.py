"""Switch entities for BikeTrax devices."""
from __future__ import annotations

from collections.abc import Callable
from dataclasses import dataclass
from typing import Any

from aiobiketrax import Device
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN
from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.util.unit_system import UnitSystem

from . import BikeTraxBaseEntity
from .const import DATA_DEVICE, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator


@dataclass
class BikeTraxRequiredKeysMixin:
    """Mixin for required keys."""

    coordinator: str
    get_fn: Callable[[Device], bool]
    set_fn: Callable[[Device], bool]


@dataclass
class BikeTraxBinarySwitchEntityDescription(
    SwitchEntityDescription, BikeTraxRequiredKeysMixin
):
    """Describes BikeTrax binary_sensor entity."""

    attr_fn: Callable[[Device, UnitSystem], dict[str, Any]] | None = None


SWITCH_TYPES: tuple[BikeTraxBinarySwitchEntityDescription, ...] = (
    BikeTraxBinarySwitchEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_stolen",
        name="Stolen",
        icon="mdi:account-lock",
        get_fn=lambda d: d.is_stolen,
        set_fn=lambda d, v: d.set_stolen(v),
    ),
    BikeTraxBinarySwitchEntityDescription(
        coordinator=DATA_DEVICE,
        key="is_tracking_enabled",
        name="Tracking enabled",
        icon="mdi:radar",
        get_fn=lambda d: d.is_tracking_enabled,
        set_fn=lambda d, v: d.set_tracking_enabled(v),
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax switches from config entry."""

    coordinators: dict[str, BikeTraxDataUpdateCoordinator] = hass.data[DOMAIN][
        config_entry.entry_id
    ]

    entities = [
        BikeTraxBinarySensor(coordinators[description.coordinator], device, description)
        for description in SWITCH_TYPES
        for device in coordinators[description.coordinator].account.devices
    ]

    async_add_entities(entities)


class BikeTraxBinarySensor(BikeTraxBaseEntity, SwitchEntity):
    """Representation of a BikeTrax device switch."""

    entity_description: BikeTraxBinarySwitchEntityDescription

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
        description: BikeTraxBinarySwitchEntityDescription,
    ) -> None:
        """Initialize switch."""
        super().__init__(coordinator, device)

        self.entity_description = description
        self.entity_id = f"{SWITCH_DOMAIN}.{DOMAIN}_{description.key}_{device.id}"

        self._attr_name = f"{device.name} {description.name}"
        self._attr_unique_id = f"{device.id}-{description.key}"

    @property
    def is_on(self) -> bool:
        """Return the status of the switch."""
        return self.entity_description.get_fn(self.device)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn the entity on."""
        if not self.coordinator.read_only:
            await self.entity_description.set_fn(self.device, True)
            await self.async_update_ha_state()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn the entity off."""
        if not self.coordinator.read_only:
            await self.entity_description.set_fn(self.device, False)
            await self.async_update_ha_state()
