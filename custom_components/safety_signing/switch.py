# Light đang lỗi không tạo trigger action được vì ko có hiện on off method

"""Platform for sensor integration."""
from __future__ import annotations

from typing import Any, Optional

# These constants are relevant to the type of entity we are using.
# See below for how they are used.
from homeassistant.components.cover import (
    ATTR_POSITION,
    SUPPORT_CLOSE,
    SUPPORT_OPEN,
    SUPPORT_SET_POSITION,
    CoverEntity,
)
from homeassistant.const import (
    CONF_NAME,
    STATE_OFF,
    STATE_ON,
)
from homeassistant.components.switch import DOMAIN as SWITCH_DOMAIN, SwitchEntity
from homeassistant.helpers.restore_state import RestoreEntity

from homeassistant.components.light import LightEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from .const import DOMAIN

import logging
_LOGGER = logging.getLogger(__name__)

# This function is called as part of the __init__.async_setup_entry (via the
# hass.config_entries.async_forward_entry_setup call)
async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add cover for passed config_entry in HA."""
    # The token is loaded from the associated hass.data entry that was created in the
    # __init__.async_setup_entry function
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(SimpleSwitch(hass, cron))
    if new_devices:
        async_add_entities(new_devices)


class SimpleSwitch(SwitchEntity, RestoreEntity):
    """Representation of a Adaptive Lighting switch."""

    def __init__(self, hass, cron):
        """Initialize the Adaptive Lighting switch."""
        self._hass = hass
        self._cron = cron
        self._icon = "mdi:skip-next-circle"
        self._unique_id = f"{self._cron.cron_id}_cron"
        self._name = f"{self._cron.name} cron"
        self._initial_state = True
        self._state = None

    @property
    def name(self):
        """Return the name of the device if any."""
        return self._name

    @property
    def unique_id(self):
        """Return the unique ID of entity."""
        return self._unique_id

    @property
    def icon(self) -> str:
        """Icon to use in the frontend, if any."""
        return self._icon

    @property
    def is_on(self) -> Optional[bool]:
        """Return true if adaptive lighting is on."""
        return self._state

    async def async_added_to_hass(self) -> None:
        """Call when entity about to be added to hass."""
        last_state = await self.async_get_last_state()
        _LOGGER.debug("%s: last state is %s", self._name, last_state)
        if (last_state is None and self._initial_state) or (
            last_state is not None and last_state.state == STATE_ON
        ):
            await self.async_turn_on()
        else:
            await self.async_turn_off()

    async def async_turn_on(self, **kwargs) -> None:
        """Turn on adaptive lighting sleep mode."""
        await self._cron.running_cron()
        self._state = True

    async def async_turn_off(self, **kwargs) -> None:
        """Turn off adaptive lighting sleep mode."""
        await self._cron.turn_off_cron()
        self._state = False


# This entire class could be written to extend a base class to ensure common attributes
# are kept identical/in sync. It's broken apart here between the Cover and Sensors to
# be explicit about what is returned, and the comments outline where the overlap is.
class CronJobEntity(LightEntity):
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
