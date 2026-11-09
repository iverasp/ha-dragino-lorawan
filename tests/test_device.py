"""Tests for the LHT65N decoder and PIR attachment."""

from custom_components.dragino_lorawan.devices.lht65n import LHT65N


def test_decode_data() -> None:
    """Decode temperature, humidity, PIR, count, and battery."""
    payload = bytes.fromhex("0BB80A2802260E01000123")
    assert LHT65N.decode_data(payload) == {
        "battery_voltage": 3.0,
        "battery_status": "ultra_low",
        "temperature": 26.0,
        "humidity": 55.0,
        "external_sensor_disconnected": False,
        "motion": True,
        "movement_count": 0x123,
    }


def test_decode_data_without_pir_attachment() -> None:
    """Decode base readings without exposing PIR values."""
    payload = bytes.fromhex("0BB80A2802260100000000")
    assert LHT65N.decode_data(payload) == {
        "battery_voltage": 3.0,
        "battery_status": "ultra_low",
        "temperature": 26.0,
        "humidity": 55.0,
        "external_sensor_disconnected": False,
    }


def test_decode_battery_status() -> None:
    """Decode the two high battery-status bits."""
    payload = bytes.fromhex("CBB80A2802260100000000")
    values = LHT65N.decode_data(payload)
    assert values["battery_voltage"] == 3.0
    assert values["battery_status"] == "good"


def test_decode_status() -> None:
    """Decode firmware and battery from a device status frame."""
    payload = bytes.fromhex("1A015601FF0BB8")
    assert LHT65N.decode_status(payload) == {
        "firmware_version": "1.5.6",
        "battery_voltage": 3.0,
    }
