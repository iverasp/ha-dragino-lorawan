# Dragino LoRaWAN for Home Assistant

Custom Home Assistant integration using the native LoRaWAN framework introduced
in Home Assistant 2026.11.

## Supported devices

- Dragino LHT65N registered in The Things Stack with the Dragino `lht65`
  catalog identity, including the PIR external attachment

Entities: temperature, humidity, PIR motion, movement count, battery voltage,
and battery status.

## Installation

### Marketplace

1. Open **Settings → Marketplace** in Home Assistant 2026.11 or newer.
2. Select **Add from link** and enter
   `https://github.com/iverasp/ha-dragino-lorawan`.
3. Install **Dragino LoRaWAN** and restart Home Assistant when prompted.

### Manual installation

1. Copy `custom_components/dragino_lorawan` into Home Assistant's
   `config/custom_components` directory.
2. Restart Home Assistant.

### Configuration

1. Ensure the native **The Things Network** LoRaWAN integration is configured.
2. Open **Settings → Devices & services** and configure the discovered
   **Dragino LoRaWAN** integration, or add it manually.
3. Send a fresh uplink from the device.

The TTN device must use the Dragino device-repository identity. The integration
matches `dragino/lht65`; external attachments are detected from their type in
port-2 uplinks. The PIR attachment uses extension type `0x0e` and enables the
motion and movement-count entities.

## Development

The integration requires Home Assistant 2026.11 or newer. Decoder tests can run
inside a Home Assistant development environment with:

```bash
pytest tests/test_device.py
```

The PIR payload format follows Dragino's official LHT65N-PIR TTN decoder.

### Adding a product

Device decoders live in `custom_components/dragino_lorawan/devices`. To add a
product, subclass `DraginoDevice`, declare its LoRaWAN `identifiers` and
`model_name`, and add it to `DraginoDeviceCollection.DEVICES`. Register only
the entities supported by that product in the per-device maps in `sensor.py`
and `binary_sensor.py`.
