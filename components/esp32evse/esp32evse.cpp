// Implementation of the ESP32 EVSE ESPHome component.  This file contains the
// UART protocol glue that synchronises charger state with the generated
// entities configured in YAML.
#include "esp32evse.h"

#include "esphome/core/helpers.h"
#include "esphome/core/log.h"

#include <cctype>
#include <cmath>
#include <cstdio>
#include <cstdlib>
#include <cstring>
#include <ctime>
#include <inttypes.h>
#include <limits>
#include <string>
#include <utility>
#include <vector>

namespace esphome {
namespace esp32evse {

static const char *const TAG = "esp32evse";

namespace {

// Utility: return a pointer to the substring that follows ``prefix`` if the
// incoming UART line starts with it.  Many EVSE responses follow a predictable
// ``KEY=VALUE`` structure, so this helper keeps the parsing code terse.
const char *value_after_prefix(const std::string &line, const char *prefix) {
  const size_t prefix_len = strlen(prefix);
  if (line.compare(0, prefix_len, prefix) != 0)
    return nullptr;
  size_t pos = prefix_len;
  if (pos < line.size() && (line[pos] == '=' || line[pos] == ':'))
    ++pos;
  while (pos < line.size() && isspace(static_cast<unsigned char>(line[pos])))
    ++pos;
  return line.c_str() + pos;
}

// Utility: trim whitespace and optional quotes from a string returned by the
// EVSE so we can forward clean values to downstream consumers.
std::string trim_copy(const char *value) {
  if (value == nullptr)
    return {};
  std::string out(value);
  size_t start = 0;
  while (start < out.size() && isspace(static_cast<unsigned char>(out[start])))
    ++start;
  size_t end = out.size();
  while (end > start && isspace(static_cast<unsigned char>(out[end - 1])))
    --end;
  out = out.substr(start, end - start);
  if (out.size() >= 2 && ((out.front() == '"' && out.back() == '"') ||
                          (out.front() == '\'' && out.back() == '\''))) {
    out = out.substr(1, out.size() - 2);
  }
  return out;
}

// Utility: split a delimited string into trimmed tokens.  Used for parsing
// multi-value responses such as comma separated sensor tuples.
std::vector<std::string> split_and_trim(const std::string &input, char delimiter = ',') {
  std::vector<std::string> parts;
  size_t start = 0;
  while (start <= input.size()) {
    size_t end = input.find(delimiter, start);
    std::string part;
    if (end == std::string::npos) {
      part = input.substr(start);
      parts.push_back(trim_copy(part.c_str()));
      break;
    }
    part = input.substr(start, end - start);
    parts.push_back(trim_copy(part.c_str()));
    start = end + 1;
  }
  return parts;
}

// Utility: parse the last floating point number contained in a response.
float parse_last_float(const std::string &input) {
  float result = NAN;
  const char *start = input.c_str();
  char *endptr = nullptr;
  while (*start != '\0') {
    float value = strtof(start, &endptr);
    if (endptr == start) {
      ++start;
      continue;
    }
    result = value;
    start = endptr;
  }
  return result;
}

}  // namespace

// Called once at boot to schedule initial state requests from the EVSE.
void ESP32EVSEComponent::setup() {
  ESP_LOGCONFIG(TAG, "Setting up ESP32 EVSE component");

  this->set_timeout(1000, [this]() {
    this->request_state_update();
    this->request_enable_update();
    this->request_pending_authorization_update();

    if (this->temperature_high_sensor_ != nullptr || this->temperature_low_sensor_ != nullptr)
      this->request_temperature_update();
    if (this->charging_current_number_ != nullptr)
      this->request_charging_current_update();
    if (this->emeter_power_sensor_ != nullptr)
      this->request_emeter_power_update();
    if (this->emeter_session_time_sensor_ != nullptr)
      this->request_emeter_session_time_update();
    if (this->emeter_charging_time_sensor_ != nullptr)
      this->request_emeter_charging_time_update();
    if (this->chip_text_sensor_ != nullptr)
      this->request_chip_update();
    if (this->version_text_sensor_ != nullptr)
      this->request_version_update();
    if (this->idf_version_text_sensor_ != nullptr)
      this->request_idf_version_update();
    if (this->build_time_text_sensor_ != nullptr)
      this->request_build_time_update();
    if (this->device_time_text_sensor_ != nullptr)
      this->request_device_time_update();
    if (this->wifi_sta_ssid_text_sensor_ != nullptr)
      this->request_wifi_sta_cfg_update();
    if (this->wifi_sta_ip_text_sensor_ != nullptr)
      this->request_wifi_sta_ip_update();
    if (this->wifi_sta_mac_text_sensor_ != nullptr)
      this->request_wifi_sta_mac_update();
    if (this->device_name_text_sensor_ != nullptr)
      this->request_device_name_update();
    if (this->available_switch_ != nullptr)
      this->request_available_update();
    if (this->request_authorization_switch_ != nullptr)
      this->request_request_authorization_update();
    if (this->heap_used_sensor_ != nullptr || this->heap_total_sensor_ != nullptr)
      this->request_heap_update();
    if (this->energy_consumption_sensor_ != nullptr)
      this->request_energy_consumption_update();
    if (this->total_energy_consumption_sensor_ != nullptr)
      this->request_total_energy_consumption_update();
    if (this->voltage_l1_sensor_ != nullptr || this->voltage_l2_sensor_ != nullptr ||
        this->voltage_l3_sensor_ != nullptr)
      this->request_voltage_update();
    if (this->current_l1_sensor_ != nullptr || this->current_l2_sensor_ != nullptr ||
        this->current_l3_sensor_ != nullptr)
      this->request_current_update();
    if (this->wifi_rssi_sensor_ != nullptr || this->wifi_connected_binary_sensor_ != nullptr)
      this->request_wifi_status_update();
    if (this->default_charging_current_number_ != nullptr)
      this->request_default_charging_current_update();
    if (this->maximum_charging_current_number_ != nullptr)
      this->request_maximum_charging_current_update();
    if (this->consumption_limit_number_ != nullptr)
      this->request_consumption_limit_update();
    if (this->default_consumption_limit_number_ != nullptr)
      this->request_default_consumption_limit_update();
    if (this->charging_time_limit_number_ != nullptr)
      this->request_charging_time_limit_update();
    if (this->default_charging_time_limit_number_ != nullptr)
      this->request_default_charging_time_limit_update();
    if (this->under_power_limit_number_ != nullptr)
      this->request_under_power_limit_update();
    if (this->default_under_power_limit_number_ != nullptr)
      this->request_default_under_power_limit_update();
  });
}

// Process incoming UART bytes and drive the command queue.  This keeps the ESPHome
// scheduler responsive even while waiting for EVSE acknowledgements.
void ESP32EVSEComponent::loop() {
  while (this->available()) {
    uint8_t byte;
    this->read_byte(&byte);
    char c = static_cast<char>(byte);
    if (c == '\n' || c == '\r') {
      if (!this->read_buffer_.empty()) {
        this->process_line_(this->read_buffer_);
        this->read_buffer_.clear();
      }
    } else {
      this->read_buffer_.push_back(c);
      if (this->read_buffer_.size() > 512) {
        ESP_LOGW(TAG, "Line too long (%zu), discarding partial data", this->read_buffer_.size());
        this->read_buffer_.clear();
      }
    }
  }

  const uint32_t now = millis();
  while (!this->pending_commands_.empty()) {
    auto &front = this->pending_commands_.front();
    if (!front.sent) {
      this->process_next_command_();
      break;
    }
    if (now - front.start_time < 5000) {
      break;
    }
    ESP_LOGW(TAG, "Command '%s' timed out", front.command.c_str());
    auto pending = std::move(this->pending_commands_.front());
    this->pending_commands_.pop_front();
    if (pending.callback)
      pending.callback(false);
    this->process_next_command_();
  }
}

// Periodic refresh triggered by ``PollingComponent`` every 60 seconds.
void ESP32EVSEComponent::update() {
  this->request_state_update();
  this->request_enable_update();
  this->request_pending_authorization_update();

  if (this->temperature_high_sensor_ != nullptr || this->temperature_low_sensor_ != nullptr)
    this->request_temperature_update();
  if (this->charging_current_number_ != nullptr)
    this->request_charging_current_update();
  if (this->emeter_power_sensor_ != nullptr)
    this->request_emeter_power_update();
  if (this->emeter_session_time_sensor_ != nullptr)
    this->request_emeter_session_time_update();
  if (this->emeter_charging_time_sensor_ != nullptr)
    this->request_emeter_charging_time_update();
  if (this->heap_used_sensor_ != nullptr || this->heap_total_sensor_ != nullptr)
    this->request_heap_update();
  if (this->energy_consumption_sensor_ != nullptr)
    this->request_energy_consumption_update();
  if (this->total_energy_consumption_sensor_ != nullptr)
    this->request_total_energy_consumption_update();
  if (this->voltage_l1_sensor_ != nullptr || this->voltage_l2_sensor_ != nullptr ||
      this->voltage_l3_sensor_ != nullptr)
    this->request_voltage_update();
  if (this->current_l1_sensor_ != nullptr || this->current_l2_sensor_ != nullptr ||
      this->current_l3_sensor_ != nullptr)
    this->request_current_update();
  if (this->wifi_rssi_sensor_ != nullptr || this->wifi_connected_binary_sensor_ != nullptr)
    this->request_wifi_status_update();
  if (this->available_switch_ != nullptr)
    this->request_available_update();
  if (this->request_authorization_switch_ != nullptr)
    this->request_request_authorization_update();
  if (this->default_charging_current_number_ != nullptr)
    this->request_default_charging_current_update();
  if (this->maximum_charging_current_number_ != nullptr)
    this->request_maximum_charging_current_update();
  if (this->consumption_limit_number_ != nullptr)
    this->request_consumption_limit_update();
  if (this->default_consumption_limit_number_ != nullptr)
    this->request_default_consumption_limit_update();
  if (this->charging_time_limit_number_ != nullptr)
    this->request_charging_time_limit_update();
  if (this->default_charging_time_limit_number_ != nullptr)
    this->request_default_charging_time_limit_update();
  if (this->under_power_limit_number_ != nullptr)
    this->request_under_power_limit_update();
  if (this->default_under_power_limit_number_ != nullptr)
    this->request_default_under_power_limit_update();
}

// Emit human readable configuration details in the ESPHome logs.
void ESP32EVSEComponent::dump_config() {
  ESP_LOGCONFIG(TAG, "ESP32 EVSE:");
  auto *uart_parent = this->parent_;
  if (uart_parent != nullptr) {
    ESP_LOGCONFIG(TAG, "  UART Baud Rate: %u", uart_parent->get_baud_rate());
    ESP_LOGCONFIG(TAG, "  UART Data Bits: %u", uart_parent->get_data_bits());
    ESP_LOGCONFIG(TAG, "  UART Parity: %s", LOG_STR_ARG(uart::parity_to_str(uart_parent->get_parity())));
    ESP_LOGCONFIG(TAG, "  UART Stop Bits: %u", uart_parent->get_stop_bits());
    size_t rx_buffer_size = uart_parent->get_rx_buffer_size();
    if (rx_buffer_size != 0) {
      ESP_LOGCONFIG(TAG, "  UART RX Buffer Size: %u", rx_buffer_size);
    }
  } else {
    ESP_LOGW(TAG, "  No UART parent configured");
  }
}

// Thin wrappers that enqueue the corresponding AT command.  Keeping them in one
// place makes it easy to audit which controller features we query.
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
void ESP32EVSEComponent::request_chip_update() { this->send_command_("AT+CHIP?"); }
void ESP32EVSEComponent::request_version_update() { this->send_command_("AT+VER?"); }
void ESP32EVSEComponent::request_idf_version_update() { this->send_command_("AT+IDFVER?"); }
void ESP32EVSEComponent::request_build_time_update() { this->send_command_("AT+BUILDTIME?"); }
void ESP32EVSEComponent::request_device_time_update() { this->send_command_("AT+TIME?"); }
void ESP32EVSEComponent::request_wifi_sta_cfg_update() { this->send_command_("AT+WIFISTACFG?"); }
void ESP32EVSEComponent::request_wifi_sta_ip_update() { this->send_command_("AT+WIFISTAIP?"); }
void ESP32EVSEComponent::request_wifi_sta_mac_update() { this->send_command_("AT+WIFISTAMAC?"); }
void ESP32EVSEComponent::request_device_name_update() { this->send_command_("AT+DEVNAME?"); }
void ESP32EVSEComponent::request_available_update() { this->send_command_("AT+AVAILABLE?"); }
void ESP32EVSEComponent::request_request_authorization_update() {
  this->send_command_("AT+REQAUTH?");
}
void ESP32EVSEComponent::request_heap_update() { this->send_command_("AT+HEAP?"); }
void ESP32EVSEComponent::request_energy_consumption_update() {
  this->send_command_("AT+EMETERCONSUM?");
}
void ESP32EVSEComponent::request_total_energy_consumption_update() {
  this->send_command_("AT+EMETERTOTCONSUM?");
}
void ESP32EVSEComponent::request_voltage_update() { this->send_command_("AT+EMETERVOLTAGE?"); }
void ESP32EVSEComponent::request_current_update() { this->send_command_("AT+EMETERCURRENT?"); }
void ESP32EVSEComponent::request_wifi_status_update() { this->send_command_("AT+WIFISTACONN?"); }
void ESP32EVSEComponent::request_default_charging_current_update() {
  this->send_command_("AT+DEFCHCUR?");
}
void ESP32EVSEComponent::request_maximum_charging_current_update() {
  this->send_command_("AT+MAXCHCUR?");
}
void ESP32EVSEComponent::request_consumption_limit_update() {
  this->send_command_("AT+CONSUMLIM?");
}
void ESP32EVSEComponent::request_default_consumption_limit_update() {
  this->send_command_("AT+DEFCONSUMLIM?");
}
void ESP32EVSEComponent::request_charging_time_limit_update() {
  this->send_command_("AT+CHTIMELIM?");
}
void ESP32EVSEComponent::request_default_charging_time_limit_update() {
  this->send_command_("AT+DEFCHTIMELIM?");
}
void ESP32EVSEComponent::request_under_power_limit_update() {
  this->send_command_("AT+UNDERPOWERLIM?");
}
void ESP32EVSEComponent::request_default_under_power_limit_update() {
  this->send_command_("AT+DEFUNDERPOWERLIM?");
}
void ESP32EVSEComponent::request_pending_authorization_update() {
  this->send_command_("AT+PENDAUTH?");
}

// Translate ESPHome entity state changes into AT commands.
void ESP32EVSEComponent::write_enable_state(bool enabled) {
  std::string command = "AT+ENABLE=";
  command += enabled ? '1' : '0';
  this->send_command_(command, [this, enabled](bool success) {
    if (!success && this->enable_switch_ != nullptr) {
      this->enable_switch_->publish_state(!enabled);
    }
  });
}

void ESP32EVSEComponent::write_available_state(bool available) {
  std::string command = "AT+AVAILABLE=";
  command += available ? '1' : '0';
  this->send_command_(command, [this](bool success) {
    if (!success && this->available_switch_ != nullptr) {
      this->request_available_update();
    }
  });
}

void ESP32EVSEComponent::write_request_authorization_state(bool request) {
  std::string command = "AT+REQAUTH=";
  command += request ? '1' : '0';
  this->send_command_(command, [this](bool success) {
    if (!success && this->request_authorization_switch_ != nullptr) {
      this->request_request_authorization_update();
    }
  });
}

void ESP32EVSEComponent::write_charging_current(float current) {
  this->write_number_value(this->charging_current_number_, current);
}

void ESP32EVSEComponent::write_number_value(ESP32EVSEChargingCurrentNumber *number, float value) {
  if (number == nullptr)
    return;
  const std::string &command = number->get_command();
  if (command.empty())
    return;
  float scaled_value = value * number->get_multiplier();
  int32_t to_send = static_cast<int32_t>(std::lroundf(scaled_value));
  std::string cmd = command + "=" + to_string(to_send);
  this->send_command_(cmd, [this, number](bool success) {
    if (!success) {
      this->request_number_update_(number);
    }
  });
}

// Convenience wrappers for popular subscription targets.  They are exposed to
// users through templated buttons in YAML.
void ESP32EVSEComponent::subscribe_fast_power_updates() {
  this->send_command_("AT+SUB=\"+EMETERPOWER\",500");
}

void ESP32EVSEComponent::unsubscribe_fast_power_updates() {
  this->send_command_("AT+UNSUB=\"+EMETERPOWER\"");
}

void ESP32EVSEComponent::at_sub(const std::string &command, uint32_t period_ms) {
  if (!this->is_valid_subscription_argument_(command)) {
    ESP_LOGW(TAG,
             "Rejected AT+SUB wrapper request with argument '%s'; only subscription targets are allowed",
             command.c_str());
    return;
  }
  ESP_LOGW(TAG, "Sending AT+SUB for command '%s' with period %" PRIu32 " ms", command.c_str(), period_ms);
  std::string cmd = "AT+SUB=" + command + "," + std::to_string(period_ms);
  this->send_command_(cmd);
}

void ESP32EVSEComponent::at_unsub(const std::string &command) {
  if (command.empty()) {
    ESP_LOGW(TAG, "Sending AT+UNSUB with empty command parameter");
    this->send_command_("AT+UNSUB=\"\"");
    return;
  }

  if (!this->is_valid_subscription_argument_(command)) {
    ESP_LOGW(TAG,
             "Rejected AT+UNSUB wrapper request with argument '%s'; only subscription targets are allowed",
             command.c_str());
    return;
  }

  ESP_LOGW(TAG, "Sending AT+UNSUB for command '%s'", command.c_str());
  std::string cmd = "AT+UNSUB=" + command;
  this->send_command_(cmd);
}

// Validate that a subscription string only contains characters supported by the
// EVSE firmware (alphanumeric, plus, underscore, and quotes).
bool ESP32EVSEComponent::is_valid_subscription_argument_(const std::string &argument) const {
  if (argument.empty()) {
    return false;
  }
  for (size_t i = 0; i + 2 < argument.size(); ++i) {
    char c0 = argument[i];
    char c1 = argument[i + 1];
    char c2 = argument[i + 2];
    if ((c0 == 'A' || c0 == 'a') && (c1 == 'T' || c1 == 't') && c2 == '+') {
      return false;
    }
  }
  return true;
}

void ESP32EVSEComponent::send_reset_command() { this->send_command_("AT+RST"); }

void ESP32EVSEComponent::send_authorize_command() { this->send_command_("AT+AUTH"); }

bool ESP32EVSEComponent::send_command_(const std::string &command, std::function<void(bool)> callback) {
  ESP_LOGV(TAG, "Queueing command: %s", command.c_str());
  PendingCommand pending;
  pending.command = command;
  pending.callback = std::move(callback);
  this->pending_commands_.push_back(std::move(pending));
  this->process_next_command_();
  return true;
}

// Parse a single line returned by the EVSE and dispatch to the appropriate
// update handler.  The protocol is a mix of ``+KEY=VALUE`` lines and asynchronous
// ``OK``/``ERROR`` acknowledgements.
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
  if (const char *value = value_after_prefix(line, "+STATE")) {
    int state_value = atoi(value);
    this->update_state_(state_value);
    return;
  }
  if (const char *value = value_after_prefix(line, "+ENABLE")) {
    int enable_value = atoi(value);
    this->update_enable_(enable_value == 1);
    return;
  }
  if (const char *value = value_after_prefix(line, "+TEMP")) {
    int count = 0;
    int32_t high = 0;
    int32_t low = 0;
    if (sscanf(value, "%d,%" PRIi32 ",%" PRIi32, &count, &high, &low) == 3) {
      this->update_temperature_(count, high, low);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+CHCUR")) {
    int chcur_value = atoi(value);
    if (chcur_value >= 0)
      this->update_charging_current_(static_cast<uint16_t>(chcur_value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERPOWER")) {
    uint32_t power = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_emeter_power_(power);
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERSESTIME")) {
    uint32_t time = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_emeter_session_time_(time);
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERCHTIME")) {
    uint32_t time = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_emeter_charging_time_(time);
    return;
  }
  if (const char *value = value_after_prefix(line, "+CHIP")) {
    std::string chip_info = trim_copy(value);
    auto chip_parts = split_and_trim(chip_info);
    if (!chip_parts.empty()) {
      std::string formatted = chip_parts.front();
      if (chip_parts.size() >= 2) {
        int cores = atoi(chip_parts[1].c_str());
        if (cores > 0) {
          formatted += ", " + std::to_string(cores) + (cores == 1 ? " core" : " cores");
        }
      }
      this->update_chip_(formatted);
    } else {
      this->update_chip_(chip_info);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+VER")) {
    this->update_version_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+IDFVER")) {
    this->update_idf_version_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+BUILDTIME")) {
    this->update_build_time_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+TIME")) {
    uint32_t timestamp = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_device_time_(timestamp);
    return;
  }
  if (const char *value = value_after_prefix(line, "+WIFISTACFG")) {
    std::string wifi_cfg = trim_copy(value);
    auto wifi_parts = split_and_trim(wifi_cfg);
    std::string ssid;
    if (wifi_parts.size() >= 2)
      ssid = wifi_parts[1];
    else
      ssid = wifi_cfg;
    this->update_wifi_sta_cfg_(ssid);
    return;
  }
  if (const char *value = value_after_prefix(line, "+WIFISTAIP")) {
    this->update_wifi_sta_ip_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+WIFISTAMAC")) {
    this->update_wifi_sta_mac_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+DEVNAME")) {
    this->update_device_name_(trim_copy(value));
    return;
  }
  if (const char *value = value_after_prefix(line, "+AVAILABLE")) {
    int available = atoi(value);
    this->update_available_(available == 1);
    return;
  }
  if (const char *value = value_after_prefix(line, "+REQAUTH")) {
    int req = atoi(value);
    this->update_request_authorization_(req == 1);
    return;
  }
  if (const char *value = value_after_prefix(line, "+HEAP")) {
    const char *cursor = value;
    char *endptr = nullptr;
    bool has_used = false;
    bool has_total = false;
    uint32_t heap_used = 0;
    uint32_t heap_total = 0;

    unsigned long parsed = strtoul(cursor, &endptr, 10);
    if (endptr != cursor) {
      heap_used = static_cast<uint32_t>(parsed);
      has_used = true;
      cursor = endptr;

      while (*cursor != '\0' && isspace(static_cast<unsigned char>(*cursor)))
        ++cursor;
      if (*cursor == ',') {
        ++cursor;
        while (*cursor != '\0' && isspace(static_cast<unsigned char>(*cursor)))
          ++cursor;
        parsed = strtoul(cursor, &endptr, 10);
        if (endptr != cursor) {
          heap_total = static_cast<uint32_t>(parsed);
          has_total = true;
        }
      }
    }

    if (has_used || has_total) {
      this->update_heap_(has_used ? std::optional<uint32_t>(heap_used) : std::nullopt,
                         has_total ? std::optional<uint32_t>(heap_total) : std::nullopt);
    } else {
      ESP_LOGW(TAG, "Unable to parse heap values from '%s'", value);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERCONSUM")) {
    float consum = strtof(value, nullptr);
    this->update_energy_consumption_(consum);
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERTOTCONSUM")) {
    float consum = parse_last_float(value);
    if (std::isnan(consum)) {
      ESP_LOGW(TAG, "Unable to parse total energy consumption from '%s'", value);
    } else {
      this->update_total_energy_consumption_(consum);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERVOLTAGE")) {
    float l1 = NAN;
    float l2 = NAN;
    float l3 = NAN;
    if (sscanf(value, "%f,%f,%f", &l1, &l2, &l3) == 3) {
      this->update_voltages_(l1, l2, l3);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+EMETERCURRENT")) {
    float l1 = NAN;
    float l2 = NAN;
    float l3 = NAN;
    if (sscanf(value, "%f,%f,%f", &l1, &l2, &l3) == 3) {
      this->update_currents_(l1, l2, l3);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+WIFISTACONN")) {
    int connected = 0;
    int rssi = std::numeric_limits<int>::min();
    int parsed = sscanf(value, "%d,%d", &connected, &rssi);
    if (parsed >= 1) {
      if (parsed < 2) {
        rssi = std::numeric_limits<int>::min();
      }
      this->update_wifi_status_(connected == 1, rssi);
    }
    return;
  }
  if (const char *value = value_after_prefix(line, "+DEFCHCUR")) {
    int val = atoi(value);
    this->update_default_charging_current_(static_cast<uint16_t>(val));
    return;
  }
  if (const char *value = value_after_prefix(line, "+MAXCHCUR")) {
    int val = atoi(value);
    this->update_maximum_charging_current_(static_cast<uint16_t>(val));
    return;
  }
  if (const char *value = value_after_prefix(line, "+CONSUMLIM")) {
    float val = strtof(value, nullptr);
    this->update_consumption_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+DEFCONSUMLIM")) {
    float val = strtof(value, nullptr);
    this->update_default_consumption_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+CHTIMELIM")) {
    uint32_t val = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_charging_time_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+DEFCHTIMELIM")) {
    uint32_t val = static_cast<uint32_t>(strtoul(value, nullptr, 10));
    this->update_default_charging_time_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+UNDERPOWERLIM")) {
    float val = strtof(value, nullptr);
    this->update_under_power_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+DEFUNDERPOWERLIM")) {
    float val = strtof(value, nullptr);
    this->update_default_under_power_limit_(val);
    return;
  }
  if (const char *value = value_after_prefix(line, "+PENDAUTH")) {
    int val = atoi(value);
    this->update_pending_authorization_(val == 1);
    return;
  }

  ESP_LOGD(TAG, "Unhandled line: %s", line.c_str());
}

// Called after receiving an ``OK`` or ``ERROR`` response for the oldest pending
// command.
void ESP32EVSEComponent::handle_ack_(bool success) {
  if (this->pending_commands_.empty()) {
    ESP_LOGW(TAG, "Received %s without pending command", success ? "OK" : "ERROR");
    return;
  }
  auto pending = std::move(this->pending_commands_.front());
  this->pending_commands_.pop_front();
  ESP_LOGV(TAG, "Command '%s' completed with %s", pending.command.c_str(), success ? "OK" : "ERROR");
  if (pending.callback)
    pending.callback(success);
  this->process_next_command_();
}

// Send the next queued command if we are not already waiting for a reply.
void ESP32EVSEComponent::process_next_command_() {
  if (this->pending_commands_.empty())
    return;

  auto &front = this->pending_commands_.front();
  if (front.sent)
    return;

  ESP_LOGV(TAG, "Sending command: %s", front.command.c_str());
  this->write_str(front.command.c_str());
  this->write_str("\r\n");
  front.start_time = millis();
  front.sent = true;
}

// Publish EVSE state machine codes (A/B/C/etc.) to the bound text sensor.
void ESP32EVSEComponent::update_state_(uint8_t state) {
  static const char *const STATE_NAMES[] = {"A", "B1", "B2", "C1", "C2", "D1", "D2", "E", "F"};
  const char *state_name = "UNKNOWN";
  if (state < sizeof(STATE_NAMES) / sizeof(STATE_NAMES[0])) {
    state_name = STATE_NAMES[state];
  }
  this->publish_text_sensor_state_(this->state_text_sensor_, state_name);
}

// Mirror EVSE flags back into ESPHome entities.
void ESP32EVSEComponent::update_enable_(bool enable) {
  if (this->enable_switch_ != nullptr) {
    this->enable_switch_->publish_state(enable);
  }
}

// Publish the EVSE's reported temperature extremes.  Values are sent in
// centi-degrees, so we convert to Celsius before forwarding them.
void ESP32EVSEComponent::update_temperature_(int count, int32_t high, int32_t low) {
  if (this->temperature_high_sensor_ == nullptr && this->temperature_low_sensor_ == nullptr)
    return;
  if (count <= 0) {
    if (this->temperature_high_sensor_ != nullptr)
      this->temperature_high_sensor_->publish_state(NAN);
    if (this->temperature_low_sensor_ != nullptr)
      this->temperature_low_sensor_->publish_state(NAN);
    return;
  }
  float high_c = high / 100.0f;
  float low_c = low / 100.0f;
  ESP_LOGD(TAG, "Temperature sensors: %d, high %.2f°C, low %.2f°C", count, high_c, low_c);
  if (this->temperature_high_sensor_ != nullptr)
    this->temperature_high_sensor_->publish_state(high_c);
  if (this->temperature_low_sensor_ != nullptr)
    this->temperature_low_sensor_->publish_state(low_c);
}

// Helper: convert the raw integer value reported by the EVSE into the scaled
// float the number entity expects before publishing it.
void ESP32EVSEComponent::publish_scaled_number_(ESP32EVSEChargingCurrentNumber *number, float raw_value) {
  if (number == nullptr)
    return;
  float multiplier = number->get_multiplier();
  if (multiplier == 0.0f)
    multiplier = 1.0f;
  float value = raw_value / multiplier;
  number->publish_state(value);
}

// Helper: only publish text sensor updates when the value actually changes to
// avoid unnecessary state spam for subscribers.
void ESP32EVSEComponent::publish_text_sensor_state_(text_sensor::TextSensor *sensor,
                                                    const std::string &state) {
  if (sensor == nullptr)
    return;
  if (sensor->has_state() && sensor->state == state)
    return;
  sensor->publish_state(state);
}

void ESP32EVSEComponent::update_charging_current_(uint16_t value_tenths) {
  this->publish_scaled_number_(this->charging_current_number_, value_tenths);
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

void ESP32EVSEComponent::update_chip_(const std::string &chip) {
  this->publish_text_sensor_state_(this->chip_text_sensor_, chip);
}

void ESP32EVSEComponent::update_version_(const std::string &version) {
  this->publish_text_sensor_state_(this->version_text_sensor_, version);
}

void ESP32EVSEComponent::update_idf_version_(const std::string &idf_version) {
  this->publish_text_sensor_state_(this->idf_version_text_sensor_, idf_version);
}

void ESP32EVSEComponent::update_build_time_(const std::string &build_time) {
  if (this->build_time_text_sensor_ == nullptr)
    return;
  std::string sanitized = build_time;
  size_t pos = 0;
  while ((pos = sanitized.find('"', pos)) != std::string::npos) {
    sanitized.erase(pos, 1);
  }
  this->publish_text_sensor_state_(this->build_time_text_sensor_, sanitized);
}

void ESP32EVSEComponent::update_device_time_(uint32_t timestamp) {
  if (this->device_time_text_sensor_ == nullptr)
    return;
  time_t raw_time = static_cast<time_t>(timestamp);
  struct tm tm_info;
  if (!localtime_r(&raw_time, &tm_info)) {
    this->publish_text_sensor_state_(this->device_time_text_sensor_, "invalid");
    return;
  }
  char buffer[32];
  if (strftime(buffer, sizeof(buffer), "%Y-%m-%d %H:%M", &tm_info) == 0) {
    this->publish_text_sensor_state_(this->device_time_text_sensor_, "invalid");
    return;
  }
  this->publish_text_sensor_state_(this->device_time_text_sensor_, buffer);
}

void ESP32EVSEComponent::update_wifi_sta_cfg_(const std::string &ssid) {
  this->publish_text_sensor_state_(this->wifi_sta_ssid_text_sensor_, ssid);
}

void ESP32EVSEComponent::update_wifi_sta_ip_(const std::string &ip) {
  this->publish_text_sensor_state_(this->wifi_sta_ip_text_sensor_, ip);
}

void ESP32EVSEComponent::update_wifi_sta_mac_(const std::string &mac) {
  this->publish_text_sensor_state_(this->wifi_sta_mac_text_sensor_, mac);
}

void ESP32EVSEComponent::update_device_name_(const std::string &name) {
  this->publish_text_sensor_state_(this->device_name_text_sensor_, name);
}

void ESP32EVSEComponent::update_available_(bool available) {
  if (this->available_switch_ != nullptr) {
    this->available_switch_->publish_state(available);
  }
}

void ESP32EVSEComponent::update_request_authorization_(bool request) {
  if (this->request_authorization_switch_ != nullptr) {
    this->request_authorization_switch_->publish_state(request);
  }
}

void ESP32EVSEComponent::update_heap_(std::optional<uint32_t> heap_used_bytes,
                                      std::optional<uint32_t> heap_total_bytes) {
  if (heap_used_bytes.has_value() && this->heap_used_sensor_ != nullptr) {
    this->heap_used_sensor_->publish_state(*heap_used_bytes);
  }
  if (heap_total_bytes.has_value() && this->heap_total_sensor_ != nullptr) {
    this->heap_total_sensor_->publish_state(*heap_total_bytes);
  }
}

void ESP32EVSEComponent::update_energy_consumption_(float value) {
  if (this->energy_consumption_sensor_ != nullptr) {
    this->energy_consumption_sensor_->publish_state(value);
  }
}

void ESP32EVSEComponent::update_total_energy_consumption_(float value) {
  if (this->total_energy_consumption_sensor_ != nullptr) {
    this->total_energy_consumption_sensor_->publish_state(value);
  }
}

void ESP32EVSEComponent::update_voltages_(float l1, float l2, float l3) {
  if (!std::isnan(l1))
    l1 /= 1000.0f;
  if (!std::isnan(l2))
    l2 /= 1000.0f;
  if (!std::isnan(l3))
    l3 /= 1000.0f;
  if (this->voltage_l1_sensor_ != nullptr)
    this->voltage_l1_sensor_->publish_state(l1);
  if (this->voltage_l2_sensor_ != nullptr)
    this->voltage_l2_sensor_->publish_state(l2);
  if (this->voltage_l3_sensor_ != nullptr)
    this->voltage_l3_sensor_->publish_state(l3);
}

void ESP32EVSEComponent::update_currents_(float l1, float l2, float l3) {
  if (!std::isnan(l1))
    l1 /= 1000.0f;
  if (!std::isnan(l2))
    l2 /= 1000.0f;
  if (!std::isnan(l3))
    l3 /= 1000.0f;
  if (this->current_l1_sensor_ != nullptr)
    this->current_l1_sensor_->publish_state(l1);
  if (this->current_l2_sensor_ != nullptr)
    this->current_l2_sensor_->publish_state(l2);
  if (this->current_l3_sensor_ != nullptr)
    this->current_l3_sensor_->publish_state(l3);
}

void ESP32EVSEComponent::update_wifi_status_(bool connected, int rssi) {
  if (this->wifi_connected_binary_sensor_ != nullptr) {
    this->wifi_connected_binary_sensor_->publish_state(connected);
  }
  if (this->wifi_rssi_sensor_ != nullptr) {
    if (connected && rssi != std::numeric_limits<int>::min()) {
      this->wifi_rssi_sensor_->publish_state(rssi);
    } else {
      this->wifi_rssi_sensor_->publish_state(NAN);
    }
  }
}

// Forward various numeric reports from the EVSE to their corresponding number
// entities.  Values are scaled so ESPHome users interact with human readable
// units instead of protocol specific integers.
void ESP32EVSEComponent::update_default_charging_current_(uint16_t value_tenths) {
  this->publish_scaled_number_(this->default_charging_current_number_, value_tenths);
}

void ESP32EVSEComponent::update_maximum_charging_current_(uint16_t value_amps) {
  this->publish_scaled_number_(this->maximum_charging_current_number_, value_amps);
}

void ESP32EVSEComponent::update_consumption_limit_(float value) {
  this->publish_scaled_number_(this->consumption_limit_number_, value);
}

void ESP32EVSEComponent::update_default_consumption_limit_(float value) {
  this->publish_scaled_number_(this->default_consumption_limit_number_, value);
}

void ESP32EVSEComponent::update_charging_time_limit_(uint32_t value) {
  this->publish_scaled_number_(this->charging_time_limit_number_, static_cast<float>(value));
}

void ESP32EVSEComponent::update_default_charging_time_limit_(uint32_t value) {
  this->publish_scaled_number_(this->default_charging_time_limit_number_, static_cast<float>(value));
}

void ESP32EVSEComponent::update_under_power_limit_(float value) {
  this->publish_scaled_number_(this->under_power_limit_number_, value);
}

void ESP32EVSEComponent::update_default_under_power_limit_(float value) {
  this->publish_scaled_number_(this->default_under_power_limit_number_, value);
}

void ESP32EVSEComponent::update_pending_authorization_(bool pending) {
  if (this->pending_authorization_binary_sensor_ != nullptr) {
    this->pending_authorization_binary_sensor_->publish_state(pending);
  }
}

// When a write command fails we re-request the value so the UI reflects the
// actual charger state.
void ESP32EVSEComponent::request_number_update_(ESP32EVSEChargingCurrentNumber *number) {
  if (number == nullptr)
    return;
  if (number == this->charging_current_number_) {
    this->request_charging_current_update();
  } else if (number == this->default_charging_current_number_) {
    this->request_default_charging_current_update();
  } else if (number == this->maximum_charging_current_number_) {
    this->request_maximum_charging_current_update();
  } else if (number == this->consumption_limit_number_) {
    this->request_consumption_limit_update();
  } else if (number == this->default_consumption_limit_number_) {
    this->request_default_consumption_limit_update();
  } else if (number == this->charging_time_limit_number_) {
    this->request_charging_time_limit_update();
  } else if (number == this->default_charging_time_limit_number_) {
    this->request_default_charging_time_limit_update();
  } else if (number == this->under_power_limit_number_) {
    this->request_under_power_limit_update();
  } else if (number == this->default_under_power_limit_number_) {
    this->request_default_under_power_limit_update();
  }
}

void ESP32EVSEEnableSwitch::write_state(bool state) {
  if (this->parent_ == nullptr)
    return;
  this->publish_state(state);
  this->parent_->write_enable_state(state);
}

// Switch implementations optimistically publish their new state and rely on the
// component callbacks to revert if the EVSE rejects the request.
void ESP32EVSEAvailableSwitch::write_state(bool state) {
  if (this->parent_ == nullptr)
    return;
  this->publish_state(state);
  this->parent_->write_available_state(state);
}

void ESP32EVSERequestAuthorizationSwitch::write_state(bool state) {
  if (this->parent_ == nullptr)
    return;
  this->publish_state(state);
  this->parent_->write_request_authorization_state(state);
}

ESP32EVSEChargingCurrentNumber::ESP32EVSEChargingCurrentNumber() {
  this->traits.set_min_value(6.0f);
  this->traits.set_max_value(63.0f);
  this->traits.set_step(0.1f);
}

void ESP32EVSEChargingCurrentNumber::control(float value) {
  if (this->parent_ == nullptr)
    return;
  this->publish_state(value);
  this->parent_->write_number_value(this, value);
}

// Buttons translate presses into EVSE commands with no additional state.
void ESP32EVSEResetButton::press_action() {
  if (this->parent_ == nullptr)
    return;
  this->parent_->send_reset_command();
}

void ESP32EVSEAuthorizeButton::press_action() {
  if (this->parent_ == nullptr)
    return;
  this->parent_->send_authorize_command();
}

}  // namespace esp32evse
}  // namespace esphome
