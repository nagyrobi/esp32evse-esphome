# ESP32 EVSE External Component for ESPHome

This repository provides an ESPHome external component that integrates the ESP32-based EVSE controller using its AT command interface. The component communicates over UART to expose real-time telemetry and control primitives inside ESPHome automations.

## Features

- UART-based polling of the EVSE's AT command set.
- Sensors for supply voltage, charging current, delivered energy and internal temperature.
- Text sensor for the EVSE charging state (Ready, Charging, Fault, etc.).
- Switch, button and number entities that wrap the start/stop, reset and current-limit commands with acknowledgement handling.
- Configurable polling interval and optional inclusion of individual entities to match the EVSE hardware capabilities.

## Repository Layout

```
components/
└── esp32_evse/
    ├── __init__.py
    ├── button.py
    ├── const.py
    ├── esp32_evse.cpp
    ├── esp32_evse.h
    ├── number.py
    ├── sensor.py
    ├── switch.py
    └── text_sensor.py
```

## Usage

1. Clone or copy this repository into your ESPHome `custom_components` directory (for example `config/custom_components/esp32_evse`).
2. Include the external component in your ESPHome configuration and configure the UART port connected to the EVSE controller.
3. Create sensor/text sensor/switch/button/number entries using the ``platform: esp32_evse`` integration to expose the telemetry and controls you need, referencing the component with ``esp32_evse_id``.

### Example ESPHome Configuration

```yaml
external_components:
  - source: github://your-user/esp32evse-esphome

uart:
  id: evse_uart
  tx_pin: GPIO17
  rx_pin: GPIO16
  baud_rate: 115200
  stop_bits: 1
  parity: NONE

esp32_evse:
  id: evse
  uart_id: evse_uart
  update_interval: 10s

sensor:
  - platform: esp32_evse
    esp32_evse_id: evse
    type: voltage
    name: EVSE Line Voltage
  - platform: esp32_evse
    esp32_evse_id: evse
    type: current
    name: EVSE Charging Current
  - platform: esp32_evse
    esp32_evse_id: evse
    type: energy
    name: EVSE Delivered Energy
  - platform: esp32_evse
    esp32_evse_id: evse
    type: temperature
    name: EVSE Controller Temperature

text_sensor:
  - platform: esp32_evse
    esp32_evse_id: evse
    name: EVSE Charging State

switch:
  - platform: esp32_evse
    esp32_evse_id: evse
    name: EVSE Charging Enable

button:
  - platform: esp32_evse
    esp32_evse_id: evse
    name: EVSE Reset

number:
  - platform: esp32_evse
    esp32_evse_id: evse
    name: EVSE Current Limit
    min_value: 6
    max_value: 32
    step: 1
```

## AT Command Coverage

The component issues the following EVSE AT commands during normal operation:

| Command | Purpose |
| ------- | ------- |
| `AT` | Presence check during setup. |
| `AT+STATE?` | Updates the charging state text sensor. |
| `AT+VOLT?` | Provides the line voltage sensor value. |
| `AT+CURR?` | Provides the charging current sensor value. |
| `AT+ENER?` | Provides the delivered energy sensor value. |
| `AT+TEMP?` | Provides the controller temperature sensor value. |
| `AT+START` / `AT+STOP` | Toggles charging through the switch entity. |
| `AT+SETCUR=<value>` | Adjusts the allowable charging current via the number entity. |
| `AT+RESET` | Invoked by the reset button to restart the EVSE controller. |

Responses are parsed into native ESPHome entities with retries and timeouts. Any `ERR` responses are logged so you can diagnose problems from the ESPHome logs. Sensor platforms accept the following `type` values: `voltage`, `current`, `energy`, and `temperature`. Additional platforms use the default type (`charging_state` for the text sensor, `charging` for the switch, `reset` for the button, and `current_limit` for the number). If your EVSE exposes additional commands you can extend the component by following the existing sensor and actuator patterns.

## Notes

- The component automatically retries failed commands twice before reporting an error.
- Unknown or malformed responses are logged and ignored to keep the ESPHome runtime stable.
- When the EVSE reports a charging state of `Charging`, `Active` or `Preparing`, the charging switch is kept in sync with the reported state.
- For best results ensure the EVSE uses matching UART settings (baud rate, parity, stop bits) to the ESPHome configuration.

