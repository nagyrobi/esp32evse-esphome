#include "esp32evse.h"

#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <inttypes.h>

namespace esphome {
namespace esp32evse {

static const char *const TAG = "esp32evse";

void ESP32EVSEComponent::setup() {
  ESP_LOGCONFIG(TAG, "Setting up ESP32 EVSE component");

  // Initial queries
  this->set_timeout(1000, [this]() {
    this->request_state_update();
    this->request_enable_update();
    this->request_temperature_update();
    this->request_charging_current_update();
    this->request_emeter_power_update();
    this->request_emeter_session_time_update();
    this->request_emeter_charging_time_update();

    // Subscribe to state and enable updates every second by default
    this->send_command_("AT+SUB=\"+STATE\",1000");
    this->send_command_("AT+SUB=\"+ENABLE\",1000");
    if (this->emeter_power_sensor_ != nullptr) {
      this->send_command_("AT+SUB=\"+EMETERPOWER\",1000");
    }
  });

  if (this->temperature_sensor_ != nullptr) {
    this->set_interval("temp_poll", 60000, [this]() { this->request_temperature_update(); });
  }
  if (this->emeter_power_sensor_ != nullptr) {
    this->set_interval("emeter_power_poll", 30000, [this]() { this->request_emeter_power_update(); });
  }
  if (this->emeter_session_time_sensor_ != nullptr) {
    this->set_interval("emeter_ses_time_poll", 10000,
                       [this]() { this->request_emeter_session_time_update(); });
  }
  if (this->emeter_charging_time_sensor_ != nullptr) {
    this->set_interval("emeter_ch_time_poll", 10000,
                       [this]() { this->request_emeter_charging_time_update(); });
  }
  if (this->charging_current_number_ != nullptr) {
    this->set_interval("chcur_poll", 60000, [this]() { this->request_charging_current_update(); });
  }
}

void ESP32EVSEComponent::loop() {
  while (this->available()) {
    uint8_t byte;
    this->read_byte(&byte);
    char c = static_cast<char>(byte);
    if (c == '\r')
      continue;
    if (c == '\n') {
      if (!this->read_buffer_.empty()) {
        this->process_line_(this->read_buffer_);
        this->read_buffer_.clear();
      }
    } else {
      this->read_buffer_.push_back(c);
      if (this->read_buffer_.size() > 256) {
        ESP_LOGW(TAG, "Line too long, resetting buffer");
        this->read_buffer_.clear();
      }
    }
  }

  // Handle command timeouts (5 seconds)
  const uint32_t now = millis();
  while (!this->pending_commands_.empty()) {
    auto &front = this->pending_commands_.front();
    if (now - front.start_time < 5000) {
      break;
    }
    ESP_LOGW(TAG, "Command '%s' timed out", front.command.c_str());
    if (front.callback)
      front.callback(false);
    this->pending_commands_.pop_front();
  }
}

void ESP32EVSEComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "ESP32 EVSE:");
  if (this->temperature_sensor_ != nullptr) {
    ESP_LOGCONFIG(TAG, "  Temperature polling interval: 60s");
  }
  if (this->emeter_power_sensor_ != nullptr) {
    ESP_LOGCONFIG(TAG, "  Energy meter power polling interval: 30s");
  }
  if (this->emeter_session_time_sensor_ != nullptr || this->emeter_charging_time_sensor_ != nullptr) {
    ESP_LOGCONFIG(TAG, "  Energy meter time polling interval: 10s");
  }
  if (this->charging_current_number_ != nullptr) {
    ESP_LOGCONFIG(TAG, "  Charging current polling interval: 60s");
  }
}

