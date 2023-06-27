"""The Detailed Hello World Push integration."""
from __future__ import annotations

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
import json
import logging
from .token import Token
from .const import DOMAIN, API_IP

_LOGGER = logging.getLogger(__name__)

# List of platforms to support. There should be a matching .py file for each,
# eg <cover.py> and <sensor.py>
PLATFORMS: list[str] = ["sensor", "light"]


async def async_setup_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Set up Hello World from a config entry."""
    # Store an instance of the "connecting" class that does the work of speaking
    # with your actual devices.
    api_ip_address = API_IP
    try:
        input_config = json.loads(entry.data["json_config"])
        input_config["token_serial"]
        input_config["serial_number"]
        input_config["pin"]
        input_config["access_token"] = json.dumps(input_config["access_token"])
        input_config["app"]
        input_config["tax_ids"]
        pdf_options = ""
        if "pdf_options" in input_config and len(input_config["pdf_options"]) >= 1:
            pdf_options = json.dumps(input_config["pdf_options"])
    except:
        """Input config error"""
        _LOGGER.exception("Unexpected exception")
        return True

    tax_ids = []
    if len(input_config["tax_ids"]) >= 1:
        for tax_id in input_config["tax_ids"]:
            if tax_id.replace("-", "").isnumeric() and len(tax_id.replace("-", "")) >= 10 and len(tax_id.replace("-", "")) <= 16:
                tax_ids.append(tax_id.replace("-", ""))
    
    token = Token(hass, entry.data["name"], api_ip_address, pdf_options, json.dumps(tax_ids), input_config["token_serial"], input_config["serial_number"], input_config["access_token"], input_config["pin"], input_config["app"])
    await token.check_serial_exists()
    hass.data.setdefault(DOMAIN, {})[entry.entry_id] = token
    _LOGGER.info("Token ok")

    # hass.data.setdefault(DOMAIN, {})[entry.entry_id] = token.Token(hass, entry.data["name"], entry.data["token_serial"], entry.data["serial_number"], entry.data["access_token"], entry.data["pin"], entry.data["app"]) if entry.entry_id not in hass.data.setdefault(DOMAIN, {}).keys() else False

    # This creates each HA object for each platform your device requires.
    # It's done by calling the `async_setup_entry` function in each platform module.
    hass.config_entries.async_setup_platforms(entry, PLATFORMS)
    # hass.async_create_task(
    #     hass.config_entries.async_forward_entry_setup(
    #         ConfigEntry, "cover"
    #     )
    # )
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ConfigEntry) -> bool:
    """Unload a config entry."""
    # This is called when an entry/configured device is to be removed. The class
    # needs to unload itself, and remove callbacks. See the classes for further
    # details
    unload_ok = await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
    if unload_ok:
        hass.data[DOMAIN].pop(entry.entry_id)

    return unload_ok
