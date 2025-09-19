"""Button platform for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import CONF_TYPE, ICON_RESTART

from . import ESP32EVSEComponent
from .const import CONF_ESP32_EVSE_ID, CONF_RESET_BUTTON

DEPENDENCIES = ["esp32_evse"]

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEResetButton = esp32_evse_ns.class_(
    "ESP32EVSEResetButton", button.Button, cg.Parented(ESP32EVSEComponent)
)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32_EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Optional(CONF_TYPE, default=CONF_RESET_BUTTON): cv.one_of(
            CONF_RESET_BUTTON, lower=True
        ),
    }
).extend(button.button_schema(ESP32EVSEResetButton, icon=ICON_RESTART))


async def to_code(config: dict) -> None:
    parent = await cg.get_variable(config[CONF_ESP32_EVSE_ID])
    btn = await button.new_button(config)
    cg.add(btn.set_parent(parent))
    cg.add(parent.set_reset_button(btn))