void ESP32EVSEComponent::request_state_update() { this->send_command_("AT+STATE?"); }
void ESP32EVSEComponent::request_enable_update() { this->send_command_("AT+ENABLE?"); }
void ESP32EVSEComponent::request_temperature_update() { this->send_command_("AT+TEMP?"); }
void ESP32EVSEComponent::request_charging_current_update() { this->send_command_("AT+CHCUR?"); }
void ESP32EVSEComponent::request_emeter_power_update() { this->send_command_("AT+EMETERPOWER?"); }
void ESP32EVSEComponent::request_emeter_session_time_update() {
  this->send_command_("AT+EMETERSESTIME?");
}
void ESP32EVSEComponent::request_emeter_charging_time_update() {
  this->send_command_("AT+EMETERCHTIME?");
}

void ESP32EVSEComponent::write_enable_state(bool enabled) {
  std::string command = "AT+ENABLE=";
  command += enabled ? '1' : '0';
  this->send_command_(command, [this, enabled](bool success) {
    if (!success && this->enable_switch_ != nullptr) {
      this->enable_switch_->publish_state(!enabled);
    }
  });
}

void ESP32EVSEComponent::write_charging_current(float current) {
  if (current < 6.0f)
    current = 6.0f;
  else if (current > 63.0f)
    current = 63.0f;
  uint16_t tenths = static_cast<uint16_t>(std::roundf(current * 10.0f));
  std::string command = "AT+CHCUR=" + std::to_string(tenths);
  this->send_command_(command, [this](bool success) {
    if (!success && this->charging_current_number_ != nullptr) {
      this->request_charging_current_update();
    }
  });
}

void ESP32EVSEComponent::subscribe_fast_power_updates() {
  this->send_command_("AT+SUB=\"+EMETERPOWER\",500");
}

void ESP32EVSEComponent::unsubscribe_fast_power_updates() {
  this->send_command_("AT+UNSUB=\"+EMETERPOWER\"");
}

void ESP32EVSEComponent::send_command_(const std::string &command, std::function<void(bool)> callback) {
  ESP_LOGV(TAG, "Sending command: %s", command.c_str());
  this->write_str(command.c_str());
  this->write_str("\r\n");
  PendingCommand pending{command, std::move(callback), millis()};
  this->pending_commands_.push_back(std::move(pending));
}

void ESP32EVSEComponent::process_line_(const std::string &line) {
  ESP_LOGV(TAG, "Received line: %s", line.c_str());
  if (line == "OK") {
    this->handle_ack_(true);
    return;
  }
  if (line == "ERROR") {
    this->handle_ack_(false);
    return;
  }
  if (line.rfind("+STATE=", 0) == 0) {
    int value = atoi(line.c_str() + 7);
    this->update_state_(value);
    return;
  }
  if (line.rfind("+ENABLE=", 0) == 0) {
    int value = atoi(line.c_str() + 8);
    this->update_enable_(value == 1);
    return;
  }
  if (line.rfind("+TEMP=", 0) == 0) {
    int count = 0;
    int32_t high = 0;
    int32_t low = 0;
    if (sscanf(line.c_str(), "+TEMP=%d,%" PRIi32 ",%" PRIi32, &count, &high, &low) == 3) {
      this->update_temperature_(count, high, low);
    }
    return;
  }
  if (line.rfind("+CHCUR=", 0) == 0) {
    int value = atoi(line.c_str() + 7);
    if (value >= 0)
      this->update_charging_current_(static_cast<uint16_t>(value));
    return;
  }
  if (line.rfind("+EMETERPOWER=", 0) == 0) {
    uint32_t power = static_cast<uint32_t>(strtoul(line.c_str() + 13, nullptr, 10));
    this->update_emeter_power_(power);
    return;
  }
  if (line.rfind("+EMETERSESTIME=", 0) == 0) {
    uint32_t time = static_cast<uint32_t>(strtoul(line.c_str() + 15, nullptr, 10));
    this->update_emeter_session_time_(time);
    return;
  }
  if (line.rfind("+EMETERCHTIME=", 0) == 0) {
    uint32_t time = static_cast<uint32_t>(strtoul(line.c_str() + 14, nullptr, 10));
    this->update_emeter_charging_time_(time);
    return;
  }
  ESP_LOGD(TAG, "Unhandled line: %s", line.c_str());
}

