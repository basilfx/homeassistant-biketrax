"""Device alarm control panel for BikeTrax devices."""
from __future__ import annotations

from aiobiketrax import Device
from homeassistant.components.alarm_control_panel import DOMAIN as ALARM_DOMAIN
from homeassistant.components.alarm_control_panel import AlarmControlPanelEntity
from homeassistant.components.alarm_control_panel.const import (
    AlarmControlPanelEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import (
    STATE_ALARM_ARMED_AWAY,
    STATE_ALARM_ARMED_HOME,
    STATE_ALARM_DISARMED,
    STATE_ALARM_TRIGGERED,
)
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback

from . import BikeTraxBaseEntity
from .const import DATA_DEVICE, DOMAIN
from .coordinator import BikeTraxDataUpdateCoordinator


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up the BikeTrax alarm control panel from a config entry."""
    coordinator: BikeTraxDataUpdateCoordinator = hass.data[DOMAIN][
        config_entry.entry_id
    ][DATA_DEVICE]

    entities: list[BikeTraxAlarmController] = [
        BikeTraxAlarmController(coordinator, device)
        for device in coordinator.account.devices
    ]

    async_add_entities(entities)


class BikeTraxAlarmController(BikeTraxBaseEntity, AlarmControlPanelEntity):
    """Representation of a BikeTrax Alarm."""

    _attr_code_arm_required = False

    # Both 'arm home' and 'arm away' are added, because the UI does not reflect
    # the supported features correctly.
    # See https://github.com/nielsfaber/alarmo/issues/384 for some details.
    _attr_supported_features = (
        AlarmControlPanelEntityFeature.ARM_HOME
        | AlarmControlPanelEntityFeature.ARM_AWAY
        | AlarmControlPanelEntityFeature.TRIGGER
    )

    def __init__(
        self,
        coordinator: BikeTraxDataUpdateCoordinator,
        device: Device,
    ) -> None:
        """Initialize the tracker."""
        super().__init__(coordinator, device)

        self.entity_id = f"{ALARM_DOMAIN}.{DOMAIN}_alarm_{device.id}"
        self._attr_name = f"{device.name} Alarm"
        self._attr_unique_id = f"{device.id}-alarm"
        self._is_home = False

    @property
    def state(self):
        """Return the state of the device."""
        return (
            STATE_ALARM_TRIGGERED
            if self.device.is_alarm_triggered or self.device.is_stolen
            else STATE_ALARM_ARMED_HOME
            if self.device.is_guarded and self._is_home
            else STATE_ALARM_ARMED_AWAY
            if self.device.is_guarded
            else STATE_ALARM_DISARMED
        )

    async def async_alarm_disarm(self, code: str | None = None) -> None:
        """Send disarm command."""
        if not self.coordinator.read_only:
            self._is_home = False
            await self.device.set_guarded(False)

    async def async_alarm_arm_home(self, code: str | None = None) -> None:
        """Send arm away command."""
        if not self.coordinator.read_only:
            self._is_home = True
            await self.device.set_guarded(True)

    async def async_alarm_arm_away(self, code: str | None = None) -> None:
        """Send arm away command."""
        if not self.coordinator.read_only:
            self._is_home = False
            await self.device.set_guarded(True)

    async def async_alarm_trigger(self, code: str | None = None) -> None:
        """Send alarm trigger command."""
        if not self.coordinator.read_only:
            await self.device.set_stolen(True)
