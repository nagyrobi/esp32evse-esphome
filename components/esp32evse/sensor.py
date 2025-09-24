import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.const import (
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_TEMPERATURE,
    ICON_FLASH,
    ICON_THERMOMETER,
    ICON_TIMER,
    STATE_CLASS_MEASUREMENT,
    UNIT_CELSIUS,
    UNIT_SECOND,
)

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent

DEPENDENCIES = ["esp32evse"]

CONF_TEMPERATURE = "temperature"
CONF_EMETER_POWER = "emeter_power"
CONF_EMETER_SESSION_TIME = "emeter_session_time"
CONF_EMETER_CHARGING_TIME = "emeter_charging_time"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=2,
            ),
            cv.Optional(CONF_EMETER_POWER): sensor.sensor_schema(
                device_class=DEVICE_CLASS_POWER,
                state_class=STATE_CLASS_MEASUREMENT,
                unit_of_measurement="W",
                icon=ICON_FLASH,
            ),
            cv.Optional(CONF_EMETER_SESSION_TIME): sensor.sensor_schema(
                unit_of_measurement=UNIT_SECOND,
                icon=ICON_TIMER,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_EMETER_CHARGING_TIME): sensor.sensor_schema(
                unit_of_measurement=UNIT_SECOND,
                icon=ICON_TIMER,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
        }
    ),
    cv.has_at_least_one_key(
        CONF_TEMPERATURE,
        CONF_EMETER_POWER,
        CONF_EMETER_SESSION_TIME,
        CONF_EMETER_CHARGING_TIME,
    ),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if temperature_config := config.get(CONF_TEMPERATURE):
        sens = await sensor.new_sensor(temperature_config)
        cg.add(parent.set_temperature_sensor(sens))
    if power_config := config.get(CONF_EMETER_POWER):
        sens = await sensor.new_sensor(power_config)
        cg.add(parent.set_emeter_power_sensor(sens))
    if session_config := config.get(CONF_EMETER_SESSION_TIME):
        sens = await sensor.new_sensor(session_config)
        cg.add(parent.set_emeter_session_time_sensor(sens))
    if charging_config := config.get(CONF_EMETER_CHARGING_TIME):
        sens = await sensor.new_sensor(charging_config)
        cg.add(parent.set_emeter_charging_time_sensor(sens))
