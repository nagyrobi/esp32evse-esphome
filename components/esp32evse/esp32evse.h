#pragma once

#include "esphome/components/button/button.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/component.h"
#include "esphome/core/defines.h"
#include "esphome/core/hal.h"

#include <deque>
#include <functional>
#include <string>

namespace esphome {
namespace esp32evse {

class ESP32EVSEEnableSwitch;
class ESP32EVSEChargingCurrentNumber;
class ESP32EVSEFastSubscribeButton;
class ESP32EVSEFastUnsubscribeButton;

class ESP32EVSEComponent : public uart::UARTDevice, public Component {
 public:
  void setup() override;
  void loop() override;
  void dump_config() override;

  void set_state_text_sensor(text_sensor::TextSensor *sensor) { this->state_text_sensor_ = sensor; }
  void set_enable_switch(ESP32EVSEEnableSwitch *sw) { this->enable_switch_ = sw; }
  void set_temperature_sensor(sensor::Sensor *sensor) { this->temperature_sensor_ = sensor; }
  void set_charging_current_number(ESP32EVSEChargingCurrentNumber *number) {
    this->charging_current_number_ = number;
  }
  void set_emeter_power_sensor(sensor::Sensor *sensor) { this->emeter_power_sensor_ = sensor; }
  void set_emeter_session_time_sensor(sensor::Sensor *sensor) {
    this->emeter_session_time_sensor_ = sensor;
  }
  void set_emeter_charging_time_sensor(sensor::Sensor *sensor) {
    this->emeter_charging_time_sensor_ = sensor;
  }
  void set_fast_subscribe_button(ESP32EVSEFastSubscribeButton *btn) { this->fast_subscribe_button_ = btn; }
  void set_fast_unsubscribe_button(ESP32EVSEFastUnsubscribeButton *btn) {
    this->fast_unsubscribe_button_ = btn;
  }

  void request_state_update();
  void request_enable_update();
  void request_temperature_update();
  void request_charging_current_update();
  void request_emeter_power_update();
  void request_emeter_session_time_update();
  void request_emeter_charging_time_update();

  void write_enable_state(bool enabled);
  void write_charging_current(float current);
  void subscribe_fast_power_updates();
  void unsubscribe_fast_power_updates();

 protected:
  struct PendingCommand {
    std::string command;
    std::function<void(bool)> callback;
    uint32_t start_time;
  };

  void process_line_(const std::string &line);
  void handle_ack_(bool success);
  void update_state_(uint8_t state);
  void update_enable_(bool enable);
  void update_temperature_(int count, int32_t high, int32_t low);
  void update_charging_current_(uint16_t value_tenths);
  void update_emeter_power_(uint32_t power_w);
  void update_emeter_session_time_(uint32_t time_s);
  void update_emeter_charging_time_(uint32_t time_s);

  bool send_command_(const std::string &command, std::function<void(bool)> callback = nullptr);

  text_sensor::TextSensor *state_text_sensor_{nullptr};
  ESP32EVSEEnableSwitch *enable_switch_{nullptr};
  sensor::Sensor *temperature_sensor_{nullptr};
  ESP32EVSEChargingCurrentNumber *charging_current_number_{nullptr};
  sensor::Sensor *emeter_power_sensor_{nullptr};
  sensor::Sensor *emeter_session_time_sensor_{nullptr};
  sensor::Sensor *emeter_charging_time_sensor_{nullptr};
  ESP32EVSEFastSubscribeButton *fast_subscribe_button_{nullptr};
  ESP32EVSEFastUnsubscribeButton *fast_unsubscribe_button_{nullptr};

  std::string read_buffer_;
  std::deque<PendingCommand> pending_commands_;
};

class ESP32EVSEEnableSwitch : public switch_::Switch, public Parented<ESP32EVSEComponent> {
 protected:
  void write_state(bool state) override;
};

class ESP32EVSEChargingCurrentNumber : public number::Number, public Parented<ESP32EVSEComponent> {
 protected:
  number::NumberTraits traits() override;
  void control(float value) override;
};

class ESP32EVSEFastSubscribeButton : public button::Button, public Parented<ESP32EVSEComponent> {
 protected:
  void press_action() override;
};

class ESP32EVSEFastUnsubscribeButton : public button::Button, public Parented<ESP32EVSEComponent> {
 protected:
  void press_action() override;
};

}  // namespace esp32evse
}  // namespace esphome
