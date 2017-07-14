"""
Support for Z-Way API.

For more details about this platform, please refer to the documentation at
https://home-assistant.io/components/binary_sensor.zway/
"""
import logging

from homeassistant.components.zway import ZwayEntity
from homeassistant.components.binary_sensor import BinarySensorDevice

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_ALARM_BURGLAR = 'alarm_burglar'
SENSOR_TYPE_ALARM_DOOR = 'alarm_door'
SENSOR_TYPE_DOOR_WINDOW = 'door-window'


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up Zway binary sensors."""
    if discovery_info is None:
        return
    add_devices(ZwayBinarySensor(hass, switch) for switch in discovery_info)


class ZwayBinarySensor(ZwayEntity, BinarySensorDevice):
    """Representation of a Tellstick switch."""

    @property
    def is_on(self):
        """Return true if switch is on."""
        return self.device.is_on

    @property
    def device_id(self):
        """Return id of the device."""
        return self._id[0]

    @property
    def _device_class(self):
        """Return the class of the sensor."""
        return {
            'alarm_burglar': 'motion',
            'door-window': 'opening',
            'alarm_door': 'opening',
            'alarm_system': 'motion',
            'alarm_heat': 'heat',
        }.get(self._id[1], '')

    @property
    def device_class(self):
        """Return the class of the sensor."""
        return self._device_class
