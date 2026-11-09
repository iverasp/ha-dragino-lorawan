"""Binary sensors for Dragino LoRaWAN devices."""

from typing import override

from homeassistant.components.binary_sensor import (
    BinarySensorDeviceClass,
    BinarySensorEntity,
    BinarySensorEntityDescription,
)
from homeassistant.components.lorawan import LoRaWANEntity
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import DraginoConfigEntry
from .coordinator import DraginoCoordinator
from .devices import DraginoDevice, LHT65N

PARALLEL_UPDATES = 0

LHT65N_DESCRIPTIONS = (
    BinarySensorEntityDescription(
        key="motion", device_class=BinarySensorDeviceClass.MOTION
    ),
)

DESCRIPTIONS: dict[
    type[DraginoDevice], tuple[BinarySensorEntityDescription, ...]
] = {LHT65N: LHT65N_DESCRIPTIONS}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DraginoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up binary sensors supported by each Dragino product."""

    @callback
    def added(coordinator: DraginoCoordinator) -> None:
        descriptions = DESCRIPTIONS.get(type(coordinator.data), ())
        async_add_entities(
            DraginoBinarySensor(coordinator, description)
            for description in descriptions
            if description.key in coordinator.data.capabilities
        )

    entry.async_on_unload(entry.runtime_data.subscribe_coordinator_added(added))


class DraginoBinarySensor(LoRaWANEntity[DraginoDevice], BinarySensorEntity):
    """A binary state reported by a Dragino device."""

    coordinator: DraginoCoordinator

    @property
    @override
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    @property
    @override
    def is_on(self) -> bool | None:
        value = getattr(self.device, self.entity_description.key, None)
        return value if isinstance(value, bool) else None
