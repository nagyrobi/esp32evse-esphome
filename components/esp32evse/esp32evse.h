#pragma once

// Core ESPHome headers used by the component.  The order mirrors the logical
// dependencies: we expose a UART powered component that publishes entities for
// sensors, switches, numbers, buttons, etc.
#include "esphome/components/binary_sensor/binary_sensor.h"
#include "esphome/components/button/button.h"
#include "esphome/components/number/number.h"
#include "esphome/components/sensor/sensor.h"
#include "esphome/components/switch/switch.h"
#include "esphome/components/text_sensor/text_sensor.h"
#include "esphome/components/uart/uart.h"
#include "esphome/core/automation.h"
#include "esphome/core/component.h"
#include "esphome/core/defines.h"
#include "esphome/core/hal.h"

#include <deque>
#include <functional>
#include <limits>
#include <optional>
#include <string>

namespace esphome {
namespace esp32evse {

class ESP32EVSEEnableSwitch;
class ESP32EVSEAvailableSwitch;
class ESP32EVSERequestAuthorizationSwitch;
class ESP32EVSEChargingCurrentNumber;
class ESP32EVSEResetButton;
class ESP32EVSEAuthorizeButton;
class ESP32EVSEPendingAuthorizationBinarySensor;
class ESP32EVSEWifiConnectedBinarySensor;
template<typename... Ts> class ESP32EVSEAutoUpdateAction;

// Main component class that orchestrates communication with the EVSE controller
// and fans out the resulting state to the various ESPHome entities registered
// through the Python glue code.
class ESP32EVSEComponent : public uart::UARTDevice, public PollingComponent {
 public:
  ESP32EVSEComponent() : PollingComponent(60000) {}
  void setup() override;
  void loop() override;
  void dump_config() override;
  void update() override;

  // The following setter helpers are invoked from the Python glue code to
  // connect ESPHome entities to this component instance.  Storing the pointers
  // allows the C++ implementation to publish updates when data arrives from the
  // EVSE over UART.
  void set_state_text_sensor(text_sensor::TextSensor *sensor) { this->state_text_sensor_ = sensor; }
  void set_chip_text_sensor(text_sensor::TextSensor *sensor) { this->chip_text_sensor_ = sensor; }
  void set_version_text_sensor(text_sensor::TextSensor *sensor) { this->version_text_sensor_ = sensor; }
  void set_idf_version_text_sensor(text_sensor::TextSensor *sensor) {
    this->idf_version_text_sensor_ = sensor;
  }
  void set_build_time_text_sensor(text_sensor::TextSensor *sensor) {
    this->build_time_text_sensor_ = sensor;
  }
  void set_device_time_text_sensor(text_sensor::TextSensor *sensor) {
    this->device_time_text_sensor_ = sensor;
  }
  void set_wifi_sta_ssid_text_sensor(text_sensor::TextSensor *sensor) {
    this->wifi_sta_ssid_text_sensor_ = sensor;
  }
  void set_wifi_sta_ip_text_sensor(text_sensor::TextSensor *sensor) {
    this->wifi_sta_ip_text_sensor_ = sensor;
  }
  void set_wifi_sta_mac_text_sensor(text_sensor::TextSensor *sensor) {
    this->wifi_sta_mac_text_sensor_ = sensor;
  }
  void set_device_name_text_sensor(text_sensor::TextSensor *sensor) {
    this->device_name_text_sensor_ = sensor;
  }

  void set_enable_switch(ESP32EVSEEnableSwitch *sw) { this->enable_switch_ = sw; }
  void set_available_switch(ESP32EVSEAvailableSwitch *sw) { this->available_switch_ = sw; }
  void set_request_authorization_switch(ESP32EVSERequestAuthorizationSwitch *sw) {
    this->request_authorization_switch_ = sw;
  }

