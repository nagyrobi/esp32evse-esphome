"""Core registration helpers for the ESP32 EVSE custom component.

This module wires the ESPHome code generation (``codegen``) hooks for the
component so that the rest of the integration can register their entities
against a strongly-typed C++ implementation.  The inline comments below explain
why each block exists and how it fits within ESPHome's build pipeline.
"""

# Bring in the ESPHome code generation helpers so we can describe the C++ class
# hierarchy that backs the component at compile time.
import esphome.automation as automation
import esphome.codegen as cg
# Provide validation utilities to make sure user supplied YAML configuration is
# structurally correct before we attempt to generate any C++ code.
import esphome.config_validation as cv
# The component communicates via UART, therefore we need to import and require
# the UART helpers to bind the C++ object to ESPHome's UART subsystem.
from esphome.components import uart
from esphome.const import CONF_ID, CONF_UPDATE_INTERVAL

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
# Automation helpers exposed by this integration.
ESP32EVSEManagedSubscriptionAction = esp32evse_ns.class_(
    "ESP32EVSEManagedSubscriptionAction",
    automation.Action,
    cg.Parented.template(ESP32EVSEComponent),
)
ESP32EVSEUnsubscribeAllAction = esp32evse_ns.class_(
    "ESP32EVSEUnsubscribeAllAction",
    automation.Action,
    cg.Parented.template(ESP32EVSEComponent),
)

CONF_ESP32EVSE_ID = "esp32evse_id"

MIN_UPDATE_INTERVAL_MS = 10_000
MAX_UPDATE_INTERVAL_MS = 600_000

CONF_PERIOD = "period"

_REGISTERED_COMPONENT_IDS = []


def _normalize_subscription_period(value):
    """Accept integers (milliseconds) or config-time durations."""

    if isinstance(value, cv.Lambda):
        return value
    if isinstance(value, cv.TimePeriod):
        if getattr(value, "is_never", False):
            return value
        total_ms = getattr(value, "total_milliseconds", None)
        if total_ms == 0:
            raise cv.Invalid("period must be greater than 0; use 'never' to unsubscribe")
        return value
    if isinstance(value, str) and value.strip().lower() == "never":
        return "never"
    if isinstance(value, int):
        value = cv.uint32_t(value)
        if value == 0:
            raise cv.Invalid("period must be greater than 0; use 'never' to unsubscribe")
        return cv.TimePeriod(milliseconds=value)
    if isinstance(value, float):
        raise cv.Invalid("period must be specified as whole milliseconds")
    period = cv.positive_time_period_milliseconds(value)
    if isinstance(period, cv.TimePeriod):
        total_ms = getattr(period, "total_milliseconds", None)
        if total_ms == 0 and not getattr(period, "is_never", False):
            raise cv.Invalid("period must be greater than 0; use 'never' to unsubscribe")
    return period


def _resolve_parent_id(config):
    component_id = config.get(CONF_ESP32EVSE_ID)
    if component_id is not None:
        return component_id
    if len(_REGISTERED_COMPONENT_IDS) == 1:
        return _REGISTERED_COMPONENT_IDS[0]
    raise cv.Invalid(
        "esp32evse_id must be specified when multiple ESP32 EVSE components are configured"
    )


def _validate_unsubscribe_all_config(value):
    if value is None:
        value = {}
    elif not isinstance(value, dict):
        value = {CONF_ESP32EVSE_ID: value}
    return cv.Schema({cv.Optional(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent)})(value)


def _clamp_update_interval(config):
    """Ensure ``update_interval`` stays within the supported range."""

    interval = config.get(CONF_UPDATE_INTERVAL)
    if interval is None:
        return config

    total_ms = interval.total_milliseconds
    if total_ms < MIN_UPDATE_INTERVAL_MS:
        raise cv.Invalid("update_interval must be at least 10s")
    if total_ms > MAX_UPDATE_INTERVAL_MS:
        raise cv.Invalid("update_interval may not exceed 10min")
    return config


def _register_component_config(config):
    component_id = config[CONF_ID]
    if component_id not in _REGISTERED_COMPONENT_IDS:
        _REGISTERED_COMPONENT_IDS.append(component_id)
    return config


