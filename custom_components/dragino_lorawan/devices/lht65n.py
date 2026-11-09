"""Dragino LHT65N device model and extension decoders."""

from datetime import datetime
from typing import override

from lorawan_connection import DeviceDescriptor, DeviceEvent, EventType

from .base import DraginoDevice

BATTERY_STATUSES = ("ultra_low", "low", "ok", "good")


class LHT65N(DraginoDevice):
    """Decode LHT65N telemetry and supported external attachments."""

    identifiers = {"tts": ("dragino", "lht65")}
    model_name = "LHT65N"

    def __init__(self, descriptor: DeviceDescriptor) -> None:
        """Initialize values as unknown until an uplink arrives."""
        super().__init__(descriptor)
        self.temperature: float | None = None
        self.humidity: float | None = None
        self.battery_voltage: float | None = None
        self.battery_status: str | None = None
        self.motion: bool | None = None
        self.movement_count: int | None = None
        self.external_sensor_disconnected: bool | None = None
        self.firmware_version: str | None = None
        self.capabilities = {
            "temperature",
            "humidity",
            "battery_voltage",
            "battery_status",
        }
        self._updated: dict[str, datetime] = {}

    @override
    def handle_event(self, event: DeviceEvent) -> None:
        """Process live uplinks without replacing newer state."""
        if self.closed or event.type != EventType.UPLINK:
            return
        try:
            if event.f_port == 2:
                values = self.decode_data(event.data)
            elif event.f_port == 5:
                values = self.decode_status(event.data)
            else:
                return
        except ValueError:
            return
        values = {
            name: value
            for name, value in values.items()
            if name not in self._updated or event.received_at >= self._updated[name]
        }
        if not values:
            return
        for name, value in values.items():
            setattr(self, name, value)
        self.capabilities.update(values.keys())
        self._updated.update(dict.fromkeys(values, event.received_at))
        self.notify()

    @staticmethod
    def decode_data(
        data: bytes,
    ) -> dict[str, float | int | bool | str | None]:
        """Decode a current port-2 sensor report and its attachment data."""
        if len(data) != 11:
            raise ValueError("Invalid LHT65N frame length")
        if data[6] & 0x40:
            return {}  # Datalog response, not current state.
        humidity = (int.from_bytes(data[4:6], "big") & 0xFFF) / 10
        if not 0 <= humidity <= 100:
            raise ValueError("Humidity outside sensor range")
        raw_battery = int.from_bytes(data[:2], "big")
        values: dict[str, float | int | bool | str | None] = {
            "battery_voltage": (raw_battery & 0x3FFF) / 1000,
            "battery_status": BATTERY_STATUSES[raw_battery >> 14],
            "temperature": int.from_bytes(data[2:4], "big", signed=True) / 100,
            "humidity": humidity,
            "external_sensor_disconnected": bool(data[6] & 0x80),
        }
        extension = data[6] & 0x0F
        if extension == 0x0E:
            values.update(
                motion=bool(data[7] & 0x01),
                movement_count=int.from_bytes(data[8:11], "big"),
            )
        return values

    @staticmethod
    def decode_status(data: bytes) -> dict[str, str | float]:
        """Decode the device-information reply on port 5."""
        if len(data) < 7 or data[0] != 0x1A:
            raise ValueError("Not an LHT65N status frame")
        return {
            "firmware_version": (
                f"{data[1] & 0x0F}.{(data[2] >> 4) & 0x0F}.{data[2] & 0x0F}"
            ),
            "battery_voltage": int.from_bytes(data[5:7], "big") / 1000,
        }
