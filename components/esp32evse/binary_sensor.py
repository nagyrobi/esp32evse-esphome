"""Configuration helpers for the ESP32 EVSE binary sensors.

Each section below explains what kind of binary sensor is exposed to ESPHome
and why we forward the data from the EVSE controller to user-facing dashboards.
"""

# Import the code generation helpers used to hook the sensors into the C++
# component class.
import esphome.codegen as cg
# Import the platform specific helpers that create and register binary sensors.
from esphome.components import binary_sensor
# Use ESPHome's validation helpers to make sure optional configuration blocks
# are well formed before compiling the firmware.
import esphome.config_validation as cv
from esphome.const import (
    DEVICE_CLASS_CONNECTIVITY,
    DEVICE_CLASS_PROBLEM,
    ENTITY_CATEGORY_DIAGNOSTIC,
    CONF_TRIGGER_ON_INITIAL_STATE,
)

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

# Define thin C++ wrappers for the binary sensors.  They allow the main
# component to update the sensor state directly from C++ callbacks.
ESP32EVSEPendingAuthorizationBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEPendingAuthorizationBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSEWifiConnectedBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEWifiConnectedBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSEChargingLimitReachedBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEChargingLimitReachedBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSEPilotFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEPilotFaultBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSEDiodeShortBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEDiodeShortBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSELockFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSELockFaultBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSEUnlockFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSEUnlockFaultBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSERCMTriggeredBinarySensor = esp32evse_ns.class_(
    "ESP32EVSERCMTriggeredBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSERCMSelfTestFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSERCMSelfTestFaultBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSETemperatureHighFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSETemperatureHighFaultBinarySensor", binary_sensor.BinarySensor
)
ESP32EVSETemperatureFaultBinarySensor = esp32evse_ns.class_(
    "ESP32EVSETemperatureFaultBinarySensor", binary_sensor.BinarySensor
)

CONF_PENDING_AUTHORIZATION = "pending_authorization"
CONF_WIFI_CONNECTED = "wifi_connected"
CONF_CHARGING_LIMIT_REACHED = "charging_limit_reached"
CONF_PILOT_FAULT = "pilot_fault"
CONF_DIODE_SHORT = "diode_short"
CONF_LOCK_FAULT = "lock_fault"
CONF_UNLOCK_FAULT = "unlock_fault"
CONF_RCM_TRIGGERED = "rcm_triggered_fault"
CONF_RCM_SELF_TEST_FAULT = "rcm_self_test_fault"
CONF_TEMPERATURE_HIGH_FAULT = "temperature_high_fault"
CONF_TEMPERATURE_FAULT = "temperature_fault"


def _with_default_trigger(config: dict) -> dict:
    """Ensure binary sensors trigger automations on their initial state."""

    if CONF_TRIGGER_ON_INITIAL_STATE in config:
        return config
    # Copy to avoid mutating the validated configuration that ESPHome stores.
    return {**config, CONF_TRIGGER_ON_INITIAL_STATE: True}


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            # Link every sensor back to the parent component instance so they
            # can receive state updates from the EVSE UART driver.
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            # Expose whether the EVSE is waiting for an authorization step.
            cv.Optional(CONF_PENDING_AUTHORIZATION): binary_sensor.binary_sensor_schema(
                ESP32EVSEPendingAuthorizationBinarySensor,
                icon="mdi:hand-extended",
            ),
            # Report the Wi-Fi connectivity status of the charger to aid in
            # diagnostics when connectivity issues arise.
            cv.Optional(CONF_WIFI_CONNECTED): binary_sensor.binary_sensor_schema(
                ESP32EVSEWifiConnectedBinarySensor,
                device_class=DEVICE_CLASS_CONNECTIVITY,
                icon="mdi:check-network-outline",
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            # Indicate when the EVSE has finished supplying the energy corresponding 
            # to the configured charging limit.
            cv.Optional(CONF_CHARGING_LIMIT_REACHED): binary_sensor.binary_sensor_schema(
                ESP32EVSEChargingLimitReachedBinarySensor,
                icon="mdi:battery-check-outline",
            ),
            cv.Optional(CONF_PILOT_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSEPilotFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_DIODE_SHORT): binary_sensor.binary_sensor_schema(
                ESP32EVSEDiodeShortBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_LOCK_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSELockFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_UNLOCK_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSEUnlockFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_RCM_TRIGGERED): binary_sensor.binary_sensor_schema(
                ESP32EVSERCMTriggeredBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_RCM_SELF_TEST_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSERCMSelfTestFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_TEMPERATURE_HIGH_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSETemperatureHighFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_TEMPERATURE_FAULT): binary_sensor.binary_sensor_schema(
                ESP32EVSETemperatureFaultBinarySensor,
                device_class=DEVICE_CLASS_PROBLEM,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
        }
    ),
    # Require that at least one sensor is configured to avoid creating empty
    # YAML blocks that would do nothing.
    cv.has_at_least_one_key(
        CONF_PENDING_AUTHORIZATION,
        CONF_WIFI_CONNECTED,
        CONF_CHARGING_LIMIT_REACHED,
        CONF_PILOT_FAULT,
        CONF_DIODE_SHORT,
        CONF_LOCK_FAULT,
        CONF_UNLOCK_FAULT,
        CONF_RCM_TRIGGERED,
        CONF_RCM_SELF_TEST_FAULT,
        CONF_TEMPERATURE_HIGH_FAULT,
        CONF_TEMPERATURE_FAULT,
    ),
)


async def to_code(config):
    """Create the configured binary sensors and attach them to the component."""

    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if pending_config := config.get(CONF_PENDING_AUTHORIZATION):
        # The pending-authorization flag is updated whenever the EVSE expects a
        # user action (such as tapping an RFID card), so we forward its state.
        sens = await binary_sensor.new_binary_sensor(
            _with_default_trigger(pending_config)
        )
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_pending_authorization_binary_sensor(sens))
    if wifi_config := config.get(CONF_WIFI_CONNECTED):
        # Track Wi-Fi connectivity so operators can detect when the charger
        # falls offline without looking at the controller's web UI.
        sens = await binary_sensor.new_binary_sensor(
            _with_default_trigger(wifi_config)
        )
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_wifi_connected_binary_sensor(sens))
    if limit_config := config.get(CONF_CHARGING_LIMIT_REACHED):
        # Surface the flag that signals when the EVSE stopped charging because a
        # configured limit (time/energy/under-power) has been reached.
        sens = await binary_sensor.new_binary_sensor(
            _with_default_trigger(limit_config)
        )
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_charging_limit_reached_binary_sensor(sens))
    for key, setter in (
        (CONF_PILOT_FAULT, parent.set_pilot_fault_binary_sensor),
        (CONF_DIODE_SHORT, parent.set_diode_short_binary_sensor),
        (CONF_LOCK_FAULT, parent.set_lock_fault_binary_sensor),
        (CONF_UNLOCK_FAULT, parent.set_unlock_fault_binary_sensor),
        (CONF_RCM_TRIGGERED, parent.set_rcm_triggered_binary_sensor),
        (CONF_RCM_SELF_TEST_FAULT, parent.set_rcm_self_test_fault_binary_sensor),
        (CONF_TEMPERATURE_HIGH_FAULT, parent.set_temperature_high_fault_binary_sensor),
        (CONF_TEMPERATURE_FAULT, parent.set_temperature_fault_binary_sensor),
    ):
        if sensor_config := config.get(key):
            sens = await binary_sensor.new_binary_sensor(
                _with_default_trigger(sensor_config)
            )
            await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
            cg.add(setter(sens))
