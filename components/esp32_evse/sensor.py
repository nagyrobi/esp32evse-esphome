"""Sensor definitions for the ESP32 EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import sensor
from esphome.const import (
    CONF_CURRENT,
    CONF_ENERGY,
    CONF_TEMPERATURE,
    CONF_VOLTAGE,
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL_INCREASING,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_KILOWATT_HOURS,
    UNIT_VOLT,
)

SENSOR_DESCRIPTIONS = {
    CONF_VOLTAGE: sensor.sensor_schema(
        unit_of_measurement=UNIT_VOLT,
        accuracy_decimals=1,
        device_class=DEVICE_CLASS_VOLTAGE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    CONF_CURRENT: sensor.sensor_schema(
        unit_of_measurement=UNIT_AMPERE,
        accuracy_decimals=2,
        device_class=DEVICE_CLASS_CURRENT,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
    CONF_ENERGY: sensor.sensor_schema(
        unit_of_measurement=UNIT_KILOWATT_HOURS,
        accuracy_decimals=3,
        device_class=DEVICE_CLASS_ENERGY,
        state_class=STATE_CLASS_TOTAL_INCREASING,
    ),
    CONF_TEMPERATURE: sensor.sensor_schema(
        unit_of_measurement=UNIT_CELSIUS,
        accuracy_decimals=1,
        device_class=DEVICE_CLASS_TEMPERATURE,
        state_class=STATE_CLASS_MEASUREMENT,
    ),
}

SENSORS_SCHEMA = cv.Schema({cv.Optional(key): value for key, value in SENSOR_DESCRIPTIONS.items()})


async def setup_sensors(var: cg.Pvariable, config: dict | None) -> None:
    if not config:
        return

    for key, schema in SENSOR_DESCRIPTIONS.items():
        if key not in config:
            continue
        sens = await sensor.new_sensor(config[key])
        cg.add(getattr(var, f"set_{key}_sensor")(sens))

