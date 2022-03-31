"""Platform for sensor integration."""
# This file shows the setup for the sensors associated with the cover.
# They are setup in the same way with the call to the async_setup_entry function
# via HA from the module __init__. Each sensor has a device_class, this tells HA how
# to display it in the UI (for know types). The unit_of_measurement property tells HA
# what the unit is, so it can display the correct range. For predefined types (such as
# battery), the unit_of_measurement should match what's expected.
import random

from homeassistant.const import (
    ATTR_VOLTAGE,
    DEVICE_CLASS_BATTERY,
    DEVICE_CLASS_ILLUMINANCE,
    PERCENTAGE,
)
from homeassistant.components.device_automation.const import CONF_IS_OFF, CONF_IS_ON
from homeassistant.helpers.entity import Entity
from homeassistant.components.binary_sensor import BinarySensorEntity
from .const import DOMAIN


# See cover.py for more details.
# Note how both entities for each cron sensor (cron sensor and cover) are added at
# the same time to the same list. This way only a single async_add_devices call is
# required.

# async def async_remove_entry(hass, entry) -> None:

async def async_setup_entry(hass, config_entry, async_add_entities):
    """Add sensors for passed config_entry in HA."""
    token = hass.data[DOMAIN][config_entry.entry_id]

    new_devices = []
    for cron in token.crons:
        new_devices.append(BatterySensor(cron))
            # new_devices.append(IlluminanceSensor(cron))
            # hass.data[DOMAIN][config_entry.entry_id].set_installed()
    if new_devices:
        async_add_entities(new_devices)


# This base class shows the common properties and methods for a sensor as used in this
# example. See each sensor for further details about properties and methods that
# have been overridden.
class SensorBase(BinarySensorEntity):
    """Base representation of a Hello World Sensor."""

    should_poll = False

    def __init__(self, cron):
        """Initialize the sensor."""
        self._cron = cron

    # To link this entity to the cover device, this property must return an
    # identifiers value matching that used in the cover, but no other information such
    # as name. If name is returned, this entity will then also become a device in the
    # HA UI.
    @property
    def device_info(self):
        """Return information to link this entity with the correct device."""
        return {
            "identifiers": {(DOMAIN, self._cron.cron_id)},
            # If desired, the name for the device could be different to the entity
            "name": self.name,
            "sw_version": self._cron.firmware_version,
            "model": self._cron.model,
            "manufacturer": self._cron.token.manufacturer,
        }

class BatterySensor(SensorBase):
    """Representation of a Sensor."""

    # The class of this device. Note the value should come from the homeassistant.const
    # module. More information on the available devices classes can be seen here:
    # https://developers.home-assistant.io/docs/core/entity/sensor
    device_class = "running"

    # The unit of measurement for this entity. As it's a DEVICE_CLASS_BATTERY, this
    # should be PERCENTAGE. A number of units are supported by HA, for some
    # examples, see:
    # https://developers.home-assistant.io/docs/core/entity/sensor#available-device-classes
    # _attr_unit_of_measurement = "running"

    def __init__(self, cron):
        """Initialize the sensor."""
        super().__init__(cron)
        # As per the sensor, this must be a unique value within this domain. This is done
        # by using the device ID, and appending "_battery"
        self._attr_unique_id = f"{self._cron.cron_id}_sensor"
        # The name of the entity
        self._attr_name = f"Token sensor"
        

    @property
    def icon(self) -> str:
        """Icon of the entity."""
        return "mdi:account"
        # return "mdi:alarm-light"


    # The value of this sensor. As this is a DEVICE_CLASS_BATTERY, this value must be
    # the battery level as a percentage (between 0 and 100)
    @property
    def state(self):
        """Return the state of the sensor."""
        return self._cron.is_enable

    @property
    def is_on(self):
        """Return true if the binary sensor is on."""
        return self._state

# This is another sensor, but more simple compared to the battery above. See the
# comments above for how each field works.