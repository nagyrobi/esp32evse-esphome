import esphome.codegen as cg
from esphome.components import sensor
import esphome.config_validation as cv
from esphome.const import (
    DEVICE_CLASS_CURRENT,
    DEVICE_CLASS_ENERGY,
    DEVICE_CLASS_POWER,
    DEVICE_CLASS_SIGNAL_STRENGTH,
    DEVICE_CLASS_TEMPERATURE,
    DEVICE_CLASS_VOLTAGE,
    ENTITY_CATEGORY_DIAGNOSTIC,
    ICON_FLASH,
    ICON_THERMOMETER,
    ICON_TIMER,
    STATE_CLASS_MEASUREMENT,
    STATE_CLASS_TOTAL,
    STATE_CLASS_TOTAL_INCREASING,
    UNIT_AMPERE,
    UNIT_CELSIUS,
    UNIT_DECIBEL_MILLIWATT,
    UNIT_SECOND,
    UNIT_VOLT,
)

try:
    from esphome.const import UNIT_WATT_HOUR
except ImportError:
    from esphome.const import UNIT_WATT_HOURS as UNIT_WATT_HOUR

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent

DEPENDENCIES = ["esp32evse"]

CONF_TEMPERATURE = "temperature"
CONF_TEMPERATURE_HIGH = "temperature_high"
CONF_TEMPERATURE_LOW = "temperature_low"
CONF_EMETER_POWER = "emeter_power"
CONF_EMETER_SESSION_TIME = "emeter_session_time"
CONF_EMETER_CHARGING_TIME = "emeter_charging_time"
CONF_HEAP = "heap"
CONF_HEAP_USED = "heap_used"
CONF_HEAP_TOTAL = "heap_total"
CONF_ENERGY_CONSUMPTION = "energy_consumption"
CONF_TOTAL_ENERGY_CONSUMPTION = "total_energy_consumption"
CONF_VOLTAGE_L1 = "voltage_l1"
CONF_VOLTAGE_L2 = "voltage_l2"
CONF_VOLTAGE_L3 = "voltage_l3"
CONF_CURRENT_L1 = "current_l1"
CONF_CURRENT_L2 = "current_l2"
CONF_CURRENT_L3 = "current_l3"
CONF_WIFI_RSSI = "wifi_rssi"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            cv.Optional(CONF_TEMPERATURE_HIGH): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=2,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_TEMPERATURE_LOW): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=2,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_TEMPERATURE): sensor.sensor_schema(
                unit_of_measurement=UNIT_CELSIUS,
                icon=ICON_THERMOMETER,
                device_class=DEVICE_CLASS_TEMPERATURE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=2,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_EMETER_POWER): sensor.sensor_schema(
                device_class=DEVICE_CLASS_POWER,
                state_class=STATE_CLASS_MEASUREMENT,
                unit_of_measurement="W",
                icon=ICON_FLASH,
            ),
            cv.Optional(CONF_EMETER_SESSION_TIME): sensor.sensor_schema(
                unit_of_measurement=UNIT_SECOND,
                icon=ICON_TIMER,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_EMETER_CHARGING_TIME): sensor.sensor_schema(
                unit_of_measurement=UNIT_SECOND,
                icon=ICON_TIMER,
                state_class=STATE_CLASS_MEASUREMENT,
            ),
            cv.Optional(CONF_HEAP): sensor.sensor_schema(
                unit_of_measurement="B",
                icon="mdi:memory",
                state_class=STATE_CLASS_MEASUREMENT,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_HEAP_USED): sensor.sensor_schema(
                unit_of_measurement="B",
                icon="mdi:memory",
                state_class=STATE_CLASS_MEASUREMENT,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_HEAP_TOTAL): sensor.sensor_schema(
                unit_of_measurement="B",
                icon="mdi:memory",
                state_class=STATE_CLASS_MEASUREMENT,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_ENERGY_CONSUMPTION): sensor.sensor_schema(
                unit_of_measurement=UNIT_WATT_HOUR,
                icon="mdi:counter",
                device_class=DEVICE_CLASS_ENERGY,
                state_class=STATE_CLASS_TOTAL_INCREASING,
            ),
            cv.Optional(CONF_TOTAL_ENERGY_CONSUMPTION): sensor.sensor_schema(
                unit_of_measurement=UNIT_WATT_HOUR,
                icon="mdi:counter",
                device_class=DEVICE_CLASS_ENERGY,
                state_class=STATE_CLASS_TOTAL,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            cv.Optional(CONF_VOLTAGE_L1): sensor.sensor_schema(
                unit_of_measurement=UNIT_VOLT,
                icon="mdi:alpha-v-circle",
                device_class=DEVICE_CLASS_VOLTAGE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_VOLTAGE_L2): sensor.sensor_schema(
                unit_of_measurement=UNIT_VOLT,
                icon="mdi:alpha-v-circle",
                device_class=DEVICE_CLASS_VOLTAGE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_VOLTAGE_L3): sensor.sensor_schema(
                unit_of_measurement=UNIT_VOLT,
                icon="mdi:alpha-v-circle",
                device_class=DEVICE_CLASS_VOLTAGE,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_CURRENT_L1): sensor.sensor_schema(
                unit_of_measurement=UNIT_AMPERE,
                icon="mdi:alpha-a-circle",
                device_class=DEVICE_CLASS_CURRENT,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_CURRENT_L2): sensor.sensor_schema(
                unit_of_measurement=UNIT_AMPERE,
                icon="mdi:alpha-a-circle",
                device_class=DEVICE_CLASS_CURRENT,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_CURRENT_L3): sensor.sensor_schema(
                unit_of_measurement=UNIT_AMPERE,
                icon="mdi:alpha-a-circle",
                device_class=DEVICE_CLASS_CURRENT,
                state_class=STATE_CLASS_MEASUREMENT,
                accuracy_decimals=1,
            ),
            cv.Optional(CONF_WIFI_RSSI): sensor.sensor_schema(
                unit_of_measurement=UNIT_DECIBEL_MILLIWATT,
                icon="mdi:wifi",
                device_class=DEVICE_CLASS_SIGNAL_STRENGTH,
                state_class=STATE_CLASS_MEASUREMENT,
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
        }
    ),
    cv.has_at_least_one_key(
        CONF_TEMPERATURE,
        CONF_TEMPERATURE_HIGH,
        CONF_TEMPERATURE_LOW,
        CONF_EMETER_POWER,
        CONF_EMETER_SESSION_TIME,
        CONF_EMETER_CHARGING_TIME,
        CONF_HEAP,
        CONF_HEAP_USED,
        CONF_HEAP_TOTAL,
        CONF_ENERGY_CONSUMPTION,
        CONF_TOTAL_ENERGY_CONSUMPTION,
        CONF_VOLTAGE_L1,
        CONF_VOLTAGE_L2,
        CONF_VOLTAGE_L3,
        CONF_CURRENT_L1,
        CONF_CURRENT_L2,
        CONF_CURRENT_L3,
        CONF_WIFI_RSSI,
    ),
)


