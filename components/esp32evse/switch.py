import esphome.codegen as cg
from esphome.components import switch
import esphome.config_validation as cv

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEEnableSwitch = esp32evse_ns.class_("ESP32EVSEEnableSwitch", switch.Switch)

CONF_ENABLE = "enable"


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Required(CONF_ENABLE): switch.switch_schema(
            ESP32EVSEEnableSwitch,
            icon="mdi:toggle-switch",
        ),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    enable_config = config[CONF_ENABLE]
    sw = await switch.new_switch(enable_config)
    await cg.register_parented(sw, config[CONF_ESP32EVSE_ID])
    cg.add(parent.set_enable_switch(sw))
