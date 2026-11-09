"""Backward-compatible imports for Dragino device models."""

from .devices import DraginoDevice, DraginoDeviceCollection, LHT65N

LHT65NPIR = LHT65N

__all__ = ["DraginoDevice", "DraginoDeviceCollection", "LHT65N", "LHT65NPIR"]
