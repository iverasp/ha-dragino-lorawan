"""Sensors for Dragino LoRaWAN devices."""

from collections.abc import Callable
from dataclasses import dataclass
from typing import override

from homeassistant.components.lorawan import LoRaWANEntity
from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorEntityDescription,
    SensorStateClass,
)
from homeassistant.const import (
    PERCENTAGE,
    EntityCategory,
    UnitOfElectricPotential,
    UnitOfTemperature,
)
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.device_registry import DeviceInfo
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import DraginoConfigEntry
from .coordinator import DraginoCoordinator
from .devices import DraginoDevice, LHT65N

PARALLEL_UPDATES = 0


@dataclass(frozen=True, kw_only=True)
class DraginoSensorDescription(SensorEntityDescription):
    """Map one device value to a sensor."""

    value_fn: Callable[[DraginoDevice], float | int | str | None]


LHT65N_DESCRIPTIONS: tuple[DraginoSensorDescription, ...] = (
    DraginoSensorDescription(
        key="temperature",
        value_fn=lambda device: getattr(device, "temperature", None),
        device_class=SensorDeviceClass.TEMPERATURE,
        native_unit_of_measurement=UnitOfTemperature.CELSIUS,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    DraginoSensorDescription(
        key="humidity",
        value_fn=lambda device: getattr(device, "humidity", None),
        device_class=SensorDeviceClass.HUMIDITY,
        native_unit_of_measurement=PERCENTAGE,
        state_class=SensorStateClass.MEASUREMENT,
    ),
    DraginoSensorDescription(
        key="battery_voltage",
        value_fn=lambda device: getattr(device, "battery_voltage", None),
        translation_key="battery_voltage",
        device_class=SensorDeviceClass.VOLTAGE,
        native_unit_of_measurement=UnitOfElectricPotential.VOLT,
        state_class=SensorStateClass.MEASUREMENT,
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DraginoSensorDescription(
        key="battery_status",
        value_fn=lambda device: getattr(device, "battery_status", None),
        translation_key="battery_status",
        device_class=SensorDeviceClass.ENUM,
        options=["ultra_low", "low", "ok", "good"],
        entity_category=EntityCategory.DIAGNOSTIC,
    ),
    DraginoSensorDescription(
        key="movement_count",
        value_fn=lambda device: getattr(device, "movement_count", None),
        translation_key="movement_count",
    ),
)

DESCRIPTIONS: dict[type[DraginoDevice], tuple[DraginoSensorDescription, ...]] = {
    LHT65N: LHT65N_DESCRIPTIONS,
}


async def async_setup_entry(
    hass: HomeAssistant,
    entry: DraginoConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up sensors for existing and newly discovered devices."""

    @callback
    def added(coordinator: DraginoCoordinator) -> None:
        descriptions = DESCRIPTIONS.get(type(coordinator.data), ())
        async_add_entities(
            DraginoSensor(coordinator, description)
            for description in descriptions
            if description.key in coordinator.data.capabilities
        )

    entry.async_on_unload(entry.runtime_data.subscribe_coordinator_added(added))


class DraginoSensor(LoRaWANEntity[DraginoDevice], SensorEntity):
    """A measurement reported by a Dragino device."""

    coordinator: DraginoCoordinator
    entity_description: DraginoSensorDescription

    @property
    @override
    def device_info(self) -> DeviceInfo:
        return self.coordinator.device_info

    @property
    @override
    def native_value(self) -> float | int | str | None:
        return self.entity_description.value_fn(self.device)
