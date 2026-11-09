"""Supported Dragino device models."""

from lorawan_connection import DeviceCollection

from .base import DraginoDevice
from .lht65n import LHT65N

__all__ = ["DraginoDevice", "DraginoDeviceCollection", "LHT65N"]


class DraginoDeviceCollection(DeviceCollection[DraginoDevice]):
    """Catalog of supported Dragino products."""

    DEVICES = (LHT65N,)
