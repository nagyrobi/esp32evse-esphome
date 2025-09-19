"""Number platform for the ESP32 EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number

from .const import CONF_CURRENT_LIMIT

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEComponent = esp32_evse_ns.class_("ESP32EVSEComponent")
ESP32EVSECurrentLimitNumber = esp32_evse_ns.class_(
    "ESP32EVSECurrentLimitNumber", number.Number, cg.Parented(ESP32EVSEComponent)
)

NUMBERS_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_CURRENT_LIMIT): number.number_schema(
            ESP32EVSECurrentLimitNumber,
            unit_of_measurement="A",
            min_value=6.0,
            max_value=32.0,
            step=1.0,
            mode=number.NUMBER_MODE_SLIDER,
        )
    }
)


async def setup_numbers(var: cg.Pvariable, config: dict | None) -> None:
    if not config:
        return

    if CONF_CURRENT_LIMIT in config:
        num = await number.new_number(config[CONF_CURRENT_LIMIT])
        cg.add(var.set_current_limit_number(num))

