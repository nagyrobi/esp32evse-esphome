"""Code generation helpers for the ESP32 EVSE external component."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UPDATE_INTERVAL

from . import sensor as sensor_config
from . import text_sensor as text_sensor_config
from . import switch as switch_config
from . import button as button_config
from . import number as number_config
from .const import (
    CONF_BUTTONS,
    CONF_NUMBERS,
    CONF_SENSORS,
    CONF_SWITCHES,
    CONF_TEXT_SENSORS,
    DEFAULT_UPDATE_INTERVAL,
)

AUTO_LOAD = ["sensor", "text_sensor", "number", "switch", "button"]
DEPENDENCIES = ["uart"]

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEComponent = esp32_evse_ns.class_(
    "ESP32EVSEComponent", cg.PollingComponent, uart.UARTDevice
)

CONFIG_SCHEMA = (
    cv.Schema({cv.GenerateID(): cv.declare_id(ESP32EVSEComponent)})
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(
        {
            cv.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.update_interval,
            cv.Optional(CONF_SENSORS, default={}): sensor_config.SENSORS_SCHEMA,
            cv.Optional(CONF_TEXT_SENSORS, default={}): text_sensor_config.TEXT_SENSORS_SCHEMA,
            cv.Optional(CONF_SWITCHES, default={}): switch_config.SWITCHES_SCHEMA,
            cv.Optional(CONF_BUTTONS, default={}): button_config.BUTTONS_SCHEMA,
            cv.Optional(CONF_NUMBERS, default={}): number_config.NUMBERS_SCHEMA,
        }
    )
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))

    await sensor_config.setup_sensors(var, config.get(CONF_SENSORS))
    await text_sensor_config.setup_text_sensors(var, config.get(CONF_TEXT_SENSORS))
    await switch_config.setup_switches(var, config.get(CONF_SWITCHES))
    await button_config.setup_buttons(var, config.get(CONF_BUTTONS))
    await number_config.setup_numbers(var, config.get(CONF_NUMBERS))