async def to_code(config):
    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if temperature_high_config := config.get(CONF_TEMPERATURE_HIGH):
        sens = await sensor.new_sensor(temperature_high_config)
        cg.add(parent.set_temperature_high_sensor(sens))
    elif temperature_config := config.get(CONF_TEMPERATURE):
        sens = await sensor.new_sensor(temperature_config)
        cg.add(parent.set_temperature_high_sensor(sens))
    if temperature_low_config := config.get(CONF_TEMPERATURE_LOW):
        sens = await sensor.new_sensor(temperature_low_config)
        cg.add(parent.set_temperature_low_sensor(sens))
    if power_config := config.get(CONF_EMETER_POWER):
        sens = await sensor.new_sensor(power_config)
        cg.add(parent.set_emeter_power_sensor(sens))
    if session_config := config.get(CONF_EMETER_SESSION_TIME):
        sens = await sensor.new_sensor(session_config)
        cg.add(parent.set_emeter_session_time_sensor(sens))
    if charging_config := config.get(CONF_EMETER_CHARGING_TIME):
        sens = await sensor.new_sensor(charging_config)
        cg.add(parent.set_emeter_charging_time_sensor(sens))
    if heap_used_config := config.get(CONF_HEAP_USED):
        sens = await sensor.new_sensor(heap_used_config)
        cg.add(parent.set_heap_used_sensor(sens))
    elif heap_config := config.get(CONF_HEAP):
        sens = await sensor.new_sensor(heap_config)
        cg.add(parent.set_heap_used_sensor(sens))
    if heap_total_config := config.get(CONF_HEAP_TOTAL):
        sens = await sensor.new_sensor(heap_total_config)
        cg.add(parent.set_heap_total_sensor(sens))
    if energy_config := config.get(CONF_ENERGY_CONSUMPTION):
        sens = await sensor.new_sensor(energy_config)
        cg.add(parent.set_energy_consumption_sensor(sens))
    if total_energy_config := config.get(CONF_TOTAL_ENERGY_CONSUMPTION):
        sens = await sensor.new_sensor(total_energy_config)
        cg.add(parent.set_total_energy_consumption_sensor(sens))
    if voltage_l1_config := config.get(CONF_VOLTAGE_L1):
        sens = await sensor.new_sensor(voltage_l1_config)
        cg.add(parent.set_voltage_l1_sensor(sens))
    if voltage_l2_config := config.get(CONF_VOLTAGE_L2):
        sens = await sensor.new_sensor(voltage_l2_config)
        cg.add(parent.set_voltage_l2_sensor(sens))
    if voltage_l3_config := config.get(CONF_VOLTAGE_L3):
        sens = await sensor.new_sensor(voltage_l3_config)
        cg.add(parent.set_voltage_l3_sensor(sens))
    if current_l1_config := config.get(CONF_CURRENT_L1):
        sens = await sensor.new_sensor(current_l1_config)
        cg.add(parent.set_current_l1_sensor(sens))
    if current_l2_config := config.get(CONF_CURRENT_L2):
        sens = await sensor.new_sensor(current_l2_config)
        cg.add(parent.set_current_l2_sensor(sens))
    if current_l3_config := config.get(CONF_CURRENT_L3):
        sens = await sensor.new_sensor(current_l3_config)
        cg.add(parent.set_current_l3_sensor(sens))
    if wifi_rssi_config := config.get(CONF_WIFI_RSSI):
        sens = await sensor.new_sensor(wifi_rssi_config)
        cg.add(parent.set_wifi_rssi_sensor(sens))
