"""Switch platform for the ESP32 EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import ICON_FLASH

from . import ESP32EVSEComponent
from .const import CONF_CHARGING_SWITCH

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")

ESP32EVSEChargingSwitch = esp32_evse_ns.class_(
    "ESP32EVSEChargingSwitch", switch.Switch, cg.Parented.template(ESP32EVSEComponent)
)

SWITCHES_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_CHARGING_SWITCH): switch.switch_schema(ESP32EVSEChargingSwitch).extend(
            {cv.Optional("icon", default=ICON_FLASH): cv.icon},
        )
    }
)


async def setup_switches(var: cg.Pvariable, config: dict | None) -> None:
    if not config:
        return

    if CONF_CHARGING_SWITCH in config:
        sw_config = config[CONF_CHARGING_SWITCH]
        sw = await switch.new_switch(sw_config)
        cg.add(var.set_charging_switch(sw))

