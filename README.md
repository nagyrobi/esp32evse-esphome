# ESP32EVSE ESPHome Integration

This repository provides an [ESPHome](https://esphome.io/) configuration and custom
component that exposes the full feature set of the ESP32EVSE charging controller.
It demonstrates how to integrate telemetry, control, and maintenance operations in
Home Assistant using ESPHome's native API.

## Repository layout

- `components/esp32evse/` – Custom ESPHome component implementation.
- `esphome.yaml` – Example configuration showcasing every supported entity exposed
  by the component.

## Getting started

1. Install the ESPHome command line tools by following the
   [official ESPHome installation guide](https://esphome.io/guides/installing_esphome.html).
2. Update the Wi-Fi credentials in `esphome.yaml` (`wifi.ssid` and `wifi.password`).
3. Optionally adjust the entity names or number limits in `esphome.yaml` to match
   your installation.
4. Connect your ESP32EVSE hardware to your computer via USB and flash the firmware:

   ```bash
   esphome run esphome.yaml
   ```

   The initial flash uses the USB connection. Subsequent updates can be performed
   over-the-air using the ESPHome Dashboard or the same command.

## Entities exposed

The example configuration enables every entity type currently supported by the
custom component. You can selectively disable groups you do not need by removing
or commenting out the related sections in `esphome.yaml`.

### Binary sensors

- **Pending Authorization** – Indicates when the charger waits for authorization.
- **Wi-Fi Connected** – Shows the connection status of the Wi-Fi station interface.

### Buttons

- **Fast Power Subscribe / Unsubscribe** – Opt in or out of fast power telemetry
  updates from the charger.
- **Reset** – Triggers a software reset of the charger.
- **Authorize** – Sends an authorization command for the currently connected vehicle.

### Numbers

All numeric controls support configurable minimum/maximum values, step size, and
communication multiplier where applicable.

- Charging current (instant, default, maximum)
- Consumption limit (instant, default)
- Charging time limit (instant, default)
- Under-power limit (instant, default)

### Sensors

- Temperature
- Power, session duration, and charging duration
- Free heap memory
- Session and total energy consumption
- Line voltages (L1/L2/L3)
- Line currents (L1/L2/L3)
- Wi-Fi RSSI

### Switches

- Charging enable – Master enable/disable for the charger.
- Available – Manually mark the charger as available to clients.
- Request authorization – Toggle whether authorization is requested for new sessions.

### Text sensors

- Charger state
- MCU identification
- Firmware version and ESP-IDF version
- Firmware build time and device runtime clock
- Wi-Fi SSID, IP address, and MAC address
- Configured device name

## Customization tips

- Rename entities to match your Home Assistant naming convention.
- Adjust number ranges to match the electrical limits of your installation.
- Remove sections you do not need to reduce resource usage on the device.

With the configuration in this repository you can quickly evaluate the ESP32EVSE
component and tailor it to your own EV charging project.
