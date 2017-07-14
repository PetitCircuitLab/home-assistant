"""
Support for Z-Way API.

For more details about this component, please refer to the documentation at
https://home-assistant.io/components/zway/
"""
from datetime import timedelta
import logging

from homeassistant.const import (
    EVENT_HOMEASSISTANT_START, CONF_URL, CONF_USERNAME, CONF_PASSWORD)
from homeassistant.helpers import discovery
import homeassistant.helpers.config_validation as cv
from homeassistant.helpers.entity import Entity
from homeassistant.helpers.event import track_point_in_utc_time
from homeassistant.util.dt import utcnow
import voluptuous as vol

DOMAIN = 'zway'

REQUIREMENTS = ['petitzway==0.0.5']

_LOGGER = logging.getLogger(__name__)

MIN_UPDATE_INTERVAL = timedelta(seconds=2)
DEFAULT_UPDATE_INTERVAL = timedelta(seconds=2)

CONF_UPDATE_INTERVAL = 'update_interval'

CONFIG_SCHEMA = vol.Schema({
    DOMAIN: vol.Schema({
        vol.Required(CONF_URL): cv.string,
        vol.Required(CONF_USERNAME): cv.string,
        vol.Required(CONF_PASSWORD): cv.string,
        vol.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): (
            vol.All(cv.time_period, vol.Clamp(min=MIN_UPDATE_INTERVAL)))
    }),
}, extra=vol.ALLOW_EXTRA)


def setup(hass, config):
    """Set up the Z-Way component."""
    client = ZwayClient(hass, config)

    hass.data[DOMAIN] = client

    hass.bus.listen(EVENT_HOMEASSISTANT_START, client.update)

    return True


class ZwayClient(object):
    """Get the latest data and update the states."""

    def __init__(self, hass, config):
        """Initialize the Z-Way data object."""
        from petitzway import Controller

        username = config[DOMAIN].get(CONF_USERNAME)
        password = config[DOMAIN].get(CONF_PASSWORD)
        url = config[DOMAIN].get(CONF_URL)

        self.entities = []

        self._interval = config[DOMAIN].get(CONF_UPDATE_INTERVAL)
        self._hass = hass
        self._config = config
        self._client = Controller(baseurl=url,
                                  username=username, password=password)

    def update(self, *args):
        """Update local list of devices."""
        try:
            self._sync()
        finally:
            track_point_in_utc_time(self._hass, self.update,
                                    utcnow() + self._interval)

    def _sync(self):
        """Update local list of devices."""
        if not self._client.update():
            _LOGGER.warning("Failed request")

        def discover(device_id, component):
            """Discover the component."""
            discovery.load_platform(self._hass, component, DOMAIN,
                                    [device_id], self._config)

        known_ids = {entity.device_id for entity in self.entities}

        for device in self._client.get_all_devices():
            if device.device_id in known_ids:
                continue
            if device.devicetype == "switchBinary":
                discover(device.device_id, 'switch')
            if device.devicetype == "sensorMultilevel":
                discover((device.device_id,
                          device.probetype,
                          device.metrics['scaleTitle']), 'sensor')
            if device.devicetype == "sensorBinary":
                discover((device.device_id,
                          device.probetype), 'binary_sensor')

            for entity in self.entities:
                entity.changed()

    def device(self, device_id):
        """Return device representation."""
        return self._client.device(device_id)


class ZwayEntity(Entity):
    """Base class for all Z-Way entities."""

    def __init__(self, hass, device_id):
        """Initialize the entity."""
        self._id = device_id
        self._client = hass.data[DOMAIN]
        self._name = self.device.title
        self._client.entities.append(self)

    def changed(self):
        """Return the property of the device might have changed."""
        if self.device.title:
            self._name = self.device.title
        self.schedule_update_ha_state()

    @property
    def device_id(self):
        """Return the id of the device."""
        return self._id

    @property
    def name(self):
        """Return name of device."""
        return self._name

    @property
    def device(self):
        """Return the representaion of the device."""
        return self._client.device(self.device_id)

    @property
    def should_poll(self):
        """Return the polling state."""
        return False
