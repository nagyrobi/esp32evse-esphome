"""Core registration helpers for the ESP32 EVSE custom component.

This module wires the ESPHome code generation (``codegen``) hooks for the
component so that the rest of the integration can register their entities
against a strongly-typed C++ implementation.  The inline comments below explain
why each block exists and how it fits within ESPHome's build pipeline.
"""

# Bring in the ESPHome code generation helpers so we can describe the C++ class
# hierarchy that backs the component at compile time.
import esphome.codegen as cg
# Provide validation utilities to make sure user supplied YAML configuration is
# structurally correct before we attempt to generate any C++ code.
import esphome.config_validation as cv
# The component communicates via UART, therefore we need to import and require
# the UART helpers to bind the C++ object to ESPHome's UART subsystem.
from esphome.components import uart
from esphome.const import CONF_ID

# Make sure UART gets compiled alongside our component because we depend on it
# both at configuration time and at runtime on the microcontroller.
AUTO_LOAD = ["uart"]
DEPENDENCIES = ["uart"]
# Document the maintainer so users know who to reach out to for reviews.
CODEOWNERS = ["@nagyrobi"]

esp32evse_ns = cg.esphome_ns.namespace("esp32evse")
# Declare the C++ class that implements the logic.  It inherits from
# ``PollingComponent`` so ESPHome regularly calls ``update`` and from
# ``UARTDevice`` so it can talk to the EVSE controller over serial.
ESP32EVSEComponent = esp32evse_ns.class_(
    "ESP32EVSEComponent", cg.PollingComponent, uart.UARTDevice
)

CONF_ESP32EVSE_ID = "esp32evse_id"

# Describe what options the YAML configuration block accepts.  We enforce that
# a new C++ instance is created, that UART is configured with the required
# arguments, and that the component polls every 60 seconds by default.
CONFIG_SCHEMA = cv.All(
    cv.Schema({cv.GenerateID(): cv.declare_id(ESP32EVSEComponent)})
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.polling_component_schema("60000ms"))
)

# Perform a final check after parsing so the build fails fast if the user
# forgot to wire the UART RX/TX pins—communication would not work otherwise.
FINAL_VALIDATE_SCHEMA = uart.final_validate_device_schema(
    "esp32evse", require_tx=True, require_rx=True
)


async def to_code(config):
    """Translate the validated YAML configuration into C++ code.

    We allocate a new component instance, register it with ESPHome's scheduler,
    and then hook it into the UART subsystem so runtime calls reach the EVSE.
    """

    # Create the backing C++ object and keep track of it so other modules can
    # look it up when they need to register sensors, buttons, etc.
    var = cg.new_Pvariable(config[CONF_ID])
    # Ensure ESPHome schedules ``setup``/``loop``/``update`` callbacks for the
    # component by registering it as a polling component.
    await cg.register_component(var, config)
    # Finally, bind the component to the configured UART bus so serial
    # communication with the EVSE controller is possible.
    await uart.register_uart_device(var, config)
