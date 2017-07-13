"""
"""
import logging

from homeassistant.components.zway import ZwayEntity
from homeassistant.const import TEMP_CELSIUS

_LOGGER = logging.getLogger(__name__)

SENSOR_TYPE_TEMP = 'temperature'
SENSOR_TYPE_LUMINANCE = 'luminance'

SENSOR_TYPES = {
    SENSOR_TYPE_TEMP: ['Temperature', TEMP_CELSIUS, 'mdi:thermometer'],
    SENSOR_TYPE_LUMINANCE: ['Luminance', 'lx', ''],
}


def setup_platform(hass, config, add_devices, discovery_info=None):
    """Set up Zway sensors."""
    if discovery_info is None:
        return
    add_devices(ZwaySensor(hass, switch) for switch in discovery_info)


class ZwaySensor(ZwayEntity):
    """Representation of a Zway sensor."""

    @property
    def state(self):
        """Return the value of the sensor."""
        level = None
        if type(self.device.level) is float:
            level = round(self.device.level, 1)
        else:
            level = self.device.level
        return level

    #@property
    #def unit_of_measurement(self):
    #    """Return the unit of measurement."""
    #    return self._id[2]

    @property
    def unit_of_measurement(self):
        """Return the unit of measurement."""
        return SENSOR_TYPES[self._type][1] \
            if self._type in SENSOR_TYPES else self._id[2]

    @property
    def device_id(self):
        """Return id of the device."""
        return self._id[0]

    @property
    def _type(self):
        """Return the type of the sensor."""
        return self._id[1]

    @property
    def icon(self):
        """Return the icon."""
        return SENSOR_TYPES[self._type][2] \
            if self._type in SENSOR_TYPES else None
