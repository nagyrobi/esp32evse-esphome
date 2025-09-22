import esphome.codegen as cg
from esphome.components import text_sensor
import esphome.config_validation as cv

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent

DEPENDENCIES = ["esp32evse"]

CONF_STATE = "state"


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Required(CONF_STATE): text_sensor.text_sensor_schema(icon="mdi:ev-station"),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    state_config = config[CONF_STATE]
    sens = await text_sensor.new_text_sensor(state_config)
    cg.add(parent.set_state_text_sensor(sens))