  void set_temperature_high_sensor(sensor::Sensor *sensor) {
    this->temperature_high_sensor_ = sensor;
  }
  void set_temperature_low_sensor(sensor::Sensor *sensor) {
    this->temperature_low_sensor_ = sensor;
  }
  void set_temperature_sensor(sensor::Sensor *sensor) { this->set_temperature_high_sensor(sensor); }
  void set_heap_used_sensor(sensor::Sensor *sensor) { this->heap_used_sensor_ = sensor; }
  void set_heap_total_sensor(sensor::Sensor *sensor) { this->heap_total_sensor_ = sensor; }
  void set_energy_consumption_sensor(sensor::Sensor *sensor) {
    this->energy_consumption_sensor_ = sensor;
  }
  void set_total_energy_consumption_sensor(sensor::Sensor *sensor) {
    this->total_energy_consumption_sensor_ = sensor;
  }
  void set_voltage_l1_sensor(sensor::Sensor *sensor) { this->voltage_l1_sensor_ = sensor; }
  void set_voltage_l2_sensor(sensor::Sensor *sensor) { this->voltage_l2_sensor_ = sensor; }
  void set_voltage_l3_sensor(sensor::Sensor *sensor) { this->voltage_l3_sensor_ = sensor; }
  void set_current_l1_sensor(sensor::Sensor *sensor) { this->current_l1_sensor_ = sensor; }
  void set_current_l2_sensor(sensor::Sensor *sensor) { this->current_l2_sensor_ = sensor; }
  void set_current_l3_sensor(sensor::Sensor *sensor) { this->current_l3_sensor_ = sensor; }
  void set_wifi_rssi_sensor(sensor::Sensor *sensor) { this->wifi_rssi_sensor_ = sensor; }

