"""Sensor platform for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import CONF_TYPE

from . import ESP32EVSEComponent
from .const import (
    CONF_CURRENT,
    CONF_ENERGY,
    CONF_ESP32_EVSE_ID,
    CONF_TEMPERATURE,
    CONF_VOLTAGE,
    SENSOR_DEFAULTS,
)

DEPENDENCIES = ["esp32_evse"]

SENSOR_TYPES: dict[str, str] = {
    CONF_VOLTAGE: "set_voltage_sensor",
    CONF_CURRENT: "set_current_sensor",
    CONF_ENERGY: "set_energy_sensor",
    CONF_TEMPERATURE: "set_temperature_sensor",
}


def _apply_sensor_defaults(config: dict) -> dict:
    sensor_type = config[CONF_TYPE]
    defaults = SENSOR_DEFAULTS.get(sensor_type, {})
    for key, value in defaults.items():
        config.setdefault(key, value)
    return config


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32_EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Required(CONF_TYPE): cv.one_of(*SENSOR_TYPES.keys(), lower=True),
        }
    ).extend(sensor.sensor_schema()),
    _apply_sensor_defaults,
)


async def to_code(config: dict) -> None:
    parent = await cg.get_variable(config[CONF_ESP32_EVSE_ID])
    setter = SENSOR_TYPES[config[CONF_TYPE]]
    sens = await sensor.new_sensor(config)
    cg.add(getattr(parent, setter)(sens))
