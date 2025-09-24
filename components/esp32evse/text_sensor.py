import esphome.codegen as cg
from esphome.components import text_sensor
import esphome.config_validation as cv
from esphome.const import EntityCategory

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent

DEPENDENCIES = ["esp32evse"]

CONF_STATE = "state"
CONF_CHIP = "chip"
CONF_VERSION = "version"
CONF_IDF_VERSION = "idf_version"
CONF_BUILD_TIME = "build_time"
CONF_DEVICE_TIME = "device_time"
CONF_WIFI_STA_SSID = "wifi_sta_ssid"
CONF_WIFI_STA_IP = "wifi_sta_ip"
CONF_WIFI_STA_MAC = "wifi_sta_mac"
CONF_DEVICE_NAME = "device_name"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_STATE): text_sensor.text_sensor_schema(icon="mdi:ev-station"),
            cv.Optional(CONF_CHIP): text_sensor.text_sensor_schema(
                icon="mdi:chip", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_VERSION): text_sensor.text_sensor_schema(
                icon="mdi:tag", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_IDF_VERSION): text_sensor.text_sensor_schema(
                icon="mdi:alpha-i-circle", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_BUILD_TIME): text_sensor.text_sensor_schema(
                icon="mdi:clock-outline", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_DEVICE_TIME): text_sensor.text_sensor_schema(
                icon="mdi:clock", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_WIFI_STA_SSID): text_sensor.text_sensor_schema(
                icon="mdi:wifi", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_WIFI_STA_IP): text_sensor.text_sensor_schema(
                icon="mdi:ip", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_WIFI_STA_MAC): text_sensor.text_sensor_schema(
                icon="mdi:lan", entity_category=EntityCategory.DIAGNOSTIC
            ),
            cv.Optional(CONF_DEVICE_NAME): text_sensor.text_sensor_schema(
                icon="mdi:rename-box", entity_category=EntityCategory.DIAGNOSTIC
            ),
        }
    ),
    cv.has_at_least_one_key(
        CONF_STATE,
        CONF_CHIP,
        CONF_VERSION,
        CONF_IDF_VERSION,
        CONF_BUILD_TIME,
        CONF_DEVICE_TIME,
        CONF_WIFI_STA_SSID,
        CONF_WIFI_STA_IP,
        CONF_WIFI_STA_MAC,
        CONF_DEVICE_NAME,
    ),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if state_config := config.get(CONF_STATE):
        sens = await text_sensor.new_text_sensor(state_config)
        cg.add(parent.set_state_text_sensor(sens))
    if chip_config := config.get(CONF_CHIP):
        sens = await text_sensor.new_text_sensor(chip_config)
        cg.add(parent.set_chip_text_sensor(sens))
    if version_config := config.get(CONF_VERSION):
        sens = await text_sensor.new_text_sensor(version_config)
        cg.add(parent.set_version_text_sensor(sens))
    if idf_version_config := config.get(CONF_IDF_VERSION):
        sens = await text_sensor.new_text_sensor(idf_version_config)
        cg.add(parent.set_idf_version_text_sensor(sens))
    if build_time_config := config.get(CONF_BUILD_TIME):
        sens = await text_sensor.new_text_sensor(build_time_config)
        cg.add(parent.set_build_time_text_sensor(sens))
    if device_time_config := config.get(CONF_DEVICE_TIME):
        sens = await text_sensor.new_text_sensor(device_time_config)
        cg.add(parent.set_device_time_text_sensor(sens))
    if wifi_ssid_config := config.get(CONF_WIFI_STA_SSID):
        sens = await text_sensor.new_text_sensor(wifi_ssid_config)
        cg.add(parent.set_wifi_sta_ssid_text_sensor(sens))
    if wifi_ip_config := config.get(CONF_WIFI_STA_IP):
        sens = await text_sensor.new_text_sensor(wifi_ip_config)
        cg.add(parent.set_wifi_sta_ip_text_sensor(sens))
    if wifi_mac_config := config.get(CONF_WIFI_STA_MAC):
        sens = await text_sensor.new_text_sensor(wifi_mac_config)
        cg.add(parent.set_wifi_sta_mac_text_sensor(sens))
    if device_name_config := config.get(CONF_DEVICE_NAME):
        sens = await text_sensor.new_text_sensor(device_name_config)
        cg.add(parent.set_device_name_text_sensor(sens))