void ESP32EVSEComponent::handle_ack_(bool success) {
  if (this->pending_commands_.empty()) {
    ESP_LOGW(TAG, "Received %s without pending command", success ? "OK" : "ERROR");
    return;
  }
  auto pending = this->pending_commands_.front();
  this->pending_commands_.pop_front();
  ESP_LOGV(TAG, "Command '%s' completed with %s", pending.command.c_str(), success ? "OK" : "ERROR");
  if (pending.callback)
    pending.callback(success);
}

void ESP32EVSEComponent::update_state_(uint8_t state) {
  static const char *const STATE_NAMES[] = {"A", "B1", "B2", "C1", "C2", "D1", "D2", "E", "F"};
  const char *state_name = "UNKNOWN";
  if (state < sizeof(STATE_NAMES) / sizeof(STATE_NAMES[0])) {
    state_name = STATE_NAMES[state];
  }
  if (this->state_text_sensor_ != nullptr) {
    this->state_text_sensor_->publish_state(state_name);
  }
}

void ESP32EVSEComponent::update_enable_(bool enable) {
  if (this->enable_switch_ != nullptr) {
    this->enable_switch_->publish_state(enable);
  }
}

void ESP32EVSEComponent::update_temperature_(int count, int32_t high, int32_t low) {
  if (this->temperature_sensor_ == nullptr)
    return;
  if (count <= 0) {
    this->temperature_sensor_->publish_state(NAN);
    return;
  }
  float high_c = high / 100.0f;
  float low_c = low / 100.0f;
  ESP_LOGD(TAG, "Temperature sensors: %d, high %.2f°C, low %.2f°C", count, high_c, low_c);
  this->temperature_sensor_->publish_state(high_c);
}

void ESP32EVSEComponent::update_charging_current_(uint16_t value_tenths) {
  if (this->charging_current_number_ != nullptr) {
    float current = value_tenths / 10.0f;
    this->charging_current_number_->publish_state(current);
  }
}

void ESP32EVSEComponent::update_emeter_power_(uint32_t power_w) {
  if (this->emeter_power_sensor_ != nullptr) {
    this->emeter_power_sensor_->publish_state(power_w);
  }
}

void ESP32EVSEComponent::update_emeter_session_time_(uint32_t time_s) {
  if (this->emeter_session_time_sensor_ != nullptr) {
    this->emeter_session_time_sensor_->publish_state(time_s);
  }
}

void ESP32EVSEComponent::update_emeter_charging_time_(uint32_t time_s) {
  if (this->emeter_charging_time_sensor_ != nullptr) {
    this->emeter_charging_time_sensor_->publish_state(time_s);
  }
}

void ESP32EVSEEnableSwitch::write_state(bool state) {
  if (this->parent_ == nullptr)
    return;
  this->publish_state(state);
  this->parent_->write_enable_state(state);
}

void ESP32EVSEChargingCurrentNumber::control(float value) {
  if (this->parent_ == nullptr)
    return;
  if (value < 6.0f)
    value = 6.0f;
  else if (value > 63.0f)
    value = 63.0f;
  this->publish_state(value);
  this->parent_->write_charging_current(value);
}

ESP32EVSEChargingCurrentNumber::ESP32EVSEChargingCurrentNumber() {
  this->traits_.set_min_value(6.0f);
  this->traits_.set_max_value(63.0f);
  this->traits_.set_step(0.1f);
}

void ESP32EVSEFastSubscribeButton::press_action() {
  if (this->parent_ == nullptr)
    return;
  this->parent_->subscribe_fast_power_updates();
}

void ESP32EVSEFastUnsubscribeButton::press_action() {
  if (this->parent_ == nullptr)
    return;
  this->parent_->unsubscribe_fast_power_updates();
}

}  // namespace esp32evse
}  // namespace esphome