  void set_charging_current_number(ESP32EVSEChargingCurrentNumber *number) {
    this->charging_current_number_ = number;
  }
  void set_default_charging_current_number(ESP32EVSEChargingCurrentNumber *number) {
    this->default_charging_current_number_ = number;
  }
  void set_maximum_charging_current_number(ESP32EVSEChargingCurrentNumber *number) {
    this->maximum_charging_current_number_ = number;
  }
  void set_consumption_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->consumption_limit_number_ = number;
  }
  void set_default_consumption_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->default_consumption_limit_number_ = number;
  }
  void set_charging_time_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->charging_time_limit_number_ = number;
  }
  void set_default_charging_time_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->default_charging_time_limit_number_ = number;
  }
  void set_under_power_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->under_power_limit_number_ = number;
  }
  void set_default_under_power_limit_number(ESP32EVSEChargingCurrentNumber *number) {
    this->default_under_power_limit_number_ = number;
  }

  float clamp_charging_current_value(ESP32EVSEChargingCurrentNumber *number, float value) const;

  void set_emeter_power_sensor(sensor::Sensor *sensor) { this->emeter_power_sensor_ = sensor; }
  void set_emeter_session_time_sensor(sensor::Sensor *sensor) {
    this->emeter_session_time_sensor_ = sensor;
  }
  void set_emeter_charging_time_sensor(sensor::Sensor *sensor) {
    this->emeter_charging_time_sensor_ = sensor;
  }

  void set_reset_button(ESP32EVSEResetButton *btn) { this->reset_button_ = btn; }
  void set_authorize_button(ESP32EVSEAuthorizeButton *btn) { this->authorize_button_ = btn; }

  void set_pending_authorization_binary_sensor(ESP32EVSEPendingAuthorizationBinarySensor *bs) {
    this->pending_authorization_binary_sensor_ = bs;
  }
  void set_wifi_connected_binary_sensor(ESP32EVSEWifiConnectedBinarySensor *bs) {
    this->wifi_connected_binary_sensor_ = bs;
  }

  // Methods that enqueue UART requests to refresh EVSE state.  These are called
  // during setup and from entity actions (for example, when a user toggles a
  // switch) so the ESPHome representation stays in sync with the charger.
  void request_state_update();
  void request_enable_update();
  void request_temperature_update();
  void request_charging_current_update();
  void request_emeter_power_update();
  void request_emeter_session_time_update();
  void request_emeter_charging_time_update();
  void request_chip_update();
  void request_version_update();
  void request_idf_version_update();
  void request_build_time_update();
  void request_device_time_update();
  void request_wifi_sta_cfg_update();
  void request_wifi_sta_ip_update();
  void request_wifi_sta_mac_update();
  void request_device_name_update();
  void request_available_update();
  void request_request_authorization_update();
  void request_heap_update();
  void request_energy_consumption_update();
  void request_total_energy_consumption_update();
  void request_voltage_update();
  void request_current_update();
  void request_wifi_status_update();
  void request_default_charging_current_update();
  void request_maximum_charging_current_update();
  void request_consumption_limit_update();
  void request_default_consumption_limit_update();
  void request_charging_time_limit_update();
  void request_default_charging_time_limit_update();
  void request_under_power_limit_update();
  void request_default_under_power_limit_update();
  void request_pending_authorization_update();

  // Writers mirror user initiated actions back to the EVSE controller.
  void write_enable_state(bool enabled);
  void write_available_state(bool available);
  void write_request_authorization_state(bool request);
  void write_charging_current(float current);
  void write_number_value(ESP32EVSEChargingCurrentNumber *number, float value);

  // Helpers for managing optional high-frequency subscriptions exposed by the
  // EVSE firmware (for example, power telemetry feeds).
  void at_sub(const std::string &command, uint32_t period_ms);
  void at_unsub(const std::string &command = "");
  void send_reset_command();
  void send_authorize_command();

 protected:
  // Commands are queued while we wait for acknowledgements from the EVSE; this
  // struct tracks their progress and callbacks.
  struct PendingCommand {
    std::string command;
    std::function<void(bool)> callback;
    uint32_t start_time{0};
    bool sent{false};
  };

  void process_line_(const std::string &line);
  void handle_ack_(bool success);
  void process_next_command_();
  void update_state_(uint8_t state);
  void update_enable_(bool enable);
  void update_temperature_(int count, int32_t high, int32_t low);
  void update_charging_current_(uint16_t value_tenths);
  void update_emeter_power_(uint32_t power_w);
  void update_emeter_session_time_(uint32_t time_s);
  void update_emeter_charging_time_(uint32_t time_s);
  void update_chip_(const std::string &chip);
  void update_version_(const std::string &version);
  void update_idf_version_(const std::string &idf_version);
  void update_build_time_(const std::string &build_time);
  void update_device_time_(uint32_t timestamp);
  void update_wifi_sta_cfg_(const std::string &ssid);
  void update_wifi_sta_ip_(const std::string &ip);
  void update_wifi_sta_mac_(const std::string &mac);
  void update_device_name_(const std::string &name);
  void update_available_(bool available);
  void update_request_authorization_(bool request);
  void update_heap_(std::optional<uint32_t> heap_used_bytes,
                    std::optional<uint32_t> heap_total_bytes);
  void update_energy_consumption_(float value);
  void update_total_energy_consumption_(float value);
  void update_voltages_(float l1, float l2, float l3);
  void update_currents_(float l1, float l2, float l3);
  void update_wifi_status_(bool connected, int rssi);
  void update_default_charging_current_(uint16_t value_tenths);
  void update_maximum_charging_current_(uint16_t value_amps);
  void update_consumption_limit_(float value);
  void update_default_consumption_limit_(float value);
  void update_charging_time_limit_(uint32_t value);
  void update_default_charging_time_limit_(uint32_t value);
  void update_under_power_limit_(float value);
  void update_default_under_power_limit_(float value);
  void update_pending_authorization_(bool pending);

  bool send_command_(const std::string &command, std::function<void(bool)> callback = nullptr);
  void request_number_update_(ESP32EVSEChargingCurrentNumber *number);
  void publish_scaled_number_(ESP32EVSEChargingCurrentNumber *number, float raw_value);
  void publish_text_sensor_state_(text_sensor::TextSensor *sensor, const std::string &state);
  bool is_valid_subscription_argument_(const std::string &argument) const;

  // Entity pointers registered via the setter functions above.  We guard every
  // usage with a nullptr check so optional sensors don't consume memory when
  // omitted from the configuration.
  text_sensor::TextSensor *state_text_sensor_{nullptr};
  text_sensor::TextSensor *chip_text_sensor_{nullptr};
  text_sensor::TextSensor *version_text_sensor_{nullptr};
  text_sensor::TextSensor *idf_version_text_sensor_{nullptr};
  text_sensor::TextSensor *build_time_text_sensor_{nullptr};
  text_sensor::TextSensor *device_time_text_sensor_{nullptr};
  text_sensor::TextSensor *wifi_sta_ssid_text_sensor_{nullptr};
  text_sensor::TextSensor *wifi_sta_ip_text_sensor_{nullptr};
  text_sensor::TextSensor *wifi_sta_mac_text_sensor_{nullptr};
  text_sensor::TextSensor *device_name_text_sensor_{nullptr};

  ESP32EVSEEnableSwitch *enable_switch_{nullptr};
  ESP32EVSEAvailableSwitch *available_switch_{nullptr};
  ESP32EVSERequestAuthorizationSwitch *request_authorization_switch_{nullptr};

  sensor::Sensor *temperature_high_sensor_{nullptr};
  sensor::Sensor *temperature_low_sensor_{nullptr};
  sensor::Sensor *heap_used_sensor_{nullptr};
  sensor::Sensor *heap_total_sensor_{nullptr};
  sensor::Sensor *energy_consumption_sensor_{nullptr};
  sensor::Sensor *total_energy_consumption_sensor_{nullptr};
  sensor::Sensor *voltage_l1_sensor_{nullptr};
  sensor::Sensor *voltage_l2_sensor_{nullptr};
  sensor::Sensor *voltage_l3_sensor_{nullptr};
  sensor::Sensor *current_l1_sensor_{nullptr};
  sensor::Sensor *current_l2_sensor_{nullptr};
  sensor::Sensor *current_l3_sensor_{nullptr};
  sensor::Sensor *wifi_rssi_sensor_{nullptr};

  ESP32EVSEChargingCurrentNumber *charging_current_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *default_charging_current_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *maximum_charging_current_number_{nullptr};
  float maximum_charging_current_limit_{std::numeric_limits<float>::quiet_NaN()};
  ESP32EVSEChargingCurrentNumber *consumption_limit_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *default_consumption_limit_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *charging_time_limit_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *default_charging_time_limit_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *under_power_limit_number_{nullptr};
  ESP32EVSEChargingCurrentNumber *default_under_power_limit_number_{nullptr};

  sensor::Sensor *emeter_power_sensor_{nullptr};
  sensor::Sensor *emeter_session_time_sensor_{nullptr};
  sensor::Sensor *emeter_charging_time_sensor_{nullptr};

  ESP32EVSEResetButton *reset_button_{nullptr};
  ESP32EVSEAuthorizeButton *authorize_button_{nullptr};

  ESP32EVSEPendingAuthorizationBinarySensor *pending_authorization_binary_sensor_{nullptr};
  ESP32EVSEWifiConnectedBinarySensor *wifi_connected_binary_sensor_{nullptr};

  // UART receive buffer and queue of in-flight commands awaiting responses.
  std::string read_buffer_;
  std::deque<PendingCommand> pending_commands_;
};

