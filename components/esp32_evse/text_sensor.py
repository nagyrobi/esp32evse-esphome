"""Text sensor support for the ESP32 EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import text_sensor

from .const import CONF_CHARGING_STATE

TEXT_SENSORS_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_CHARGING_STATE): text_sensor.text_sensor_schema(),
    }
)


async def setup_text_sensors(var: cg.Pvariable, config: dict | None) -> None:
    if not config:
        return

    if CONF_CHARGING_STATE in config:
        sens = await text_sensor.new_text_sensor(config[CONF_CHARGING_STATE])
        cg.add(var.set_charging_state_text_sensor(sens))

