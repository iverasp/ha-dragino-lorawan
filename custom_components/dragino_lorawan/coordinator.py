"""Coordinate push updates from Dragino devices."""

import logging
from typing import override

from homeassistant.components.lorawan import device_identifier
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator

from .const import DOMAIN
from .devices import DraginoDevice

_LOGGER = logging.getLogger(__name__)


class DraginoCoordinator(DataUpdateCoordinator[DraginoDevice]):
    """Distribute updates from one physical device."""

    def __init__(self, hass: HomeAssistant, device: DraginoDevice) -> None:
        super().__init__(
            hass, _LOGGER, config_entry=None, name=device.descriptor.name
        )
        self.async_set_updated_data(device)
        self._unsubscribe = device.add_update_listener(self._async_device_updated)

    @property
    def device_info(self) -> DeviceInfo:
        """Return registry information for this Dragino device."""
        return DeviceInfo(
            identifiers={device_identifier(DOMAIN, self.data)},
            name=self.data.descriptor.name,
            manufacturer="Dragino",
            model=self.data.model_name,
            model_id=self.data.model_name,
            sw_version=self.data.firmware_version,
        )

    @callback
    def _async_device_updated(self) -> None:
        self.async_set_updated_data(self.data)

    @override
    async def async_shutdown(self) -> None:
        self._unsubscribe()
        await super().async_shutdown()
