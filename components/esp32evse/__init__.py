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
from esphome import automation
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
ESP32EVSEAutoUpdateAction = esp32evse_ns.class_(
    "ESP32EVSEAutoUpdateAction", automation.Action
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


_AUTOUPDATE_REGISTRY = {}


def _registry_key(obj):
    """Return a stable dictionary key for ESPHome IDs and generated objects."""

    if obj is None:
        return None
    # ``cv.use_id`` objects expose their identifier via ``.id`` while the
    # generated ESPHome mock objects have the attribute tucked under ``.id.id``.
    candidate = getattr(obj, "id", obj)
    candidate = getattr(candidate, "id", candidate)
    if isinstance(candidate, str):
        return candidate
    return None


def _normalize_subscription_target(command):
    """Convert an AT command into the corresponding subscription token."""

    if command is None:
        return None
    command = str(command).strip()
    if not command:
        return None
    if command.startswith("\"") and command.endswith("\"") and len(command) >= 2:
        command = command[1:-1]
    if command.startswith("AT"):
        command = command[2:]
    command = command.lstrip()
    if command.endswith("?"):
        command = command[:-1]
    if not command:
        return None
    if not command.startswith("+"):
        command = "+" + command.lstrip("+")
    return command


def register_autoupdate_target(component, entity, command):
    """Remember which AT command keeps *entity* in sync via AT+SUB."""

    target = _normalize_subscription_target(command)
    if target is None:
        return
    # ``entity`` is a ``cg.Pvariable`` instance during normal code generation
    # but ESPHome swaps in a lightweight ``MockObj`` during configuration
    # validation.  ``MockObj`` intentionally disables ``__hash__`` so that it
    # behaves like a regular Python object, which means we cannot use it as a
    # dictionary key directly.  Instead, stash the registration against the
    # object's identity.  ``id()`` is stable for the lifetime of the object and
    # works for both the mock placeholders and the final ``Expression``
    # instances created during code generation.
    # Keep track of the mapping both by object identity (useful while ESPHome is
    # still generating C++ code) and by the underlying ``id`` string so that
    # later lookups performed via ``cv.use_id`` succeed regardless of which
    # representation is used.
    _AUTOUPDATE_REGISTRY[id(entity)] = (component, target)
    key = _registry_key(getattr(entity, "_id", None))
    if key is not None:
        _AUTOUPDATE_REGISTRY[key] = (component, target)


def get_autoupdate_target(entity):
    """Return the component/command pair for the given entity, if registered."""

    key = _registry_key(entity)
    if key is not None and key in _AUTOUPDATE_REGISTRY:
        return _AUTOUPDATE_REGISTRY[key]
    return _AUTOUPDATE_REGISTRY.get(id(entity))


# Register automation helpers that depend on the symbols defined above.
from . import autoupdate_action  # noqa: E402,F401
