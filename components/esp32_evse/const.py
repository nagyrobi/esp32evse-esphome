"""Shared constants for the ESP32 EVSE external component."""

from esphome.const import (
    CONF_CURRENT,
    CONF_ENERGY,
    CONF_ID,
    CONF_TEMPERATURE,
    CONF_UPDATE_INTERVAL,
    CONF_VOLTAGE,
)

CONF_CHARGING_STATE = "charging_state"
CONF_CHARGING_SWITCH = "charging"
CONF_RESET_BUTTON = "reset"
CONF_CURRENT_LIMIT = "current_limit"

DEFAULT_UPDATE_INTERVAL = "15s"
# Mapping between configuration keys and the EVSE AT query commands.
SENSOR_QUERIES = {
    CONF_CHARGING_STATE: "AT+STATE?",
    CONF_VOLTAGE: "AT+VOLT?",
    CONF_CURRENT: "AT+CURR?",
    CONF_ENERGY: "AT+ENER?",
    CONF_TEMPERATURE: "AT+TEMP?",
}

# Mapping between configuration keys and EVSE control commands.
COMMAND_START_CHARGING = "AT+START"
COMMAND_STOP_CHARGING = "AT+STOP"
COMMAND_RESET = "AT+RESET"
COMMAND_SET_CURRENT_LIMIT = "AT+SETCUR"

CONF_SENSORS = "sensors"
CONF_TEXT_SENSORS = "text_sensors"
CONF_SWITCHES = "switches"
CONF_BUTTONS = "buttons"
CONF_NUMBERS = "numbers"

