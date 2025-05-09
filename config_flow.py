"""Config flow for the AVM FRITZ!Box SMS integration."""

from __future__ import annotations

import logging
from typing import Any

import aiohttp
from fritzsms.fritzbox import FritzBox
import phonenumbers
import voluptuous as vol

from homeassistant.config_entries import (
    ConfigEntry,
    ConfigFlow,
    ConfigFlowResult,
    ConfigSubentryFlow,
    SubentryFlowResult,
)
from homeassistant.const import (
    CONF_HOST,
    CONF_NAME,
    CONF_PASSWORD,
    CONF_TARGET,
    CONF_TOKEN,
    CONF_USERNAME,
)
from homeassistant.core import callback
from homeassistant.helpers.aiohttp_client import async_get_clientsession

from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)

STEP_USER_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_HOST): str,
        vol.Required(CONF_USERNAME): str,
        vol.Required(CONF_PASSWORD): str,
        vol.Required(CONF_TOKEN): str,
    }
)

STEP_TARGET_DATA_SCHEMA = vol.Schema(
    {
        vol.Required(CONF_NAME): str,
        vol.Required(CONF_TARGET): str,
    }
)


class FritzBoxConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for AVM FRITZ!Box SMS."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}
        code = ""
        if user_input is not None:
            user_input[CONF_TOKEN] = user_input[CONF_TOKEN].replace(" ", "")
            session = async_get_clientsession(self.hass)
            box = FritzBox(user_input[CONF_HOST], session)
            box.set_otp(user_input[CONF_TOKEN])
            code = box.get_otp()
            try:
                await box.login(user_input[CONF_USERNAME], user_input[CONF_PASSWORD])
                otp_configured = await box.is_otp_configured()
                await box.logout()
                if not otp_configured:
                    errors[CONF_TOKEN] = "invalid_auth"
                else:
                    return self.async_create_entry(
                        title=user_input[CONF_HOST], data=user_input
                    )
            except aiohttp.client_exceptions.ClientConnectorError:
                errors[CONF_HOST] = "cannot_connect"
            except RuntimeError:
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

            data_schema = self.add_suggested_values_to_schema(
                STEP_USER_DATA_SCHEMA, user_input
            )
        else:
            data_schema = STEP_USER_DATA_SCHEMA

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
            description_placeholders={"code": code},
        )

    @classmethod
    @callback
    def async_get_supported_subentry_types(
        cls, config_entry: ConfigEntry
    ) -> dict[str, type[ConfigSubentryFlow]]:
        """Return subentries supported by this integration."""
        return {"target": TargetSubentryFlowHandler}


class TargetSubentryFlowHandler(ConfigSubentryFlow):
    """Handle subentry flow for adding and modifying a location."""

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> SubentryFlowResult:
        """User flow to add a new target."""
        errors: dict[str, str] = {}
        if user_input is not None:
            name = user_input[CONF_NAME]
            target = user_input[CONF_TARGET]
            try:
                phonenumbers.parse(target)
            except phonenumbers.NumberParseException:
                errors[CONF_TARGET] = "impossible_number"
            else:
                return self.async_create_entry(title=name, data=user_input)

        return self.async_show_form(
            step_id="user", data_schema=STEP_TARGET_DATA_SCHEMA, errors=errors
        )
