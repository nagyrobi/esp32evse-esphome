# ESP32EVSE ESPHome Integration

This repository provides an [ESPHome](https://esphome.io/) configuration and custom
component that exposes the most important control features of the [ESP32-EVSE](https://github.com/dzurikmiroslav/esp32-evse) charging controller.

## Repository layout

- `components/esp32evse/` – Custom ESPHome component implementation.
- `esphome.yaml` – Example configuration showcasing every supported entity exposed
  by the component.

## Requirements

Check out ESPHome [documentation](https://esphome.io/) to learn about the working 
principle of the integration.
Check out ESP32-EVSE [documentation]([https://esphome.io/](https://github.com/dzurikmiroslav/esp32-evse/wiki) to learn on how to use ESP32-EVSE

You need an ESP32 board supported by ESPHome. The component communicates with ESP32-EVSE (min. version 2.0.0) via UART at 115200 baud rate. 
Enter your ESP32-EVSE web UI and in _Settings_ > _Serial_, select for the UART port _Mode_: _AT Commands_ and _Baud rate_: _115200_ then press Submit. 

If you use the [esp32s2-evse-d-a board](https://github.com/dzurikmiroslav/esp32-evse/wiki/ESP32-S2-DA) you can use a 4-pin cable with 2.5mm JST wired correctly for RX/TX/GND/5V:

| ESP32-EVSE S2 DA U6 UART (1 leftmost looking from top, 2.5mm JST) |
| -------- |
| 1: GND |
| 2: TX |
| 3: RX |
| 4: +5V |

## Entities exposed

The example configuration enables every entity type currently supported by the
custom component. You can selectively disable groups you do not need by removing
or commenting out the related sections in `esphome.yaml`.

### Sensors

- **Temperatures**
- **Power**, **session duration**, and **charging duration**
- **Heap memory usage** (used and total)
- **Session time** and **total energy consumption**
- **Line voltages** (L1/L2/L3)
- **Line currents** (L1/L2/L3)
- **Wi-Fi RSSI** (signal strength)

### Switches

- **Charging enable** – Master enable/disable for the charger, can be used to start/stop charging.
- **Available** – Manually mark the charger as available to clients.
- **Request authorization** – Toggle whether authorization is requested for new sessions.

### Buttons

- **Authorize** – Sends an authorization command for the currently connected vehicle if request authorization was enabled.
- **Reset** – Triggers a software reset of the charger.

### Binary sensors

- **Pending Authorization** – Indicates when the charger waits for authorization if request authorization was enabled.
- **Wi-Fi Connected** – Shows the connection status of the Wi-Fi station interface.

### Numbers

- **Charging current** (instant per session, default, maximum possible)
- **Consumption limit** (instant per session, default)
- **Charging time limit** (instant per session, default)
- **Under-power limit** (instant per session, default)

### Text sensors

- **Charger state** according to the J1772 standard
- **Configured device name**
- **MCU identification**
- **Firmware version** and **ESP-IDF version**
- **Firmware build time** and **device runtime clock**
- **Wi-Fi SSID**, **IP address**, **MAC address**

## Customization tips

- Rename entities to match your automation platform naming convention.
- Adjust number ranges to match the electrical limits of your installation.
- Remove sections you do not need to reduce resource usage on the device.

### Using generic AT subscriptions from YAML

The component exposes helper methods so you can trigger `AT+SUB` / `AT+UNSUB`
commands directly from ESPHome lambdas. This allows custom subscriptions beyond
the built-in fast power helpers. For example, you can add buttons that control a
subscription to the `EMETERPOWER` feed:

```yaml
button:
  - platform: template
    name: "Subscribe to EMETERPOWER"
    on_press:
      - lambda: |-
          id(evse).at_sub("\"+EMETERPOWER\"", 1000);
  - platform: template
    name: "Unsubscribe from EMETERPOWER"
    on_press:
      - lambda: |-
          id(evse).at_unsub("\"+EMETERPOWER\"");
```

Passing an empty string to `at_unsub()` sends `AT+UNSUB=""`,
which clears every active subscription:

```yaml
  - platform: template
    name: "Unsubscribe from all feeds"
    on_press:
      - lambda: |-
          id(evse).at_unsub("");
```

### Using the `esp32evse.autoupdate` action

Manually calling `at_sub()` from lambdas is powerful but requires remembering
the AT command names. The component therefore also exposes an
`esp32evse.autoupdate` action that maps the command from the entity ID:

```yaml
text_sensor:
  - platform: esp32evse
    esp32evse_id: evse
    state:
      id: evse_state

interval:
  - interval: 10s
    then:
      - esp32evse.autoupdate:
          id: evse_state
          period: 1000
```

When invoked with a non-zero period the action subscribes to the fast update
feed associated with the entity. Passing `0` unsubscribes from the same feed:

```yaml
      - esp32evse.autoupdate:
          id: evse_state
          period: 0
```


