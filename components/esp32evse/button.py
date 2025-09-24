import esphome.codegen as cg
from esphome.components import button
import esphome.config_validation as cv

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEFastSubscribeButton = esp32evse_ns.class_(
    "ESP32EVSEFastSubscribeButton", button.Button
)
ESP32EVSEFastUnsubscribeButton = esp32evse_ns.class_(
    "ESP32EVSEFastUnsubscribeButton", button.Button
)

CONF_FAST_SUBSCRIBE = "fast_power_subscribe"
CONF_FAST_UNSUBSCRIBE = "fast_power_unsubscribe"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_FAST_SUBSCRIBE): button.button_schema(
                ESP32EVSEFastSubscribeButton,
                icon="mdi:speedometer",
            ),
            cv.Optional(CONF_FAST_UNSUBSCRIBE): button.button_schema(
                ESP32EVSEFastUnsubscribeButton,
                icon="mdi:speedometer-slow",
            ),
        }
    ),
    cv.has_at_least_one_key(CONF_FAST_SUBSCRIBE, CONF_FAST_UNSUBSCRIBE),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if subscribe_config := config.get(CONF_FAST_SUBSCRIBE):
        btn = await button.new_button(subscribe_config)
        await cg.register_parented(btn, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_fast_subscribe_button(btn))
    if unsubscribe_config := config.get(CONF_FAST_UNSUBSCRIBE):
        btn = await button.new_button(unsubscribe_config)
        await cg.register_parented(btn, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_fast_unsubscribe_button(btn))
