#pragma once

// Minimal POSIX TZ rule support (e.g. "CET-1CEST,M3.5.0,M10.5.0/3") used to
// render the EVSE clock in the EVSE's own timezone.  The conversion is done
// here instead of through setenv("TZ")/tzset()/localtime_r() because:
//  - newlib never frees the string of an unset environment variable, so
//    toggling TZ on every poll leaked heap until the node crashed;
//  - since ESPHome 2026.3 a configured `time:` timezone overrides
//    localtime_r() and ignores TZ altogether.

#include <cstdint>
#include <ctime>

namespace esphome {
namespace esp32evse {

struct PosixTzRule {
  enum class Type : uint8_t {
    MONTH_WEEK_DAY,  // Mm.w.d
    JULIAN_NO_LEAP,  // Jn, 1..365, February 29 is never counted
    DAY_OF_YEAR,     // n, 0..365, February 29 is counted in leap years
  };
  Type type{Type::MONTH_WEEK_DAY};
  uint8_t month{0};    // 1..12
  uint8_t week{0};     // 1..5, 5 = last
  uint8_t weekday{0};  // 0..6, 0 = Sunday
  uint16_t day{0};     // for JULIAN_NO_LEAP and DAY_OF_YEAR
  int32_t time{7200};  // transition time in seconds after local midnight
};

struct PosixTz {
  int32_t std_offset{0};  // seconds west of UTC (POSIX sign convention)
  int32_t dst_offset{0};
  bool has_dst{false};
  PosixTzRule dst_start{};
  PosixTzRule dst_end{};
};

// Parse a POSIX TZ string.  Returns false (leaving `out` untouched) on any
// syntax error, including rules truncated by the sender.
bool parse_posix_tz(const char *str, PosixTz &out);

// Convert a UTC epoch to broken-down local time for the given timezone.
void posix_tz_to_local(int64_t utc, const PosixTz &tz, struct tm &out);

}  // namespace esp32evse
}  // namespace esphome
