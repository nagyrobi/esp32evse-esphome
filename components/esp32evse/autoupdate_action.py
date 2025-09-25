"""Automation helpers for ESP32 EVSE subscription updates."""

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome import automation
from esphome.components import binary_sensor, number, sensor, switch, text_sensor
from esphome.const import CONF_ID, CONF_PERIOD

from . import (
    ESP32EVSEAutoUpdateAction,
    get_autoupdate_target,
)


def _autoupdate_target_id(value):
    """Allow referencing any ESP32 EVSE entity that supports subscriptions."""

    validators = [
        cv.use_id(text_sensor.TextSensor),
        cv.use_id(sensor.Sensor),
        cv.use_id(switch.Switch),
        cv.use_id(binary_sensor.BinarySensor),
        cv.use_id(number.Number),
    ]
    for validator in validators:
        try:
            return validator(value)
        except cv.Invalid:
            continue
    raise cv.Invalid("ID must reference an ESP32 EVSE text sensor, sensor, switch, number, or binary sensor")


AUTOUPDATE_ACTION_SCHEMA = cv.Schema(
    {
        cv.Required(CONF_ID): _autoupdate_target_id,
        cv.Required(CONF_PERIOD): cv.templatable(cv.uint32_t),
    }
)


@automation.register_action("esp32evse.autoupdate", ESP32EVSEAutoUpdateAction, AUTOUPDATE_ACTION_SCHEMA)
async def esp32evse_autoupdate_to_code(config, action_id, template_arg, args):
    target = await cg.get_variable(config[CONF_ID])
    mapping = get_autoupdate_target(target)
    if mapping is None:
        raise cv.Invalid(
            "The referenced entity does not belong to the ESP32 EVSE component or does not expose an AT command"
        )
    parent, command = mapping
    var = cg.new_Pvariable(action_id, template_arg, parent)
    cg.add(var.set_command(command))
    period = await cg.templatable(config[CONF_PERIOD], args, cg.uint32)
    cg.add(var.set_period(period))
    return var
