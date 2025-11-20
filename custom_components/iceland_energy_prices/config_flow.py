"""Config flow for Iceland Energy Prices integration."""
from __future__ import annotations

import logging
from typing import Any

import voluptuous as vol

from homeassistant import config_entries
from homeassistant.core import callback
from homeassistant.data_entry_flow import FlowResult
from homeassistant.helpers.selector import (
    SelectSelector,
    SelectSelectorConfig,
    SelectSelectorMode,
)

from .const import CONF_PROVIDER, CONF_UPDATE_INTERVAL, DOMAIN, PROVIDERS

_LOGGER = logging.getLogger(__name__)


class IcelandEnergyPricesConfigFlow(config_entries.ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Iceland Energy Prices."""

    VERSION = 1

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Handle the initial step."""
        errors: dict[str, str] = {}

        if user_input is not None:
            # Create a unique ID based on the provider
            await self.async_set_unique_id(
                f"{DOMAIN}_{user_input[CONF_PROVIDER]}"
            )
            self._abort_if_unique_id_configured()

            return self.async_create_entry(
                title=PROVIDERS[user_input[CONF_PROVIDER]],
                data=user_input,
            )

        # Show configuration form with provider dropdown
        data_schema = vol.Schema(
            {
                vol.Required(CONF_PROVIDER): SelectSelector(
                    SelectSelectorConfig(
                        options=list(PROVIDERS.keys()),
                        mode=SelectSelectorMode.DROPDOWN,
                        translation_key="provider",
                    )
                ),
            }
        )

        return self.async_show_form(
            step_id="user",
            data_schema=data_schema,
            errors=errors,
        )

    @staticmethod
    @callback
    def async_get_options_flow(
        config_entry: config_entries.ConfigEntry,
    ) -> OptionsFlowHandler:
        """Get the options flow for this handler."""
        return OptionsFlowHandler(config_entry)


class OptionsFlowHandler(config_entries.OptionsFlow):
    """Handle options flow for Iceland Energy Prices."""

    def __init__(self, config_entry: config_entries.ConfigEntry) -> None:
        """Initialize options flow."""
        self.config_entry = config_entry

    async def async_step_init(
        self, user_input: dict[str, Any] | None = None
    ) -> FlowResult:
        """Manage the options."""
        if user_input is not None:
            return self.async_create_entry(data=user_input)

        return self.async_show_form(
            step_id="init",
            data_schema=vol.Schema(
                {
                    vol.Optional(
                        CONF_UPDATE_INTERVAL,
                        default=self.config_entry.options.get(
                            CONF_UPDATE_INTERVAL, 24
                        ),
                    ): vol.All(vol.Coerce(int), vol.Range(min=1, max=168)),
                }
            ),
        )