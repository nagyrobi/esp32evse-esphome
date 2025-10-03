# ESP32-EVSE ESPHome Integration

This repository provides an [ESPHome](https://esphome.io/) custom component that exposes the most important control features of the [ESP32-EVSE](https://github.com/dzurikmiroslav/esp32-evse) charging controller. 
It's mainly intended to be used in a custom [HMI screen based on ESPHome and LVGL](https://github.com/nagyrobi/esp32-evse_esphome-lvgl).

It implements the communication with ESP32-EVSE using [AT Commands](https://github.com/dzurikmiroslav/esp32-evse/wiki/AT-commands).

Why would you complement ESP32-EVSE with another ESP32 running ESPHome? You can extend its functionality independently, increasing flexibility:
- make HMI/graphical UI rendered via LVGL, on an ESP32-based screen, with fully open source resources (no proprietary editor needed)
- optinally connect to Home Assistant via native API (or MQTT to other systems), exposing the EVSE as a bunch of sensors and controls
- implement any custom authorization like RFiD readers etc.
- multiple UARTs can be configured (eg one talking to `esp32-evse`, other talking to smart meter etc), make own Dynamic Load Management through HA or other ESPHome components (eg use data from other meters in various ways; freely implement DLM logic either in HA or in ESPHome)
- can use free GPIOs or the display for anything else
- has Bluetooth and with it you could pair with your car and implement additional related features (eg open charging flap automatically, poll battery status, temperature; garage door control etc, which wouldn't have to interfere with EVSE board at all)
- the EVSE not having to deal with any of the above, can keep working independently as a mission critical piece of hardware

## Requirements

You need an ESP32-based display or board supported by ESPHome. The component communicates with ESP32-EVSE (min. version 2.0.0) via UART at 115200 baud rate. Check out the [HMI screen based on ESPHome and LVGL](https://github.com/nagyrobi/esp32-evse_esphome-lvgl) repository for example hardware configurations.
.
Enter your ESP32-EVSE web UI and in _Settings_ > _Serial_, select for the UART port _Mode_: _AT Commands_. _Baud rate_: _115200_,  _Data bits_: _8_,  _Stop bits_: _1_, _Parity_: _Disable_. 
Press Submit and reboot the evse from  _System_ > _Restart_.

If you use the [esp32s2-evse-d-a board](https://github.com/dzurikmiroslav/esp32-evse/wiki/ESP32-S2-DA) you can use a 4-pin cable with 2.5mm JST wired correctly for RX/TX/GND/5V:

| ESP32-EVSE S2 DA U6 UART (2.5mm JST) |
| -------- |
| 1: GND |
| 2: TX |
| 3: RX |
| 4: +5V |

Use cable as short as possible.

Configure the UART as per ESPHome docs, and instantiate the EVSE component and link it to the configured UART bus:

```yaml
uart:
  id: evse_uart
  tx_pin: GPIOXX
  rx_pin: GPIOXX
  baud_rate: 921600 
  stop_bits: 1
  parity: NONE

esp32evse:
  id: evse
  uart_id: evse_uart
  update_interval: 60s # Optional: adjust how often the component polls the charger (10s–10min), defaults to 60s.
```
## Entities exposed

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
    uptime:
      name: "EVSE Uptime"
```
If your installation only uses a single temperature sensor, expose it via the combined ``temperature`` key instead of the individual high/low entries:

```yaml
    temperature:
      name: "EVSE Temperature"
```

The optional ``uptime`` sensor surfaces how long the EVSE firmware has been running since the last reboot, which is useful for
diagnostics and correlating watchdog resets.

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
    three_phase_meter:
      name: "EVSE Three-Phase Meter"
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
    charging_limit_reached:
      name: "EVSE Charging Limit Reached"
```

The ``charging_limit_reached`` binary sensor turns on when the EVSE stopped charging because a configured limit (time, energy, or
under-power) was met, allowing automations to react immediately.

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
- Use ``internal: true`` for fast updating sensors (voltage and current) you might not need in the Home Automation system to avoid database overload.
- Adjust the ``maximum_charging_current`` to match the electrical limits of your installation (eg. add ``max_value: 32`` parameter if you have 32A breakers installed).
- Omit the entities you don't want to use, to reduce resource usage on the device.

## Auto-updating entities

ESP32-EVSE is able to periodically push values without waiting for query commands. 

The component exposes dedicated automation actions that wrap the `AT+SUB`
and `AT+UNSUB` commands. Check out the
[AT Commands documentation](https://github.com/dzurikmiroslav/esp32-evse/wiki/AT-commands)
for details.

**Example:** To subscribe the ``emeter_power`` sensor to push updates every second (use any
valid [ESPHome time](https://esphome.io/guides/configuration-types/#config-time)
bigger than ``100ms``):

```yaml
    on_...:
      - esp32evse.emeter_power.subscribe: 1s
```

Provide ``never`` to stop receiving updates for the same entity:

```yaml
    on_...:
      - esp32evse.emeter_power.subscribe: never
```

And use ``esp32evse.unsubscribe_all`` to clear every active subscription in one
shot (add ``esp32evse_id: <id>`` if you host multiple EVSE components):

```yaml
    on_...:
      - esp32evse.unsubscribe_all:
```

**Note:** A few subscription actions control multiple sensors because the EVSE
reports them together. For example, ``esp32evse.temperature.subscribe`` drives
both ``temperature_high`` and ``temperature_low``, ``esp32evse.heap.subscribe``
updates ``heap_used`` and ``heap_total``, and the ``esp32evse.voltage.subscribe`` and
``esp32evse.current.subscribe`` actions publish all phase-specific measurements.

Subscriptions are also available for the new entities: ``esp32evse.uptime.subscribe``
queries or follows the EVSE uptime, while ``esp32evse.charging_limit_reached.subscribe``
tracks push notifications when a charging limit trips.


