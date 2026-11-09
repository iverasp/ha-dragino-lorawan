"""Base model shared by Dragino LoRaWAN devices."""

from lorawan_connection import Device


class DraginoDevice(Device):
    """Base class for devices supported by the Dragino integration."""

    model_name: str
    firmware_version: str | None
    capabilities: set[str]
