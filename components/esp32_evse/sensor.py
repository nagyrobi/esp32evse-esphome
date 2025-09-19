"""Sensor platform configuration for the ESP32 EVSE component."""

from __future__ import annotations

from dataclasses import dataclass
from typing import Callable

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

from . import ESP32EVSEComponent


@dataclass(frozen=True)
class _SensorDescriptor:
    key: str
    schema: Callable[[], sensor.SensorSchema]
    setter: str


_SENSOR_DESCRIPTORS = (
    _SensorDescriptor(
        key=CONF_VOLTAGE,
        schema=lambda: sensor.sensor_schema(
            unit_of_measurement=UNIT_VOLT,
            accuracy_decimals=1,
            device_class=DEVICE_CLASS_VOLTAGE,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        setter="set_voltage_sensor",
    ),
    _SensorDescriptor(
        key=CONF_CURRENT,
        schema=lambda: sensor.sensor_schema(
            unit_of_measurement=UNIT_AMPERE,
            accuracy_decimals=2,
            device_class=DEVICE_CLASS_CURRENT,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        setter="set_current_sensor",
    ),
    _SensorDescriptor(
        key=CONF_ENERGY,
        schema=lambda: sensor.sensor_schema(
            unit_of_measurement=UNIT_KILOWATT_HOURS,
            accuracy_decimals=3,
            device_class=DEVICE_CLASS_ENERGY,
            state_class=STATE_CLASS_TOTAL_INCREASING,
        ),
        setter="set_energy_sensor",
    ),
    _SensorDescriptor(
        key=CONF_TEMPERATURE,
        schema=lambda: sensor.sensor_schema(
            unit_of_measurement=UNIT_CELSIUS,
            accuracy_decimals=1,
            device_class=DEVICE_CLASS_TEMPERATURE,
            state_class=STATE_CLASS_MEASUREMENT,
        ),
        setter="set_temperature_sensor",
    ),
)

SENSORS_SCHEMA = cv.Schema(
    {
        cv.Optional(descriptor.key): descriptor.schema()
        for descriptor in _SENSOR_DESCRIPTORS
    }
)


async def setup_sensors(parent: ESP32EVSEComponent, config: dict | None) -> None:
    """Attach configured sensors to the native component."""

    if not config:
        return

    for descriptor in _SENSOR_DESCRIPTORS:
        if descriptor.key not in config:
            continue
        sens = await sensor.new_sensor(config[descriptor.key])
        cg.add(getattr(parent, descriptor.setter)(sens))
