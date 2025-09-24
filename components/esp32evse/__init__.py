import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID

AUTO_LOAD = ["uart"]
DEPENDENCIES = ["uart"]
CODEOWNERS = ["@dzurikmiroslav"]

esp32evse_ns = cg.esphome_ns.namespace("esp32evse")
ESP32EVSEComponent = esp32evse_ns.class_(
    "ESP32EVSEComponent", cg.PollingComponent, uart.UARTDevice
)

CONF_ESP32EVSE_ID = "esp32evse_id"

CONFIG_SCHEMA = cv.All(
    cv.Schema({cv.GenerateID(): cv.declare_id(ESP32EVSEComponent)})
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.polling_component_schema("60000ms"))
)

FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "esp32evse", require_tx=True, require_rx=True
)


async def to_code(config):
    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)
