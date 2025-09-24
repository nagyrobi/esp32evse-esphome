import inspect

import esphome.codegen as cg
from esphome.components import number
import esphome.config_validation as cv

from esphome.const import (
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_STEP,
    ENTITY_CATEGORY_CONFIG,
    UNIT_AMPERE,
    UNIT_SECOND,
    UNIT_WATT,
)

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEChargingCurrentNumber = esp32evse_ns.class_(
    "ESP32EVSEChargingCurrentNumber", number.Number
)

CONF_CHARGING_CURRENT = "charging_current"
CONF_DEFAULT_CHARGING_CURRENT = "default_charging_current"
CONF_MAXIMUM_CHARGING_CURRENT = "maximum_charging_current"
CONF_CONSUMPTION_LIMIT = "consumption_limit"
CONF_DEFAULT_CONSUMPTION_LIMIT = "default_consumption_limit"
CONF_CHARGING_TIME_LIMIT = "charging_time_limit"
CONF_DEFAULT_CHARGING_TIME_LIMIT = "default_charging_time_limit"
CONF_UNDER_POWER_LIMIT = "under_power_limit"
CONF_DEFAULT_UNDER_POWER_LIMIT = "default_under_power_limit"
CONF_MULTIPLIER = "multiplier"

_NUMBER_SCHEMA_SUPPORTS_LIMITS = "min_value" in inspect.signature(  # pragma: no branch
    number.number_schema
).parameters


def _build_number_schema(
    icon,
    unit,
    default_min,
    default_max,
    default_step,
    default_multiplier,
    entity_category=None,
):
    kwargs = {"icon": icon}
    if unit is not None:
        kwargs["unit_of_measurement"] = unit
    if entity_category is not None:
        kwargs["entity_category"] = entity_category
    if _NUMBER_SCHEMA_SUPPORTS_LIMITS:
        kwargs.update(
            {
                "min_value": default_min,
                "max_value": default_max,
                "step": default_step,
            }
        )
    base = number.number_schema(ESP32EVSEChargingCurrentNumber, **kwargs)
    return base.extend(
        {
            cv.Optional(CONF_MIN_VALUE, default=default_min): cv.float_,
            cv.Optional(CONF_MAX_VALUE, default=default_max): cv.float_,
            cv.Optional(CONF_STEP, default=default_step): cv.positive_float,
            cv.Optional(CONF_MULTIPLIER, default=default_multiplier): cv.positive_float,
        }
    )


_NUMBER_TYPES = {
    CONF_CHARGING_CURRENT: {
        "schema": _build_number_schema(
            icon="mdi:current-ac",
            unit=UNIT_AMPERE,
            default_min=6.0,
            default_max=63.0,
            default_step=0.1,
            default_multiplier=10.0,
        ),
        "command": "AT+CHCUR",
        "setter": "set_charging_current_number",
    },
    CONF_DEFAULT_CHARGING_CURRENT: {
        "schema": _build_number_schema(
            icon="mdi:current-ac",
            unit=UNIT_AMPERE,
            default_min=6.0,
            default_max=63.0,
            default_step=0.1,
            default_multiplier=10.0,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        "command": "AT+DEFCHCUR",
        "setter": "set_default_charging_current_number",
    },
    CONF_MAXIMUM_CHARGING_CURRENT: {
        "schema": _build_number_schema(
            icon="mdi:current-ac",
            unit=UNIT_AMPERE,
            default_min=6.0,
            default_max=63.0,
            default_step=0.1,
            default_multiplier=10.0,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        "command": "AT+MAXCHCUR",
        "setter": "set_maximum_charging_current_number",
    },
    CONF_CONSUMPTION_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:gauge",
            unit=UNIT_WATT,
            default_min=0.0,
            default_max=100000.0,
            default_step=10.0,
            default_multiplier=1.0,
        ),
        "command": "AT+CONSUMLIM",
        "setter": "set_consumption_limit_number",
    },
    CONF_DEFAULT_CONSUMPTION_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:gauge",
            unit=UNIT_WATT,
            default_min=0.0,
            default_max=100000.0,
            default_step=10.0,
            default_multiplier=1.0,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        "command": "AT+DEFCONSUMLIM",
        "setter": "set_default_consumption_limit_number",
    },
    CONF_CHARGING_TIME_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:timer-outline",
            unit=UNIT_SECOND,
            default_min=0.0,
            default_max=86400.0,
            default_step=60.0,
            default_multiplier=1.0,
        ),
        "command": "AT+CHTIMELIM",
        "setter": "set_charging_time_limit_number",
    },
    CONF_DEFAULT_CHARGING_TIME_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:timer-outline",
            unit=UNIT_SECOND,
            default_min=0.0,
            default_max=86400.0,
            default_step=60.0,
            default_multiplier=1.0,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        "command": "AT+DEFCHTIMELIM",
        "setter": "set_default_charging_time_limit_number",
    },
    CONF_UNDER_POWER_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:flash-outline",
            unit=UNIT_WATT,
            default_min=0.0,
            default_max=100000.0,
            default_step=10.0,
            default_multiplier=1.0,
        ),
        "command": "AT+UNDERPOWERLIM",
        "setter": "set_under_power_limit_number",
    },
    CONF_DEFAULT_UNDER_POWER_LIMIT: {
        "schema": _build_number_schema(
            icon="mdi:flash-outline",
            unit=UNIT_WATT,
            default_min=0.0,
            default_max=100000.0,
            default_step=10.0,
            default_multiplier=1.0,
            entity_category=ENTITY_CATEGORY_CONFIG,
        ),
        "command": "AT+DEFUNDERPOWERLIM",
        "setter": "set_default_under_power_limit_number",
    },
}


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            **{
                cv.Optional(key): meta["schema"] for key, meta in _NUMBER_TYPES.items()
            },
        }
    ),
    cv.has_at_least_one_key(*_NUMBER_TYPES.keys()),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])
    for key, meta in _NUMBER_TYPES.items():
        if key not in config:
            continue
        number_config = config[key]
        num = await number.new_number(
            number_config,
            min_value=number_config[CONF_MIN_VALUE],
            max_value=number_config[CONF_MAX_VALUE],
            step=number_config[CONF_STEP],
        )
        await cg.register_parented(num, config[CONF_ESP32EVSE_ID])
        cg.add(num.set_command(meta["command"]))
        cg.add(num.set_multiplier(number_config[CONF_MULTIPLIER]))
        cg.add(getattr(parent, meta["setter"])(num))
