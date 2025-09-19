"""Integration entry point for the ESP32-based EVSE external component."""

from __future__ import annotations

import esphome.codegen as cg
import esphome.config_validation as cv
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UPDATE_INTERVAL

from .const import (
    CONF_BUTTONS,
    CONF_NUMBERS,
    CONF_SENSORS,
    CONF_SWITCHES,
    CONF_TEXT_SENSORS,
    DEFAULT_UPDATE_INTERVAL,
)

esp32_evse_ns = cg.esphome_ns.namespace("esp32_evse")
ESP32EVSEComponent = esp32_evse_ns.class_(
    "ESP32EVSEComponent",
    cg.PollingComponent,
    uart.UARTDevice,
)

AUTO_LOAD = ["sensor", "text_sensor", "number", "switch", "button"]
DEPENDENCIES = ["uart"]


def _platform_options(schema_map: dict[str, cv.Schema]) -> dict:
    """Convert the platform schema mapping to optional configuration keys."""

    return {cv.Optional(key, default={}): value for key, value in schema_map.items()}


# The platform helper modules import the component class, so load them lazily
# after the namespace has been declared.
from . import button as button_config  # noqa: E402
from . import number as number_config  # noqa: E402
from . import sensor as sensor_config  # noqa: E402
from . import switch as switch_config  # noqa: E402
from . import text_sensor as text_sensor_config  # noqa: E402

_PLATFORM_SCHEMAS = {
    CONF_SENSORS: sensor_config.SENSORS_SCHEMA,
    CONF_TEXT_SENSORS: text_sensor_config.TEXT_SENSORS_SCHEMA,
    CONF_SWITCHES: switch_config.SWITCHES_SCHEMA,
    CONF_BUTTONS: button_config.BUTTONS_SCHEMA,
    CONF_NUMBERS: number_config.NUMBERS_SCHEMA,
}

CONFIG_SCHEMA = (
    cv.Schema({cv.GenerateID(): cv.declare_id(ESP32EVSEComponent)})
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(
        {
            cv.Optional(CONF_UPDATE_INTERVAL, default=DEFAULT_UPDATE_INTERVAL): cv.update_interval,
            **_platform_options(_PLATFORM_SCHEMAS),
        }
    )
)


async def to_code(config: dict) -> None:
    """Generate the C++ component object graph for the EVSE integration."""

    var = cg.new_Pvariable(config[CONF_ID])
    await cg.register_component(var, config)
    await uart.register_uart_device(var, config)

    cg.add(var.set_update_interval(config[CONF_UPDATE_INTERVAL]))

    await sensor_config.setup_sensors(var, config.get(CONF_SENSORS))
    await text_sensor_config.setup_text_sensors(var, config.get(CONF_TEXT_SENSORS))
    await switch_config.setup_switches(var, config.get(CONF_SWITCHES))
    await button_config.setup_buttons(var, config.get(CONF_BUTTONS))
    await number_config.setup_numbers(var, config.get(CONF_NUMBERS))
