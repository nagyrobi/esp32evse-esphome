# ESP32EVSE ESPHome Integration

This repository provides an [ESPHome](https://esphome.io/) configuration and custom
component that exposes the most important control features of the [ESP32-EVSE](https://github.com/dzurikmiroslav/esp32-evse) charging controller.

It implements the communication with ESP32-EVSE using [AT Commands](https://github.com/dzurikmiroslav/esp32-evse/wiki/AT-commands).

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

```yaml
sensor:
  - platform: esp32evse
    esp32evse_id: evse
    emeter_power:
      name: "EVSE Power"
    emeter_charging_time:
      name: "EVSE Charging Time"
    emeter_session_time:
      name: "EVSE Session Time"
    energy_consumption:
      name: "EVSE Session Energy"
    total_energy_consumption:
      name: "EVSE Total Energy"
    voltage_l1:
      name: "EVSE Voltage L1"
    voltage_l2:
      name: "EVSE Voltage L2"
    voltage_l3:
      name: "EVSE Voltage L3"
    current_l1:
      name: "EVSE Current L1"
    current_l2:
      name: "EVSE Current L2"
    current_l3:
      name: "EVSE Current L3"
    temperature_high:
      name: "EVSE Temperature High"
    temperature_low:
      name: "EVSE Temperature Low"
    wifi_rssi:
      name: "EVSE Wi-Fi RSSI"
    heap_used:
      name: "EVSE Heap Used"
    heap_total:
      name: "EVSE Heap Total"
```
If your installation only uses a single probe, expose it via the combined ``temperature`` key instead of the individual high/low entries:

```yaml
    temperature:
      name: "EVSE Temperature"
```

### Switches

```yaml
switch:
  - platform: esp32evse
    esp32evse_id: evse
    enable:
      name: "EVSE Charging Enable"
    available:
      name: "EVSE Available"
    request_authorization:
      name: "EVSE Request Authorization"
```

### Buttons

```yaml
button:
  - platform: esp32evse
    esp32evse_id: evse
    authorize:
      name: "EVSE Authorize"
    reset:
      name: "EVSE Restart"
```

### Binary sensors

```yaml
binary_sensor:
  - platform: esp32evse
    esp32evse_id: evse
    pending_authorization:
      name: "EVSE Pending Authorization"
    wifi_connected:
      name: "EVSE Wi-Fi Connected"
```

### Numbers

```yaml
number:
  - platform: esp32evse
    esp32evse_id: evse
    charging_current:
      name: "EVSE Charging Current"
    default_charging_current:
      name: "EVSE Default Charging Current"
    maximum_charging_current:
      name: "EVSE Maximum Charging Current"
    consumption_limit:
      name: "EVSE Consumption Limit"
    default_consumption_limit:
      name: "EVSE Default Consumption Limit"
    charging_time_limit:
      name: "EVSE Charging Time Limit"
    default_charging_time_limit:
      name: "EVSE Default Charging Time Limit"
    under_power_limit:
      name: "EVSE Under Power Limit"
    default_under_power_limit:
      name: "EVSE Default Under Power Limit"
```

### Text sensors

```yaml
text_sensor:
  - platform: esp32evse
    esp32evse_id: evse
    state:
      name: "EVSE State (J1772)"
    device_name:
      name: "EVSE Device Name"
    device_time:
      name: "EVSE Device Time"
    wifi_sta_ssid:
      name: "EVSE Wi-Fi SSID"
    wifi_sta_ip:
      name: "EVSE Wi-Fi IP"
    wifi_sta_mac:
      name: "EVSE Wi-Fi MAC"
    chip:
      name: "EVSE MCU"
    build_time:
      name: "EVSE Build Time"
    version:
      name: "EVSE Firmware Version"
    idf_version:
      name: "EVSE IDF Version"
```

## Customization tips

- Rename entities to match your automation platform naming convention.
- Adjust number ranges to match the electrical limits of your installation.
- Remove sections you do not need to reduce resource usage on the device.

### Using generic AT subscriptions from YAML

The component exposes helper methods so you can trigger `AT+SUB` / `AT+UNSUB`
commands directly from ESPHome lambdas. This allows custom subscriptions beyond
ESPHome's built-in update period. Check out the [AT Commands documentation](https://github.com/dzurikmiroslav/esp32-evse/wiki/AT-commands)
for details

```yaml
    on_press:
      - lambda: |-
          id(evse).at_sub("\"+EMETERPOWER\"", 1000);

    on_press:
      - lambda: |-
          id(evse).at_unsub("\"+EMETERPOWER\"");
```

Passing an empty string to `at_unsub()` sends `AT+UNSUB=""`,
which clears every active subscription:

```yaml
    on_press:
      - lambda: |-
          id(evse).at_unsub("");
```


