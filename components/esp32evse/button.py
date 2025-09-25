"""Expose ESP32 EVSE button entities to ESPHome."""

# The imports mirror ESPHome's standard pattern—``codegen`` wires the C++ class,
# ``button`` provides helper factories, and ``config_validation`` ensures the
# YAML blocks are correct before compilation.
import esphome.codegen as cg
from esphome.components import button
import esphome.config_validation as cv
from esphome.const import ENTITY_CATEGORY_DIAGNOSTIC

from . import CONF_ESP32EVSE_ID, ESP32EVSEComponent, esp32evse_ns

DEPENDENCIES = ["esp32evse"]

# Define the lightweight C++ wrappers representing the actions we can trigger
# on the EVSE controller from Home Assistant.
ESP32EVSEResetButton = esp32evse_ns.class_("ESP32EVSEResetButton", button.Button)
ESP32EVSEAuthorizeButton = esp32evse_ns.class_("ESP32EVSEAuthorizeButton", button.Button)

CONF_RESET = "reset"
CONF_AUTHORIZE = "authorize"


CONFIG_SCHEMA = cv.All(
    cv.Schema(
        {
            # Associate the buttons with the parent EVSE component instance.
            cv.GenerateID(CONF_ESP32EVSE_ID): cv.use_id(ESP32EVSEComponent),
            # Reset triggers a soft reboot of the charger, which is useful during
            # troubleshooting.
            cv.Optional(CONF_RESET): button.button_schema(
                ESP32EVSEResetButton,
                icon="mdi:restart",
                entity_category=ENTITY_CATEGORY_DIAGNOSTIC,
            ),
            # Authorize commands the EVSE to start charging the currently
            # connected vehicle if authorization is required.
            cv.Optional(CONF_AUTHORIZE): button.button_schema(
                ESP32EVSEAuthorizeButton,
                icon="mdi:battery-check-outline",
            ),
        }
    ),
    # Ensure at least one button is defined—empty button sections are a common
    # configuration mistake and would otherwise generate unused code.
    cv.has_at_least_one_key(
        CONF_RESET,
        CONF_AUTHORIZE,
    ),
)


async def to_code(config):
    """Create the configured buttons and link them to the EVSE component."""

    parent = await cg.get_variable(config[CONF_ESP32EVSE_ID])

    if reset_config := config.get(CONF_RESET):
        # The reset button sends the ``AT+RESET`` command via UART when pressed.
        btn = await button.new_button(reset_config)
        await cg.register_parented(btn, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_reset_button(btn))
    if authorize_config := config.get(CONF_AUTHORIZE):
        # The authorize button requests the EVSE to begin charging the session.
        btn = await button.new_button(authorize_config)
        await cg.register_parented(btn, config[CONF_ESP32EVSE_ID])
        cg.add(parent.set_authorize_button(btn))
