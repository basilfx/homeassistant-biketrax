"""Config flow for PowUnity BikeTrax integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol
from aiobiketrax import Account
from homeassistant import config_entries
from homeassistant.core import HomeAssistant, callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers import aiohttp_client

from .const import CONF_READ_ONLY, DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required("username"): str,
        vol.Required("password"): str,
    }
)


async def validate_input(hass: HomeAssistant, data: dict[str, Any]) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from STEP_USER_DATA_SCHEMA with values provided by the user.
    """

    account = Account(
        data["username"],
        data["password"],
        aiohttp_client.async_get_clientsession(hass),
    )

    try:
        await account.update_devices()
    except:
        raise InvalidAuth

    return {"title": f"BikeTrax {data['username']}"}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for PowUnity BikeTrax."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is None:
            return self.async_show_form(
                step_id="user", data_schema=STEP_USER_DATA_SCHEMA
            )

        errors = {}

        try:
            info = await validate_input(self.hass, user_input)
        except CannotConnect:
            errors["base"] = "cannot_connect"
        except InvalidAuth:
            errors["base"] = "invalid_auth"
        except Exception:  # pylint: disable=broad-except
            _LOGGER.exception("Unexpected exception")
            errors["base"] = "unknown"
        else:
            return self.async_create_entry(title=info["title"], data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_USER_DATA_SCHEMA, errors=errors
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> BikeTraxOptionsFlow:
        """Return a BikeTrax option flow."""
        return BikeTraxOptionsFlow(config_entry)


class BikeTraxOptionsFlow(config_entries.OptionsFlow):
    """Handle a option flow for BikeTrax."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize BikeTrax option flow."""
        self.config_entry = config_entry
        self.options = dict(config_entry.options)

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        return await self.async_step_account_options()

    async def async_step_account_options(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        if user_input is not None:
            # Manually update & reload the config entry after options change.
            changed = self.hass.config_entries.async_update_entry(
                self.config_entry,
                options=user_input,
            )
            if changed:
                await self.hass.config_entries.async_reload(self.config_entry.entry_id)
            return self.async_create_entry(title="", data=user_input)
        return self.async_show_form(
            step_id="account_options",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_READ_ONLY,
                        default=self.config_entry.options.get(CONF_READ_ONLY, False),
                    ): bool,
                }
            ),
        )


class CannotConnect(HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidAuth(HomeAssistantError):
    """Error to indicate there is invalid auth."""