// Lightweight wrappers for the ESPHome entity classes.  They forward state
// changes initiated from external clients back to the component implementation.
class ESP32EVSEEnableSwitch : public switch_::Switch, public Parented<ESP32EVSEComponent> {
 protected:
  void write_state(bool state) override;
};

class ESP32EVSEAvailableSwitch : public switch_::Switch, public Parented<ESP32EVSEComponent> {
 protected:
  void write_state(bool state) override;
};

class ESP32EVSERequestAuthorizationSwitch
    : public switch_::Switch, public Parented<ESP32EVSEComponent> {
 protected:
  void write_state(bool state) override;
};

// Numbers represent adjustable EVSE parameters.  The multiplier bridges between
// human-friendly units and the scaled integers required by the UART protocol.
class ESP32EVSEChargingCurrentNumber : public number::Number, public Parented<ESP32EVSEComponent> {
 public:
  ESP32EVSEChargingCurrentNumber();
  void set_command(const std::string &command) { this->command_ = command; }
  void set_multiplier(float multiplier) { this->multiplier_ = multiplier; }
  const std::string &get_command() const { return this->command_; }
  float get_multiplier() const { return this->multiplier_; }

 protected:
  void control(float value) override;

  std::string command_{"AT+CHCUR"};
  float multiplier_{10.0f};
};

// Buttons simply trigger their associated EVSE command when pressed.
class ESP32EVSEResetButton : public button::Button, public Parented<ESP32EVSEComponent> {
 protected:
  void press_action() override;
};

class ESP32EVSEAuthorizeButton : public button::Button, public Parented<ESP32EVSEComponent> {
 protected:
  void press_action() override;
};

class ESP32EVSEPendingAuthorizationBinarySensor
    : public binary_sensor::BinarySensor,
      public Parented<ESP32EVSEComponent> {};

class ESP32EVSEWifiConnectedBinarySensor : public binary_sensor::BinarySensor,
                                           public Parented<ESP32EVSEComponent> {};

template<typename... Ts> class ESP32EVSEAutoUpdateAction : public automation::Action<Ts...> {
 public:
  explicit ESP32EVSEAutoUpdateAction(ESP32EVSEComponent *parent) : parent_(parent) {}

  void set_command(const std::string &command) { this->command_ = command; }
  TEMPLATABLE_VALUE(uint32_t, period)

  void play(Ts... x) override {
    if (this->parent_ == nullptr)
      return;
    if (this->command_.empty())
      return;
    std::string command = this->command_;
    if (!command.empty() && command.front() != '"')
      command = "\"" + command + "\"";
    uint32_t period = this->period_.value(x...);
    if (period == 0) {
      this->parent_->at_unsub(command);
    } else {
      this->parent_->at_sub(command, period);
    }
  }

 protected:
  ESP32EVSEComponent *parent_;
  std::string command_;
};

}  // namespace esp32evse
}  // namespace esphome
