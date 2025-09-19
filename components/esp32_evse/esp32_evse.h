#pragma once

#include "esphome/components/button/button.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/component.h"
#include "esphome/core/log.h"

#include <string>

namespace esphome {
namespace esp32_evse {

class ESP32EVSEChargingSwitch;
class ESP32EVSEResetButton;
class ESP32EVSECurrentLimitNumber;

class ESP32EVSEComponent : public PollingComponent, public uart::UARTDevice {
 public:
  ESP32EVSEComponent();

  void set_voltage_sensor(sensor::Sensor *sensor) { voltage_sensor_ = sensor; }
  void set_current_sensor(sensor::Sensor *sensor) { current_sensor_ = sensor; }
  void set_energy_sensor(sensor::Sensor *sensor) { energy_sensor_ = sensor; }
  void set_temperature_sensor(sensor::Sensor *sensor) { temperature_sensor_ = sensor; }
  void set_charging_state_text_sensor(text_sensor::TextSensor *sensor) {
    charging_state_text_sensor_ = sensor;
  }
  void set_charging_switch(ESP32EVSEChargingSwitch *sw) { charging_switch_ = sw; }
  void set_reset_button(ESP32EVSEResetButton *button) { reset_button_ = button; }
  void set_current_limit_number(ESP32EVSECurrentLimitNumber *number) {
    current_limit_number_ = number;
  }

  void setup() override;
  void dump_config() override;
  void loop() override;
  void update() override;

  bool set_charging_enabled(bool enabled);
  bool reset_evse();
  bool set_current_limit(float value);

 protected:
  bool execute_query_(const std::string &command, std::string &response);
  bool execute_command_(const std::string &command, std::string *response = nullptr);
  bool read_line_(std::string &line, uint32_t timeout_ms) const;
  void flush_input_();
  bool parse_numeric_response_(const std::string &response, const std::string &prefix,
                               float *value) const;
  bool parse_state_response_(const std::string &response, std::string *value) const;

  void publish_error_(const char *operation, const std::string &response) const;

  void update_charging_state_();
  void update_voltage_();
  void update_current_();
  void update_energy_();
  void update_temperature_();

  sensor::Sensor *voltage_sensor_{nullptr};
  sensor::Sensor *current_sensor_{nullptr};
  sensor::Sensor *energy_sensor_{nullptr};
  sensor::Sensor *temperature_sensor_{nullptr};
  text_sensor::TextSensor *charging_state_text_sensor_{nullptr};
  ESP32EVSEChargingSwitch *charging_switch_{nullptr};
  ESP32EVSEResetButton *reset_button_{nullptr};
  ESP32EVSECurrentLimitNumber *current_limit_number_{nullptr};

  std::string incoming_line_;
  uint32_t command_timeout_ms_{1500};
  uint8_t command_retries_{2};
  bool last_charging_enabled_{false};
};

class ESP32EVSEChargingSwitch : public switch_::Switch, public Parented<ESP32EVSEComponent> {
 public:
  void write_state(bool state) override;
};

class ESP32EVSEResetButton : public button::Button, public Parented<ESP32EVSEComponent> {
 protected:
  void press_action() override;
};

class ESP32EVSECurrentLimitNumber : public number::Number, public Parented<ESP32EVSEComponent> {
 protected:
  void control(float value) override;
};

}  // namespace esp32_evse
}  // namespace esphome

