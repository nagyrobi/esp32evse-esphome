#include "esp32_evse.h"

#include "esphome/core/helpers.h"

#include <cmath>

namespace esphome {
namespace esp32_evse {

static const char *const TAG = "esp32_evse";

ESP32EVSEComponent::ESP32EVSEComponent() : PollingComponent(15000) {}

void ESP32EVSEComponent::setup() {
  ESP_LOGCONFIG(TAG, "Setting up ESP32 EVSE interface...");
  this->flush_input_();

  std::string response;
  if (this->execute_command_("AT", &response)) {
    if (!response.empty() && response != "OK") {
      ESP_LOGI(TAG, "EVSE replied: %s", response.c_str());
    }
  } else {
    ESP_LOGW(TAG, "No response to basic AT probe. Continuing anyway.");
  }
}

void ESP32EVSEComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "ESP32 EVSE external component");
  LOG_SENSOR("  ", "Voltage", this->voltage_sensor_);
  LOG_SENSOR("  ", "Current", this->current_sensor_);
  LOG_SENSOR("  ", "Energy", this->energy_sensor_);
  LOG_SENSOR("  ", "Temperature", this->temperature_sensor_);
  LOG_TEXT_SENSOR("  ", "Charging State", this->charging_state_text_sensor_);
  LOG_SWITCH("  ", "Charging Control", this->charging_switch_);
  LOG_BUTTON("  ", "Reset", this->reset_button_);
  LOG_NUMBER("  ", "Current Limit", this->current_limit_number_);
  LOG_UPDATE_INTERVAL(this);
}

void ESP32EVSEComponent::loop() {
  while (this->available()) {
    const char c = this->read();
    if (c == '\r') {
      continue;
    }
    if (c == '\n') {
      if (!this->incoming_line_.empty()) {
        ESP_LOGD(TAG, "Unsolicited response: %s", this->incoming_line_.c_str());
        this->incoming_line_.clear();
      }
      continue;
    }
    this->incoming_line_.push_back(c);
  }
}

void ESP32EVSEComponent::update() {
  this->update_charging_state_();
  this->update_voltage_();
  this->update_current_();
  this->update_energy_();
  this->update_temperature_();
}

bool ESP32EVSEComponent::set_charging_enabled(bool enabled) {
  const std::string command = enabled ? "AT+START" : "AT+STOP";
  if (!this->execute_command_(command)) {
    return false;
  }
  this->last_charging_enabled_ = enabled;
  if (this->charging_switch_ != nullptr) {
    this->charging_switch_->publish_state(enabled);
  }
  return true;
}

bool ESP32EVSEComponent::reset_evse() {
  if (!this->execute_command_("AT+RESET")) {
    return false;
  }
  return true;
}

bool ESP32EVSEComponent::set_current_limit(float value) {
  char buffer[16];
  snprintf(buffer, sizeof(buffer), "%.1f", value);
  std::string command = "AT+SETCUR=";
  command += buffer;
  if (!this->execute_command_(command)) {
    return false;
  }
  if (this->current_limit_number_ != nullptr) {
    this->current_limit_number_->publish_state(value);
  }
  return true;
}

bool ESP32EVSEComponent::execute_query_(const std::string &command, std::string &response) {
  if (!this->execute_command_(command, &response)) {
    return false;
  }
  if (response.empty()) {
    ESP_LOGW(TAG, "Received empty payload for %s", command.c_str());
    return false;
  }
  return true;
}

bool ESP32EVSEComponent::execute_command_(const std::string &command, std::string *response) {
  for (uint8_t attempt = 0; attempt <= this->command_retries_; ++attempt) {
    this->flush_input_();
    this->write_str(command.c_str());
    this->write_str("\r\n");
    this->flush();

    std::string first_line;
    if (!this->read_line_(first_line, this->command_timeout_ms_)) {
      ESP_LOGW(TAG, "Timeout waiting for response to %s (attempt %u)", command.c_str(),
               static_cast<unsigned>(attempt + 1));
      continue;
    }

    if (first_line.empty()) {
      continue;
    }

    if (first_line == "OK") {
      if (response != nullptr) {
        response->clear();
      }
      return true;
    }

    if (first_line.rfind("ERR", 0) == 0) {
      this->publish_error_(command.c_str(), first_line);
      continue;
    }

    if (response != nullptr) {
      *response = first_line;
    }

    std::string second_line;
    if (this->read_line_(second_line, 150)) {
      if (second_line == "OK") {
        return true;
      }
      if (second_line.rfind("ERR", 0) == 0) {
        this->publish_error_(command.c_str(), second_line);
        continue;
      }
      // Preserve unparsed data for visibility in the logs.
      ESP_LOGD(TAG, "Additional response to %s: %s", command.c_str(), second_line.c_str());
    }

    return true;
  }

  ESP_LOGE(TAG, "Failed to execute command %s after %u attempts", command.c_str(),
           static_cast<unsigned>(this->command_retries_ + 1));
  return false;
}

