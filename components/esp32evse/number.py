"""Define the numeric entities used to configure the EVSE controller."""

import inspect

# Import ESPHome helpers that let us express configuration-time behaviour in
# Python while generating strongly typed C++ code.
import esphome.codegen as cg
from esphome.components import number
import esphome.config_validation as cv

from esphome.const import (
    CONF_MAX_VALUE,
    CONF_MIN_VALUE,
    CONF_STEP,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    ENTITY_CATEGORY_CONFIG,
    UNIT_AMPERE,
    UNIT_HOUR,
    UNIT_KILOWATT,
)

try:
    from esphome.const import UNIT_KILOWATT_HOUR
except ImportError:  # pragma: no cover - compatibility with older ESPHome releases
    from esphome.const import UNIT_KILOWATT_HOURS as UNIT_KILOWATT_HOUR

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

# A single C++ class implements all the different numeric entities.  Behaviour
# differences (command name, ranges, etc.) are controlled via metadata below.
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
    device_class=None,
):
    """Create a sensor schema and defaults tailored to a specific EVSE command."""

    kwargs = {"icon": icon}
    if unit is not None:
        kwargs["unit_of_measurement"] = unit
    if entity_category is not None:
        kwargs["entity_category"] = entity_category
    if device_class is not None:
        kwargs["device_class"] = device_class
    if _NUMBER_SCHEMA_SUPPORTS_LIMITS:
        kwargs.update(
            {
                "min_value": default_min,
                "max_value": default_max,
                "step": default_step,
            }
        )
    base = number.number_schema(ESP32EVSEChargingCurrentNumber, **kwargs)
    schema = base.extend(
        {
            cv.Optional(CONF_MIN_VALUE): cv.float_,
            cv.Optional(CONF_MAX_VALUE): cv.float_,
            cv.Optional(CONF_STEP): cv.positive_float,
            cv.Optional(CONF_MULTIPLIER): cv.positive_float,
        }
    )
    defaults = {
        CONF_MIN_VALUE: default_min,
        CONF_MAX_VALUE: default_max,
        CONF_STEP: default_step,
        CONF_MULTIPLIER: default_multiplier,
    }
    return schema, defaults


def _make_number_type(*, command, setter, **kwargs):
    """Bundle together the metadata required to expose an EVSE number entity."""

    schema, defaults = _build_number_schema(**kwargs)
    return {"schema": schema, "defaults": defaults, "command": command, "setter": setter}


# Metadata describing how each YAML key maps to an EVSE command, including
# presentation defaults and which setter on the C++ class should receive the
# resulting entity.
_NUMBER_TYPES = {
    CONF_CHARGING_CURRENT: _make_number_type(
        icon="mdi:current-ac",
        unit=UNIT_AMPERE,
        default_min=6.0,
        default_max=63.0,
        default_step=0.1,
        default_multiplier=10.0,
        command="AT+CHCUR",
        setter="set_charging_current_number",
    ),
    CONF_DEFAULT_CHARGING_CURRENT: _make_number_type(
        icon="mdi:current-ac",
        unit=UNIT_AMPERE,
        default_min=6.0,
        default_max=63.0,
        default_step=0.1,
        default_multiplier=10.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command="AT+DEFCHCUR",
        setter="set_default_charging_current_number",
    ),
    CONF_MAXIMUM_CHARGING_CURRENT: _make_number_type(
        icon="mdi:current-ac",
        unit=UNIT_AMPERE,
        default_min=6.0,
        default_max=63.0,
        default_step=1.0,
        default_multiplier=1.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command="AT+MAXCHCUR",
        setter="set_maximum_charging_current_number",
    ),
    CONF_CONSUMPTION_LIMIT: _make_number_type(
        icon="mdi:gauge",
        unit=UNIT_KILOWATT_HOUR,
        default_min=0.0,
        default_max=80.0,
        default_step=0.1,
        default_multiplier=1000.0,
        device_class=DEVICE_CLASS_ENERGY,
        command="AT+CONSUMLIM",
        setter="set_consumption_limit_number",
    ),
    CONF_DEFAULT_CONSUMPTION_LIMIT: _make_number_type(
        icon="mdi:gauge",
        unit=UNIT_KILOWATT_HOUR,
        default_min=0.0,
        default_max=80.0,
        default_step=0.1,
        default_multiplier=1000.0,
        device_class=DEVICE_CLASS_ENERGY,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command="AT+DEFCONSUMLIM",
        setter="set_default_consumption_limit_number",
    ),
    CONF_CHARGING_TIME_LIMIT: _make_number_type(
        icon="mdi:timer-outline",
        unit=UNIT_HOUR,
        default_min=0.0,
        default_max=24.0,
        default_step=0.5,
        default_multiplier=3600.0,
        command="AT+CHTIMELIM",
        setter="set_charging_time_limit_number",
    ),
    CONF_DEFAULT_CHARGING_TIME_LIMIT: _make_number_type(
        icon="mdi:timer-outline",
        unit=UNIT_HOUR,
        default_min=0.0,
        default_max=24.0,
        default_step=0.5,
        default_multiplier=3600.0,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command="AT+DEFCHTIMELIM",
        setter="set_default_charging_time_limit_number",
    ),
    CONF_UNDER_POWER_LIMIT: _make_number_type(
        icon="mdi:flash-outline",
        unit=UNIT_KILOWATT,
        default_min=0.0,
        default_max=10.0,
        default_step=0.1,
        default_multiplier=1000.0,
        device_class=DEVICE_CLASS_POWER,
        command="AT+UNDERPOWERLIM",
        setter="set_under_power_limit_number",
    ),
    CONF_DEFAULT_UNDER_POWER_LIMIT: _make_number_type(
        icon="mdi:flash-outline",
        unit=UNIT_KILOWATT,
        default_min=0.0,
        default_max=10.0,
        default_step=0.1,
        default_multiplier=1000.0,
        device_class=DEVICE_CLASS_POWER,
        entity_category=ENTITY_CATEGORY_CONFIG,
        command="AT+DEFUNDERPOWERLIM",
        setter="set_default_under_power_limit_number",
    ),
}


# Build a dynamic schema that exposes optional YAML blocks for every supported
# EVSE number while insisting that at least one is defined.
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
    """Create each configured number entity and associate it with the EVSE."""

    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])
    for key, meta in _NUMBER_TYPES.items():
        if key not in config:
            continue
        number_config = config[key]
        defaults = meta["defaults"]
        min_value = number_config.get(CONF_MIN_VALUE, defaults[CONF_MIN_VALUE])
        max_value = number_config.get(CONF_MAX_VALUE, defaults[CONF_MAX_VALUE])
        step = number_config.get(CONF_STEP, defaults[CONF_STEP])
        # Generate the number entity stub and feed in the user-provided range
        # overrides so the UI matches the EVSE firmware limits.
        num = await number.new_number(
            number_config,
            min_value=min_value,
            max_value=max_value,
            step=step,
        )
        await cg.register_parented(num, config[CONF_ESP32EVSE_ID])
        # Remember which AT command updates the EVSE when this entity changes.
        cg.add(num.set_command(meta["command"]))
        multiplier = number_config.get(CONF_MULTIPLIER, defaults[CONF_MULTIPLIER])
        # Some EVSE commands expect scaled integers (for example tenths of an
        # ampere).  The multiplier keeps the ESPHome API user friendly while
        # still speaking the correct serial protocol.
        cg.add(num.set_multiplier(multiplier))
        cg.add(getattr(parent, meta["setter"])(num))
