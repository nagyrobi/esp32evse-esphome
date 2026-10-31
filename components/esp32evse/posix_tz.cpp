#include "posix_tz.h"

namespace esphome {
namespace esp32evse {

namespace {

constexpr int64_t SECONDS_PER_DAY = 86400;
constexpr int32_t DEFAULT_TRANSITION_TIME = 7200;  // 02:00 local time
constexpr int32_t MAX_OFFSET_HOURS = 24;
constexpr int32_t MAX_TRANSITION_HOURS = 167;

bool is_digit(char c) { return c >= '0' && c <= '9'; }
bool is_alpha(char c) { return (c >= 'a' && c <= 'z') || (c >= 'A' && c <= 'Z'); }

int64_t floor_div(int64_t a, int64_t b) {
  int64_t q = a / b;
  if ((a % b != 0) && ((a < 0) != (b < 0)))
    --q;
  return q;
}

bool is_leap_year(int64_t year) { return (year % 4 == 0 && year % 100 != 0) || year % 400 == 0; }

int days_in_month(int64_t year, unsigned month) {
  static constexpr uint8_t DAYS[12] = {31, 28, 31, 30, 31, 30, 31, 31, 30, 31, 30, 31};
  if (month == 2 && is_leap_year(year))
    return 29;
  return DAYS[month - 1];
}

// Days since 1970-01-01 of a proleptic Gregorian date (H. Hinnant's algorithm).
int64_t days_from_civil(int64_t year, unsigned month, unsigned day) {
  year -= month <= 2;
  const int64_t era = (year >= 0 ? year : year - 399) / 400;
  const unsigned yoe = static_cast<unsigned>(year - era * 400);
  const unsigned doy = (153 * (month > 2 ? month - 3 : month + 9) + 2) / 5 + day - 1;
  const unsigned doe = yoe * 365 + yoe / 4 - yoe / 100 + doy;
  return era * 146097 + static_cast<int64_t>(doe) - 719468;
}

void civil_from_days(int64_t days, int64_t &year, unsigned &month, unsigned &day) {
  days += 719468;
  const int64_t era = (days >= 0 ? days : days - 146096) / 146097;
  const unsigned doe = static_cast<unsigned>(days - era * 146097);
  const unsigned yoe = (doe - doe / 1460 + doe / 36524 - doe / 146096) / 365;
  const unsigned doy = doe - (365 * yoe + yoe / 4 - yoe / 100);
  const unsigned mp = (5 * doy + 2) / 153;
  day = doy - (153 * mp + 2) / 5 + 1;
  month = mp < 10 ? mp + 3 : mp - 9;
  year = static_cast<int64_t>(yoe) + era * 400 + (month <= 2);
}

int weekday_from_days(int64_t days) {
  int64_t wday = (days + 4) % 7;  // 1970-01-01 was a Thursday
  if (wday < 0)
    wday += 7;
  return static_cast<int>(wday);
}

// Up to max_digits decimal digits, at least one.
bool parse_number(const char *&p, int max_digits, int32_t &value) {
  if (!is_digit(*p))
    return false;
  int32_t result = 0;
  for (int i = 0; i < max_digits && is_digit(*p); ++i, ++p)
    result = result * 10 + (*p - '0');
  if (is_digit(*p))
    return false;
  value = result;
  return true;
}

// Zone designation: at least three letters, or the quoted form "<+0530>".
bool parse_name(const char *&p) {
  const char *start = p;
  if (*p == '<') {
    start = ++p;
    while (is_alpha(*p) || is_digit(*p) || *p == '+' || *p == '-')
      ++p;
    if (*p != '>' || p - start < 3)
      return false;
    ++p;
    return true;
  }
  while (is_alpha(*p))
    ++p;
  return p - start >= 3;
}

// [+|-]hh[:mm[:ss]]
bool parse_hms(const char *&p, int32_t max_hours, int32_t &seconds) {
  int32_t sign = 1;
  if (*p == '+' || *p == '-') {
    if (*p == '-')
      sign = -1;
    ++p;
  }
  int32_t hours = 0;
  int32_t minutes = 0;
  int32_t secs = 0;
  if (!parse_number(p, 3, hours) || hours > max_hours)
    return false;
  if (*p == ':') {
    ++p;
    if (!parse_number(p, 2, minutes) || minutes > 59)
      return false;
    if (*p == ':') {
      ++p;
      if (!parse_number(p, 2, secs) || secs > 59)
        return false;
    }
  }
  seconds = sign * (hours * 3600 + minutes * 60 + secs);
  return true;
}

// Mm.w.d, Jn or n, optionally followed by /time.
bool parse_rule(const char *&p, PosixTzRule &rule) {
  int32_t a = 0;
  int32_t b = 0;
  int32_t c = 0;
  if (*p == 'M') {
    ++p;
    if (!parse_number(p, 2, a) || a < 1 || a > 12 || *p++ != '.')
      return false;
    if (!parse_number(p, 1, b) || b < 1 || b > 5 || *p++ != '.')
      return false;
    if (!parse_number(p, 1, c) || c > 6)
      return false;
    rule.type = PosixTzRule::Type::MONTH_WEEK_DAY;
    rule.month = static_cast<uint8_t>(a);
    rule.week = static_cast<uint8_t>(b);
    rule.weekday = static_cast<uint8_t>(c);
  } else if (*p == 'J') {
    ++p;
    if (!parse_number(p, 3, a) || a < 1 || a > 365)
      return false;
    rule.type = PosixTzRule::Type::JULIAN_NO_LEAP;
    rule.day = static_cast<uint16_t>(a);
  } else {
    if (!parse_number(p, 3, a) || a > 365)
      return false;
    rule.type = PosixTzRule::Type::DAY_OF_YEAR;
    rule.day = static_cast<uint16_t>(a);
  }
  rule.time = DEFAULT_TRANSITION_TIME;
  if (*p == '/') {
    ++p;
    if (!parse_hms(p, MAX_TRANSITION_HOURS, rule.time))
      return false;
  }
  return true;
}

// Days since 1970-01-01 of the day the rule selects in the given year.
int64_t rule_day(int64_t year, const PosixTzRule &rule) {
  const int64_t jan1 = days_from_civil(year, 1, 1);
  switch (rule.type) {
    case PosixTzRule::Type::JULIAN_NO_LEAP:
      return jan1 + rule.day - 1 + ((is_leap_year(year) && rule.day >= 60) ? 1 : 0);
    case PosixTzRule::Type::DAY_OF_YEAR:
      return jan1 + rule.day;
    case PosixTzRule::Type::MONTH_WEEK_DAY:
    default: {
      const int64_t first = days_from_civil(year, rule.month, 1);
      int mday = 1 + (rule.weekday - weekday_from_days(first) + 7) % 7 + (rule.week - 1) * 7;
      const int last = days_in_month(year, rule.month);
      while (mday > last)
        mday -= 7;  // week 5 means "last"
      return first + mday - 1;
    }
  }
}

// UTC epoch of a transition: rule time is given in the local time in effect before it.
int64_t transition_utc(int64_t year, const PosixTzRule &rule, int32_t offset_before) {
  return rule_day(year, rule) * SECONDS_PER_DAY + rule.time + offset_before;
}

bool is_dst(int64_t utc, const PosixTz &tz) {
  if (!tz.has_dst)
    return false;
  int64_t year;
  unsigned month;
  unsigned day;
  civil_from_days(floor_div(utc - tz.std_offset, SECONDS_PER_DAY), year, month, day);
  for (int64_t y = year - 1; y <= year + 1; ++y) {
    const int64_t start = transition_utc(y, tz.dst_start, tz.std_offset);
    int64_t end = transition_utc(y, tz.dst_end, tz.dst_offset);
    if (end < start)  // southern hemisphere: DST spans the new year
      end = transition_utc(y + 1, tz.dst_end, tz.dst_offset);
    if (utc >= start && utc < end)
      return true;
  }
  return false;
}

}  // namespace

bool parse_posix_tz(const char *str, PosixTz &out) {
  if (str == nullptr)
    return false;
  const char *p = str;
  PosixTz tz;
  if (!parse_name(p) || !parse_hms(p, MAX_OFFSET_HOURS, tz.std_offset))
    return false;
  if (*p == '\0') {
    out = tz;
    return true;
  }
  if (!parse_name(p))
    return false;
  tz.has_dst = true;
  tz.dst_offset = tz.std_offset - 3600;
  if (*p != ',' && *p != '\0' && !parse_hms(p, MAX_OFFSET_HOURS, tz.dst_offset))
    return false;
  if (*p == '\0') {
    // No transition rules given: libc falls back to the US rules.
    tz.dst_start.month = 3;
    tz.dst_start.week = 2;
    tz.dst_end.month = 11;
    tz.dst_end.week = 1;
  } else {
    if (*p++ != ',' || !parse_rule(p, tz.dst_start) || *p++ != ',' || !parse_rule(p, tz.dst_end) || *p != '\0')
      return false;
  }
  out = tz;
  return true;
}

void posix_tz_to_local(int64_t utc, const PosixTz &tz, struct tm &out) {
  const bool dst = is_dst(utc, tz);
  const int64_t local = utc - (dst ? tz.dst_offset : tz.std_offset);
  const int64_t days = floor_div(local, SECONDS_PER_DAY);
  const int64_t secs = local - days * SECONDS_PER_DAY;
  int64_t year;
  unsigned month;
  unsigned day;
  civil_from_days(days, year, month, day);
  out = {};
  out.tm_year = static_cast<int>(year - 1900);
  out.tm_mon = static_cast<int>(month) - 1;
  out.tm_mday = static_cast<int>(day);
  out.tm_hour = static_cast<int>(secs / 3600);
  out.tm_min = static_cast<int>((secs % 3600) / 60);
  out.tm_sec = static_cast<int>(secs % 60);
  out.tm_wday = weekday_from_days(days);
  out.tm_yday = static_cast<int>(days - days_from_civil(year, 1, 1));
  out.tm_isdst = dst ? 1 : 0;
}

}  // namespace esp32evse
}  // namespace esphome
