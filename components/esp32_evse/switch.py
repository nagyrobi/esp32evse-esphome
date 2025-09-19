"""Switch platform for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import CONF_TYPE, ICON_FLASH

from . import ESP32EVSEComponent
from .const import CONF_CHARGING_SWITCH, CONF_ESP32_EVSE_ID

DEPENDENCIES = ["esp32_evse"]

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEChargingSwitch = esp32_evse_ns.class_(
    "ESP32EVSEChargingSwitch", switch.Switch, cg.Parented(ESP32EVSEComponent)
)


CONFIG_SCHEMA = cv.Schema(
    {
        cv.GenerateID(CONF_ESP32_EVSE_ID): cv.use_id(ESP32EVSEComponent),
        cv.Optional(CONF_TYPE, default=CONF_CHARGING_SWITCH): cv.one_of(
            CONF_CHARGING_SWITCH, lower=True
        ),
    }
).extend(switch.switch_schema(ESP32EVSEChargingSwitch, icon=ICON_FLASH))


async def to_code(config: dict) -> None:
    parent = await cg.get_variable(config[CONF_ESP32_EVSE_ID])
    sw = await switch.new_switch(config)
    cg.add(sw.set_parent(parent))
    cg.add(parent.set_charging_switch(sw))