bool ESP32EVSEComponent::read_line_(std::string &line, uint32_t timeout_ms) const {
  line.clear();
  const uint32_t start = millis();
  while (millis() - start < timeout_ms) {
    if (this->available()) {
      const char c = this->read();
      if (c == '\r') {
        continue;
      }
      if (c == '\n') {
        if (!line.empty()) {
          return true;
        }
        continue;
      }
      line.push_back(c);
      continue;
    }
    delay(5);
  }
  return !line.empty();
}

void ESP32EVSEComponent::flush_input_() {
  this->incoming_line_.clear();
  while (this->available()) {
    this->read();
  }
}

bool ESP32EVSEComponent::parse_numeric_response_(const std::string &response,
                                                 const std::string &prefix, float *value) const {
  if (!value) {
    return false;
  }
  if (response.rfind(prefix, 0) != 0) {
    ESP_LOGW(TAG, "Unexpected response format: %s", response.c_str());
    return false;
  }
  const std::string data = response.substr(prefix.length());
  const float parsed = parse_float(data.c_str());
  if (isnan(parsed)) {
    ESP_LOGW(TAG, "Failed to parse numeric value from %s", response.c_str());
    return false;
  }
  *value = parsed;
  return true;
}

bool ESP32EVSEComponent::parse_state_response_(const std::string &response,
                                               std::string *value) const {
  if (!value) {
    return false;
  }
  const auto separator = response.find(':');
  if (separator == std::string::npos) {
    ESP_LOGW(TAG, "Failed to parse state from %s", response.c_str());
    return false;
  }
  *value = response.substr(separator + 1);
  return true;
}

void ESP32EVSEComponent::publish_error_(const char *operation, const std::string &response) const {
  ESP_LOGW(TAG, "%s returned error: %s", operation, response.c_str());
}

void ESP32EVSEComponent::update_charging_state_() {
  if (this->charging_state_text_sensor_ == nullptr) {
    return;
  }
  std::string response;
  if (!this->execute_query_("AT+STATE?", response)) {
    return;
  }
  std::string state;
  if (!this->parse_state_response_(response, &state)) {
    return;
  }
  this->charging_state_text_sensor_->publish_state(state);
  const bool is_active = state == "Charging" || state == "Active" || state == "Preparing";
  this->last_charging_enabled_ = is_active;
  if (this->charging_switch_ != nullptr) {
    this->charging_switch_->publish_state(this->last_charging_enabled_);
  }
}

void ESP32EVSEComponent::update_voltage_() {
  if (this->voltage_sensor_ == nullptr) {
    return;
  }
  std::string response;
  if (!this->execute_query_("AT+VOLT?", response)) {
    return;
  }
  float value;
  if (!this->parse_numeric_response_(response, "VOLT:", &value)) {
    return;
  }
  this->voltage_sensor_->publish_state(value);
}

void ESP32EVSEComponent::update_current_() {
  if (this->current_sensor_ == nullptr) {
    return;
  }
  std::string response;
  if (!this->execute_query_("AT+CURR?", response)) {
    return;
  }
  float value;
  if (!this->parse_numeric_response_(response, "CURR:", &value)) {
    return;
  }
  this->current_sensor_->publish_state(value);
}

void ESP32EVSEComponent::update_energy_() {
  if (this->energy_sensor_ == nullptr) {
    return;
  }
  std::string response;
  if (!this->execute_query_("AT+ENER?", response)) {
    return;
  }
  float value;
  if (!this->parse_numeric_response_(response, "ENER:", &value)) {
    return;
  }
  this->energy_sensor_->publish_state(value);
}

void ESP32EVSEComponent::update_temperature_() {
  if (this->temperature_sensor_ == nullptr) {
    return;
  }
  std::string response;
  if (!this->execute_query_("AT+TEMP?", response)) {
    return;
  }
  float value;
  if (!this->parse_numeric_response_(response, "TEMP:", &value)) {
    return;
  }
  this->temperature_sensor_->publish_state(value);
}

void ESP32EVSEChargingSwitch::write_state(bool state) {
  if (!this->parent_->set_charging_enabled(state)) {
    this->publish_state(this->state);
    return;
  }
  this->publish_state(state);
}

void ESP32EVSEResetButton::press_action() {
  if (!this->parent_->reset_evse()) {
    ESP_LOGW(TAG, "Reset command failed");
  }
}

void ESP32EVSECurrentLimitNumber::control(float value) {
  if (!this->parent_->set_current_limit(value)) {
    this->publish_state(this->state);
    return;
  }
  this->publish_state(value);
}

}  // namespace esp32_evse
}  // namespace esphome

