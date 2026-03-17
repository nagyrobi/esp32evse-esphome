# ESP32EVSE contribution-guide compliance audit

Source checked: <https://developers.esphome.io/contributing/code/>.

## Scope

Reviewed files under `components/esp32evse/` for:

- C++ style requirements (snake_case naming, no tabs, <= 120 char lines, avoid `#define` for constants).
- Python component conventions (`CONFIG_SCHEMA`, `FINAL_VALIDATE_SCHEMA`, codegen patterns).
- Memory-management guidance for ESP devices (minimize recurring heap allocations in hot paths such as `loop()` and response parsing).

## Findings

### ✅ Matches guide requirements

1. **Formatting/style baseline looks compliant**
   - No tab characters and no lines over 120 chars were found in `components/esp32evse/*`.
2. **Constants use `constexpr` / fixed-size storage instead of macros**
   - The C++ implementation uses `constexpr` constants and fixed-size buffers (`CommandString`, `std::array`) rather than preprocessor constants for runtime values.
3. **Encapsulation pattern is mostly aligned**
   - Mutable component state is mostly private/protected with public setter methods for generated entities.
4. **Python integration structure follows ESPHome conventions**
   - Uses `CONFIG_SCHEMA`, `FINAL_VALIDATE_SCHEMA`, and `to_code()` with generated IDs and UART registration.

### ⚠️ Gaps against guide intent

1. **Hidden heap allocations remain in parsing/runtime paths**
   - Response parsing relies heavily on `std::string` creation/copies and `std::vector<std::string>` tokenization helpers.
   - These allocations can occur repeatedly while processing UART responses, which conflicts with the guide's preference to avoid ongoing heap churn on long-lived embedded devices.
2. **One explicit dynamic allocation in component member initialization**
   - `ready_trigger_` is created with `new Trigger<>()`. While common in ESPHome internals, it is still a heap allocation and should be evaluated against the stricter memory-fragmentation guidance.

## Verdict

**Partially compliant**.

- The component appears compliant with style and schema conventions.
- It is **not fully aligned** with the memory-management section of the contribution guide due to recurring `std::string`/`std::vector` allocations in UART parsing paths.

## Suggested fixes for findings

### Fix set A: Remove recurring heap churn from response parsing

1. **Replace `split_and_trim()` vector returns with in-place token walkers**
   - Current behavior allocates one dynamic container (`std::vector`) and multiple dynamic strings for each parsed line.
   - Proposed approach:
     - Keep the input line in `read_buffer_`.
     - Parse by index/range (`start`, `end`) and handle each token immediately.
     - Only construct a `std::string` when publishing to an API that explicitly requires ownership.

2. **Convert `trim_copy()` to range-based trimming**
   - Current behavior copies the full source string before trimming.
   - Proposed approach:
     - Add helper returning `(start, end)` bounds over `const char *` / `std::string_view`.
     - Defer materialization into a `std::string` until the final publish step.

3. **Avoid temporary strings in simple numeric handlers**
   - For responses that only produce numbers, parse directly from the raw C-string and avoid intermediary `std::string` instances.

4. **Prefer fixed-capacity local buffers for small formatting tasks**
   - For simple response rewriting/sanitization, use stack `char` buffers and bounded writes where possible.

### Fix set B: Address explicit dynamic allocation in member initialization

1. **Replace heap-allocated trigger with value member**
   - Current code uses `Trigger<> *ready_trigger_{new Trigger<>()};`.
   - Proposed approach:
     - Store `Trigger<> ready_trigger_{};` directly as a member.
     - Return `&this->ready_trigger_` from `get_ready_trigger()`.
   - Benefit: removes one permanent heap allocation and aligns better with fragmentation guidance.

2. **If pointer-based trigger is required by framework constraints**
   - Keep pointer semantics, but initialize once in `setup()` from a statically owned storage pattern and document rationale in comments.

### Prioritized implementation order

1. Trigger allocation change (`ready_trigger_`) — low risk, quick win.
2. Replace vector-based tokenization in the hottest parsing branches.
3. Migrate remaining parsing helpers to range-based/string-view style.
4. Re-profile heap behavior over long uptime and confirm reduced fragmentation pressure.
