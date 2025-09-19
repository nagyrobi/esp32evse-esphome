"""Number platform for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.const import CONF_TYPE

from . import ESP32EVSEComponent
from .const import CONF_CURRENT_LIMIT, CONF_ESP32_EVSE_ID

DEPENDENCIES = ["esp32_evse"]

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSECurrentLimitNumber = esp32_evse_ns.class_(
    "ESP32EVSECurrentLimitNumber", number.Number, cg.Parented(ESP32EVSEComponent)
)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32_EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Optional(CONF_TYPE, default=CONF_CURRENT_LIMIT): cv.one_of(
            CONF_CURRENT_LIMIT, lower=True
        ),
    }
).extend(
    number.number_schema(
        ESP32EVSECurrentLimitNumber,
        unit_of_measurement="A",
        min_value=6.0,
        max_value=32.0,
        step=1.0,
        mode=number.NUMBER_MODE_SLIDER,
    )
)


async def to_code(config: dict) -> None:
    parent = await cg.get_variable(config[CONF_ESP32_EVSE_ID])
    num = await number.new_number(config)
    cg.add(num.set_parent(parent))
    cg.add(parent.set_current_limit_number(num))
