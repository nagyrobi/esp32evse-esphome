"""Number platform bindings for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import number
from esphome.const import CONF_MAX_VALUE, CONF_MIN_VALUE, CONF_STEP

from . import ESP32EVSEComponent
from .const import CONF_CURRENT_LIMIT

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSECurrentLimitNumber = esp32_evse_ns.class_(
    "ESP32EVSECurrentLimitNumber",
    number.Number,
    cg.Parented.template(ESP32EVSEComponent),
)

_DEFAULT_RANGE = {
    CONF_MIN_VALUE: 6.0,
    CONF_MAX_VALUE: 32.0,
    CONF_STEP: 1.0,
}


def _validate_range(config: dict) -> dict:
    if config[CONF_MIN_VALUE] >= config[CONF_MAX_VALUE]:
        raise cv.Invalid("max_value must be greater than min_value")
    return config


NUMBERS_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_CURRENT_LIMIT): cv.All(
            number.number_schema(
                ESP32EVSECurrentLimitNumber,
                unit_of_measurement="A",
            ).extend(
                {
                    cv.Optional(key, default=value): cv.float_ if key != CONF_STEP else cv.positive_float
                    for key, value in _DEFAULT_RANGE.items()
                }
            ),
            _validate_range,
        )
    }
)


async def setup_numbers(parent: ESP32EVSEComponent, config: dict | None) -> None:
    """Create and register the configurable number entities."""

    if not config or CONF_CURRENT_LIMIT not in config:
        return

    num_config = config[CONF_CURRENT_LIMIT]
    num = await number.new_number(
        num_config,
        min_value=num_config[CONF_MIN_VALUE],
        max_value=num_config[CONF_MAX_VALUE],
        step=num_config[CONF_STEP],
    )
    cg.add(num.traits.set_mode(number.NumberMode.SLIDER))
    cg.add(parent.set_current_limit_number(num))
