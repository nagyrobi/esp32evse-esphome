import inspect

import esphome.codegen as cg
from esphome.components import number
import esphome.config_validation as cv

from esphome.const import CONF_MAX_VALUE, CONF_MIN_VALUE, CONF_STEP, UNIT_AMPERE

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEChargingCurrentNumber = esp32evse_ns.class_(
    "ESP32EVSEChargingCurrentNumber", number.Number
)

CONF_CHARGING_CURRENT = "charging_current"


_NUMBER_SCHEMA_KWARGS = {
    "icon": "mdi:current-ac",
    "unit_of_measurement": UNIT_AMPERE,
}

if "min_value" in inspect.signature(number.number_schema).parameters:
    _NUMBER_SCHEMA_KWARGS.update(
        {
            "min_value": 6.0,
            "max_value": 63.0,
            "step": 0.1,
        }
    )


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Required(CONF_CHARGING_CURRENT): number.number_schema(
            ESP32EVSEChargingCurrentNumber,
            **_NUMBER_SCHEMA_KWARGS,
        ).extend(
            {
                cv.Optional(CONF_MIN_VALUE, default=6.0): cv.float_,
                cv.Optional(CONF_MAX_VALUE, default=63.0): cv.float_,
                cv.Optional(CONF_STEP, default=0.1): cv.positive_float,
            }
        ),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])
    charging_current_cfg = config[CONF_CHARGING_CURRENT]
    num = await number.new_number(
        charging_current_cfg,
        min_value=charging_current_cfg[CONF_MIN_VALUE],
        max_value=charging_current_cfg[CONF_MAX_VALUE],
        step=charging_current_cfg[CONF_STEP],
    )
    await cg.register_parented(num, config[CONF_ESP32EVSE_ID])
    cg.add(parent.set_charging_current_number(num))