# Describe what options the YAML configuration block accepts.  We enforce that
# a new C++ instance is created, that UART is configured with the required
# arguments, and that the component polls every 60 seconds by default while
# allowing users to override the interval within the supported range.
CONFIG_SCHEMA = cv.All(
    cv.Schema({cv.GenerateID(): cv.declare_id(ESP32EVSEComponent)})
    .extend(uart.UART_DEVICE_SCHEMA)
    .extend(cv.polling_component_schema("60000ms")),
    _register_component_config,
    _clamp_update_interval,
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
    if config[CONF_ID] not in _REGISTERED_COMPONENT_IDS:
        _REGISTERED_COMPONENT_IDS.append(config[CONF_ID])


_SUBSCRIPTION_TARGETS = {
    # Text sensors
    "state": '"+STATE"',
    "chip": '"+CHIP"',
    "version": '"+VER"',
    "idf_version": '"+IDFVER"',
    "build_time": '"+BUILDTIME"',
    "device_time": '"+TIME"',
    "wifi_sta_ssid": '"+WIFISTACFG"',
    "wifi_sta_ip": '"+WIFISTAIP"',
    "wifi_sta_mac": '"+WIFISTAMAC"',
    "device_name": '"+DEVNAME"',
    # Switches
    "enable": '"+ENABLE"',
    "available": '"+AVAILABLE"',
    "request_authorization": '"+REQAUTH"',
    "three_phase_meter": '"+EMETERTHREEPHASE"',
    # Sensors
    "temperature": '"+TEMP"',
    "emeter_power": '"+EMETERPOWER"',
    "emeter_session_time": '"+EMETERSESTIME"',
    "emeter_charging_time": '"+EMETERCHTIME"',
    "uptime": '"+UPTIME"',
    "heap": '"+HEAP"',
    "energy_consumption": '"+EMETERCONSUM"',
    "total_energy_consumption": '"+EMETERTOTCONSUM"',
    "voltage": '"+EMETERVOLTAGE"',
    "current": '"+EMETERCURRENT"',
    "wifi_rssi": '"+WIFISTACONN"',
    # Binary sensors
    "pending_authorization": '"+PENDAUTH"',
    "wifi_connected": '"+WIFISTACONN"',
    "charging_limit_reached": '"+LIMREACH"',
    "error": '"+ERROR"',
    # Numbers
    "charging_current": '"+CHCUR"',
    "default_charging_current": '"+DEFCHCUR"',
    "maximum_charging_current": '"+MAXCHCUR"',
    "consumption_limit": '"+CONSUMLIM"',
    "default_consumption_limit": '"+DEFCONSUMLIM"',
    "charging_time_limit": '"+CHTIMELIM"',
    "default_charging_time_limit": '"+DEFCHTIMELIM"',
    "under_power_limit": '"+UNDERPOWERLIM"',
    "default_under_power_limit": '"+DEFUNDERPOWERLIM"',
}

_SUBSCRIPTION_SCHEMA = automation.maybe_conf(
    CONF_PERIOD,
    cv.Schema(
        {
            cv.Optional(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Required(CONF_PERIOD): cv.templatable(_normalize_subscription_period),
        }
    ),
)


def _register_subscription_action(name: str, command: str) -> None:
    """Expose an ``esp32evse.<entity>.subscribe`` automation action."""

    @automation.register_action(
        f"esp32evse.{name}.subscribe",
        ESP32EVSEManagedSubscriptionAction,
        _SUBSCRIPTION_SCHEMA,
    )
    async def subscription_action_to_code(config, action_id, template_arg, args, *, _command=command):
        component_id = _resolve_parent_id(config)
        var = cg.new_Pvariable(action_id, template_arg)
        await cg.register_parented(var, component_id)
        cg.add(var.set_command(_command))
        period_config = config[CONF_PERIOD]
        if isinstance(period_config, str):
            period = cg.uint32(0)
        elif isinstance(period_config, cv.TimePeriod):
            if getattr(period_config, "is_never", False):
                period = cg.uint32(0)
            else:
                period = cg.uint32(period_config.total_milliseconds)
        else:
            period = await cg.templatable(period_config, args, cg.uint32)
        cg.add(var.set_period(period))
        return var


for _name, _command in _SUBSCRIPTION_TARGETS.items():
    _register_subscription_action(_name, _command)


@automation.register_action(
    "esp32evse.unsubscribe_all",
    ESP32EVSEUnsubscribeAllAction,
    _validate_unsubscribe_all_config,
)
async def unsubscribe_all_to_code(config, action_id, template_arg, args):
    component_id = _resolve_parent_id(config)
    var = cg.new_Pvariable(action_id, template_arg)
    await cg.register_parented(var, component_id)
    return var
