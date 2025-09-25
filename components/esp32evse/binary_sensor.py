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
from esphome.const import DEVICE_CLASS_CONNECTIVITY, ENTITY_CATEGORY_DIAGNOSTIC

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

CONF_PENDING_AUTHORIZATION = "pending_authorization"
CONF_WIFI_CONNECTED = "wifi_connected"


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
        }
    ),
    # Require that at least one sensor is configured to avoid creating empty
    # YAML blocks that would do nothing.
    cv.has_at_least_one_key(CONF_PENDING_AUTHORIZATION, CONF_WIFI_CONNECTED),
)


async def to_code(config):
    """Create the configured binary sensors and attach them to the component."""

    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if pending_config := config.get(CONF_PENDING_AUTHORIZATION):
        # The pending-authorization flag is updated whenever the EVSE expects a
        # user action (such as tapping an RFID card), so we forward its state.
        sens = await binary_sensor.new_binary_sensor(pending_config)
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_pending_authorization_binary_sensor(sens))
    if wifi_config := config.get(CONF_WIFI_CONNECTED):
        # Track Wi-Fi connectivity so operators can detect when the charger
        # falls offline without looking at the controller's web UI.
        sens = await binary_sensor.new_binary_sensor(wifi_config)
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_wifi_connected_binary_sensor(sens))
