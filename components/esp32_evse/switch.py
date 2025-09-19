"""Switch platform bindings for the ESP32 EVSE component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import switch
from esphome.const import ICON_FLASH

from . import ESP32EVSEComponent
from .const import CONF_CHARGING_SWITCH

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEChargingSwitch = esp32_evse_ns.class_(
    "ESP32EVSEChargingSwitch",
    switch.Switch,
    cg.Parented.template(ESP32EVSEComponent),
)

SWITCHES_SCHEMA = cv.Schema(
    {
        cv.Optional(CONF_CHARGING_SWITCH): switch.switch_schema(
            ESP32EVSEChargingSwitch,
            icon=ICON_FLASH,
        )
    }
)


async def setup_switches(parent: ESP32EVSEComponent, config: dict | None) -> None:
    """Attach the EVSE charging control switch."""

    if not config or CONF_CHARGING_SWITCH not in config:
        return

    sw = await switch.new_switch(config[CONF_CHARGING_SWITCH])
    cg.add(parent.set_charging_switch(sw))
