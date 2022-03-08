"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any

# These constants are relevant to the type of entity we are using.
# See below for how they are used.
from homeassistant.components.cover import (
    ATTR_POSITION,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    CoverEntity,
)
from homeassistant.components.button import ButtonEntity
from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from .const import DOMAIN


# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add cover for passed config_entry in HA."""
    # The token is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(HelloWorldCover(hass, cron))
    if new_devices:
        async_add_entities(new_devices)


# This entire class could be written to extend a base class to ensure common attributes
# are kept identical/in sync. It's broken apart here between the Cover and Sensors to
# be explicit about what is returned, and the comments outline where the overlap is.
class HelloWorldCover(LightEntity):
    """Representation of a dummy Cover."""

    def __init__(self, hass, cron) -> None:
        """Initialize the sensor."""
        # Usual setup is done here. Callbacks are added in async_added_to_hass.
        self._hass = hass
        self._cron = cron
        self._attr_unique_id = f"{self._cron.cron_id}_button"
        self._attr_name = f"{self._cron.name}_button"
        self.is_light_on = False

    @property
    def device_info(self) -> DeviceInfo:
        """Information about this entity/device."""
        return {
            "identifiers": {(DOMAIN, self._cron.cron_id)},
            # If desired, the name for the device could be different to the entity
            "name": self.name,
            "sw_version": self._cron.firmware_version,
            "model": self._cron.model,
            "manufacturer": self._cron.token.manufacturer,
        }

    @property
    def available(self) -> bool:
        """Return True if cron and token is available."""
        return self._cron.online and self._cron.token.online

    async def async_added_to_hass(self) -> None:
        """Run when this Entity has been added to HA."""
        self._cron.register_callback(self.async_write_ha_state)

    async def async_will_remove_from_hass(self) -> None:
        """Entity being removed from hass."""
        self._cron.remove_callback(self.async_write_ha_state)
    
    @property
    def is_on(self) -> bool:
        return self.is_light_on

    @property
    def icon(self) -> str:
        """Icon of the entity."""
        return "mdi:skip-next-circle"

    async def async_turn_on(self, **kwargs):
        """Turn device on."""
        self.is_light_on = True
        if self._cron.is_enable == "on":
            await self._cron.running_cron()

    async def async_turn_off(self, **kwargs):
        self.is_light_on = False
        """Do nothing"""
