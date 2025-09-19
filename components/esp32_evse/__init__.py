"""Code generation helpers for the ESP32 EVSE external component."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UPDATE_INTERVAL

from .const import DEFAULT_UPDATE_INTERVAL

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
        {cv.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.update_interval}
    )
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))
