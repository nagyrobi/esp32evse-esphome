import esphome.codegen as cg
from esphome.components import binary_sensor
import esphome.config_validation as cv
from esphome.const import DEVICE_CLASS_CONNECTIVITY, ENTITY_CATEGORY_DIAGNOSTIC

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

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
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_PENDING_AUTHORIZATION): binary_sensor.binary_sensor_schema(
                ESP32EVSEPendingAuthorizationBinarySensor,
                icon="mdi:clipboard-clock",
            ),
            cv.Optional(CONF_WIFI_CONNECTED): binary_sensor.binary_sensor_schema(
                ESP32EVSEWifiConnectedBinarySensor,
                device_class=DEVICE_CLASS_CONNECTIVITY,
                icon="mdi:wifi-check",
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
        }
    ),
    cv.has_at_least_one_key(CONF_PENDING_AUTHORIZATION, CONF_WIFI_CONNECTED),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if pending_config := config.get(CONF_PENDING_AUTHORIZATION):
        sens = await binary_sensor.new_binary_sensor(pending_config)
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_pending_authorization_binary_sensor(sens))
    if wifi_config := config.get(CONF_WIFI_CONNECTED):
        sens = await binary_sensor.new_binary_sensor(wifi_config)
        await cg.register_parented(sens, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_wifi_connected_binary_sensor(sens))
