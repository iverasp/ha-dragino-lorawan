"""Support Dragino devices over Home Assistant's LoRaWAN framework."""

from lorawan_connection import ConnectionUnavailable

from homeassistant.components.lorawan import DeviceManager
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv

from .const import DOMAIN
from .coordinator import DraginoCoordinator
from .devices import DraginoDevice, DraginoDeviceCollection

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)
type DraginoConfigEntry = ConfigEntry[
    DeviceManager[DraginoDevice, DraginoCoordinator]
]
PLATFORMS = [Platform.SENSOR, Platform.BINARY_SENSOR]


async def async_setup_entry(hass: HomeAssistant, entry: DraginoConfigEntry) -> None:
    """Set up supported Dragino devices across LoRaWAN connections."""
    manager = entry.runtime_data = DeviceManager(
        hass,
        entry,
        create_collection=DraginoDeviceCollection,
        create_coordinator=DraginoCoordinator,
    )
    entry.async_on_unload(manager.close)
    try:
        await manager.async_setup()
    except ConnectionUnavailable as err:
        raise ConfigEntryNotReady(str(err)) from err
    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)


async def async_unload_entry(hass: HomeAssistant, entry: DraginoConfigEntry) -> None:
    """Unload Dragino entities."""
    await hass.config_entries.async_unload_platforms_or_raise(entry, PLATFORMS)
