"""Config flow for Hello World integration."""
from __future__ import annotations
import json
import logging
from typing import Any

import voluptuous as vol
from voluptuous import Schema, Required

from homeassistant import config_entries, exceptions
from homeassistant.core import HomeAssistant

from .const import DOMAIN  # pylint:disable=unused-import
from .token import Token

_LOGGER = logging.getLogger(__name__)

# This is the schema that used to display the UI to the user. This simple
# schema has a single required name field, but it could include a number of fields
# such as username, password etc. See other components in the HA core code for
# further examples.
# Note the input displayed to the user will be translated. See the
# translations/<lang>.json file and strings.json. See here for further information:
# https://developers.home-assistant.io/docs/config_entries_config_flow_handler/#translations
# At the time of writing I found the translations created by the scaffold didn't
# quite work as documented and always gave me the "Lokalise key references" string
# (in square brackets), rather than the actual translated value. I did not attempt to
# figure this out or look further into it.
DATA_SCHEMA = Schema({
    Required("name"): str,
    Required("json_config"): str,
    Required("api_ip_address"): str
})


async def validate_input(hass: HomeAssistant, data: dict) -> dict[str, Any]:
    """Validate the user input allows us to connect.

    Data has the keys from DATA_SCHEMA with values provided by the user.
    """
    # Validate the data can be used to set up a connection.

    # This is a simple example to show an error in the UI for a short namename
    # The exceptions are defined at the end of this file, and are used in the
    # `async_step_user` method below.
    if len(data["name"]) < 3:
        raise InvalidName

    if len(data["api_ip_address"].split(".")) == 4:
        for mask in data["api_ip_address"].split("."):
            if not mask.isnumeric() or (mask.isnumeric() and (int(mask) < 0 or int(mask) > 255)):
                raise InvalidIPAddress
    else:
        raise InvalidIPAddress

    try:
        input_config = json.loads(data["config"])
        input_config["token_serial"]
        input_config["serial_number"]
        input_config["pin"]
        input_config["access_token"]
        input_config["app"]
        _LOGGER.exception(input_config)
    except:
        _LOGGER.exception("error")
        raise InvalidAccessToken
    
    # Required("token_serial"): str,
    # Required("serial_number"): str,
    # Required("pin"): str,
    # Required("access_token"): str,
    # Required("app"): str
    
    if len(input_config["token_serial"]) < 5 or len(input_config["serial_number"]) < 5:
        _LOGGER.exception("error 1")
        raise InvalidSerialNumber
    
    if len(input_config["token_serial"]) < 5:
        _LOGGER.exception("error 2")
        raise InvalidTokenSerial

    if len(input_config["pin"]) < 6 or len(input_config["pin"]) > 9:
        _LOGGER.exception("error 3")
        raise InvalidPin

    try:
        access_token = input_config["access_token"]
        if access_token["access_token"] and access_token["expires_in"] and access_token["refresh_token"] and access_token["scope"] and access_token["token_type"]:
            """This token is good"""
    except:
        _LOGGER.exception("error 4")
        raise InvalidAccessToken

    if len(input_config["app"]) >= 1:
        app_list = input_config["app"].split(';')
        for app in app_list:
            if app not in ["XHDO", "BHXH", "THUE", "KHAC"]:
                _LOGGER.exception("error 5")
                raise InvalidApp


    token = Token(hass, data["name"], input_config["token_serial"], input_config["serial_number"], input_config["access_token"], input_config["pin"], input_config["app"])
    # The dummy token provides a `test_connection` method to ensure it's working
    # as expected
    _LOGGER.exception("error 6")

    # result = await token.test_connection()
    # if not result:
    #     # If there is an error, raise an exception to notify HA that there was a
    #     # problem. The UI will also show there was a problem
    #     raise CannotConnect

    return {"title": data["name"]}


class ConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Hello World."""

    VERSION = 1
    # Pick one of the available connection classes in homeassistant/config_entries.py
    # This tells HA if it should be asking for updates, or it'll be notified of updates
    # automatically. This example uses PUSH, as the dummy token will notify HA of
    # changes.
    CONNECTION_CLASS = config_entries.CONN_CLASS_LOCAL_PUSH

    async def async_step_user(self, user_input=None):
        """Handle the initial step."""
        # This goes through the steps to take the user through the setup process.
        # Using this it is possible to update the UI and prompt for additional
        # information. This example provides a single form (built from `DATA_SCHEMA`),
        # and when that has some validated input, it calls `async_create_entry` to
        # actually create the HA config entry. Note the "title" value is returned by
        # `validate_input` above.
        errors = {}
        if user_input is not None:
            try:
                info = await validate_input(self.hass, user_input)

                return self.async_create_entry(title=info["title"], data=user_input)
            except ConnectionError:
                errors["base"] = "cannot_connect"
            except InvalidName:
                # The error string is set here, and should be translated.
                # This example does not currently cover translations, see the
                # comments on `DATA_SCHEMA` for further details.
                # Set the error on the `name` field, not the entire form.
                errors["name"] = "invalid_name"
            except InvalidConfig:
                errors["config"] = "invalid_config"
            except InvalidIPAddress:
                errors["api_ip_address"] = "invalid_ip_address"
            except InvalidTokenSerial:
                errors["config"] = "invalid_token_serial"
            except InvalidSerialNumber:
                errors["config"] = "invalid_serial_number"
            except InvalidPin:
                errors["config"] = "invalid_pin"
            except InvalidAccessToken:
                errors["config"] = "invalid_access_token"
            except InvalidApp:
                errors["config"] = "invalid_app"
            except Exception:  # pylint: disable=broad-except
                _LOGGER.exception("Unexpected exception")
                errors["base"] = "unknown"

        # If there is no user input or there were errors, show the form again, including any errors that were found with the input.
        return self.async_show_form(
            step_id="user", data_schema=DATA_SCHEMA, errors=errors
        )


class ConnectionError(exceptions.HomeAssistantError):
    """Error to indicate we cannot connect."""


class InvalidName(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid name."""

class InvalidSerialNumber(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid serial number."""

class InvalidTokenSerial(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid token serial."""

class InvalidPin(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid pin."""

class InvalidAccessToken(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid accessToken."""

class InvalidApp(exceptions.HomeAssistantError):
    """Error to indicate there is an invalid app."""

class InvalidConfig(exceptions.HomeAssistantError):
    """Error input json config"""

class InvalidIPAddress(exceptions.HomeAssistantError):
    """Error input json config"""