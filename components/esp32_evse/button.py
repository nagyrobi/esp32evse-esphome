"""Button platform bindings for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import button
from esphome.const import ICON_RESTART

from . import ESP32EVSEComponent
from .const import CONF_RESET_BUTTON

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEResetButton = esp32_evse_ns.class_(
    "ESP32EVSEResetButton",
    button.Button,
    cg.Parented.template(ESP32EVSEComponent),
)

BUTTONS_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_RESET_BUTTON): button.button_schema(
            ESP32EVSEResetButton,
            icon=ICON_RESTART,
        )
    }
)


async def setup_buttons(parent: ESP32EVSEComponent, config: dict | None) -> None:
    """Attach the optional EVSE reset button."""

    if not config or CONF_RESET_BUTTON not in config:
        return

    btn = await button.new_button(config[CONF_RESET_BUTTON])
    cg.add(parent.set_reset_button(btn))
