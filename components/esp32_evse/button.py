"""Button platform for the ESP32 EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import ICON_RESTART

from . import ESP32EVSEComponent
from .const import CONF_RESET_BUTTON

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")

ESP32EVSEResetButton = esp32_evse_ns.class_(
    "ESP32EVSEResetButton", button.Button, cg.Parented.template(ESP32EVSEComponent)
)

BUTTONS_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_RESET_BUTTON): button.button_schema(
            ESP32EVSEResetButton, icon=ICON_RESTART
        )
    }
)


async def setup_buttons(var: cg.Pvariable, config: dict | None) -> None:
    if not config:
        return

    if CONF_RESET_BUTTON in config:
        btn = await button.new_button(config[CONF_RESET_BUTTON])
        cg.add(var.set_reset_button(btn))

