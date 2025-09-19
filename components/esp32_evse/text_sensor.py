"""Text sensor platform for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor
from esphome.const import CONF_TYPE

from . import ESP32EVSEComponent
from .const import CONF_CHARGING_STATE, CONF_ESP32_EVSE_ID, TEXT_SENSOR_DEFAULTS

DEPENDENCIES = ["esp32_evse"]

TEXT_SENSOR_TYPES: dict[str, str] = {
    CONF_CHARGING_STATE: "set_charging_state_text_sensor",
}


def _apply_text_sensor_defaults(config: dict) -> dict:
    sensor_type = config[CONF_TYPE]
    defaults = TEXT_SENSOR_DEFAULTS.get(sensor_type, {})
    for key, value in defaults.items():
        config.setdefault(key, value)
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32_EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_TYPE, default=CONF_CHARGING_STATE): cv.one_of(
                *TEXT_SENSOR_TYPES.keys(), lower=True
            ),
        }
    ).extend(text_sensor.text_sensor_schema()),
    _apply_text_sensor_defaults,
)


async def to_code(config: dict) -> None:
    parent = await cg.get_variable(config[CONF_ESP32_EVSE_ID])
    setter = TEXT_SENSOR_TYPES[config[CONF_TYPE]]
    sens = await text_sensor.new_text_sensor(config)
    cg.add(getattr(parent, setter)(sens))
