import esphome.codegen as cg
from esphome.components import number
import esphome.config_validation as cv

from esphome.const import UNIT_AMPERE

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

ESP32EVSEChargingCurrentNumber = esp32evse_ns.class_(
    "ESP32EVSEChargingCurrentNumber", number.Number
)

CONF_CHARGING_CURRENT = "charging_current"


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Required(CONF_CHARGING_CURRENT): number.number_schema(
            ESP32EVSEChargingCurrentNumber,
            icon="mdi:current-ac",
            unit_of_measurement=UNIT_AMPERE,
            min_value=6.0,
            max_value=63.0,
            step=0.1,
        ),
    }
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])
    num = await number.new_number(config[CONF_CHARGING_CURRENT])
    await cg.register_parented(num, config[CONF_ESP32EVSE_ID])
    cg.add(parent.set_charging_current_number(num))
