import esphome.codegen as cg
from esphome.components import switch
import esphome.config_validation as cv
from esphome.const import ENTITY_CATEGORY_CONFIG

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEEnableSwitch = esp32evse_ns.class_("ESP32EVSEEnableSwitch", switch.Switch)
ESP32EVSEAvailableSwitch = esp32evse_ns.class_("ESP32EVSEAvailableSwitch", switch.Switch)
ESP32EVSERequestAuthorizationSwitch = esp32evse_ns.class_(
    "ESP32EVSERequestAuthorizationSwitch", switch.Switch
)

CONF_ENABLE = "enable"
CONF_AVAILABLE = "available"
CONF_REQUEST_AUTHORIZATION = "request_authorization"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_ENABLE): switch.switch_schema(
                ESP32EVSEEnableSwitch,
                icon="mdi:power-plug-battery-outline",
            ),
            cv.Optional(CONF_AVAILABLE): switch.switch_schema(
                ESP32EVSEAvailableSwitch,
                icon="mdi:fuel-cell",
                entity_category=ENTITY_CATEGORY_CONFIG,
            ),
            cv.Optional(CONF_REQUEST_AUTHORIZATION): switch.switch_schema(
                ESP32EVSERequestAuthorizationSwitch,
                icon="mdi:hand-back-left-outline",
                entity_category=ENTITY_CATEGORY_CONFIG,
            ),
        }
    ),
    cv.has_at_least_one_key(CONF_ENABLE, CONF_AVAILABLE, CONF_REQUEST_AUTHORIZATION),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if enable_config := config.get(CONF_ENABLE):
        sw = await switch.new_switch(enable_config)
        await cg.register_parented(sw, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_enable_switch(sw))
    if available_config := config.get(CONF_AVAILABLE):
        sw = await switch.new_switch(available_config)
        await cg.register_parented(sw, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_available_switch(sw))
    if req_auth_config := config.get(CONF_REQUEST_AUTHORIZATION):
        sw = await switch.new_switch(req_auth_config)
        await cg.register_parented(sw, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_request_authorization_switch(sw))
