"""Sensor platform for Iceland Energy Prices integration."""
from __future__ import annotations

from datetime import timedelta
import logging
import re
from typing import Any

from bs4 import BeautifulSoup
import requests

from homeassistant.components.sensor import (
    SensorDeviceClass,
    SensorEntity,
    SensorStateClass,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant, callback
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import (
    CoordinatorEntity,
    DataUpdateCoordinator,
    UpdateFailed,
)

from .const import (
    CONF_PROVIDER,
    CONF_UPDATE_INTERVAL,
    DATA_URL,
    DEFAULT_UPDATE_INTERVAL,
    DOMAIN,
    PRICE_AVERAGE_COST,
    PRICE_GENERAL,
    PRICE_ORIGIN_GUARANTEE,
    PRICE_SPECIAL,
    PROVIDERS,
)

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Iceland Energy Prices sensor platform."""
    update_interval = timedelta(
        hours=config_entry.options.get(CONF_UPDATE_INTERVAL, DEFAULT_UPDATE_INTERVAL)
    )

    coordinator = IcelandEnergyPricesCoordinator(
        hass,
        config_entry,
        update_interval,
    )

    # Fetch initial data
    await coordinator.async_config_entry_first_refresh()

    # Create sensor entities for each price type
    entities = [
        IcelandEnergyPriceSensor(
            coordinator,
            config_entry,
            PRICE_GENERAL,
            "General Price",
            "mdi:cash",
        ),
        IcelandEnergyPriceSensor(
            coordinator,
            config_entry,
            PRICE_SPECIAL,
            "Special Price",
            "mdi:cash-multiple",
        ),
        IcelandEnergyPriceSensor(
            coordinator,
            config_entry,
            PRICE_ORIGIN_GUARANTEE,
            "Origin Guarantee Price",
            "mdi:leaf",
        ),
        IcelandEnergyAverageCostSensor(
            coordinator,
            config_entry,
        ),
    ]

    async_add_entities(entities)


class IcelandEnergyPricesCoordinator(DataUpdateCoordinator):
    """Class to manage fetching Iceland energy price data."""

    def __init__(
        self,
        hass: HomeAssistant,
        config_entry: ConfigEntry,
        update_interval: timedelta,
    ) -> None:
        """Initialize coordinator."""
        super().__init__(
            hass,
            _LOGGER,
            name=DOMAIN,
            update_interval=update_interval,
        )
        self.config_entry = config_entry
        self._last_valid_data: dict[str, Any] | None = None

    async def _async_update_data(self) -> dict[str, Any]:
        """Fetch data from the website."""
        try:
            data = await self.hass.async_add_executor_job(
                self._fetch_price_data
            )
            # Cache the last valid result
            self._last_valid_data = data
            return data

        except requests.exceptions.HTTPError as err:
            _LOGGER.error("HTTP error occurred: %s", err)
            if self._last_valid_data:
                _LOGGER.info("Returning cached data due to HTTP error")
                return self._last_valid_data
            raise UpdateFailed(f"HTTP error occurred: {err}") from err

        except requests.exceptions.ConnectionError as err:
            _LOGGER.error("Connection error occurred: %s", err)
            if self._last_valid_data:
                _LOGGER.info("Returning cached data due to connection error")
                return self._last_valid_data
            raise UpdateFailed(f"Connection error occurred: {err}") from err

        except requests.exceptions.Timeout as err:
            _LOGGER.error("Timeout occurred: %s", err)
            if self._last_valid_data:
                _LOGGER.info("Returning cached data due to timeout")
                return self._last_valid_data
            raise UpdateFailed(f"Timeout occurred: {err}") from err

        except ValueError as err:
            _LOGGER.error("Data parsing error: %s", err)
            if self._last_valid_data:
                _LOGGER.info("Returning cached data due to parsing error")
                return self._last_valid_data
            raise UpdateFailed(f"Data parsing error: {err}") from err

        except Exception as err:
            _LOGGER.exception("Unexpected error fetching data")
            if self._last_valid_data:
                _LOGGER.info("Returning cached data due to unexpected error")
                return self._last_valid_data
            raise UpdateFailed(f"Unexpected error: {err}") from err

    def _fetch_price_data(self) -> dict[str, Any]:
        """Fetch and parse price data from the website (blocking)."""
        provider_key = self.config_entry.data[CONF_PROVIDER]
        provider_name = PROVIDERS[provider_key]

        # Fetch webpage with proper headers
        headers = {
            "User-Agent": "HomeAssistant/2025.1 (Iceland Energy Prices Integration)",
            "Accept": "text/html,application/xhtml+xml",
        }

        response = requests.get(DATA_URL, headers=headers, timeout=30)
        response.raise_for_status()

        # Parse HTML
        soup = BeautifulSoup(response.content, "lxml")

        # Find all table rows
        table = soup.find("table")
        if not table:
            raise ValueError("Price comparison table not found on page")

        rows = table.find_all("tr")
        if not rows:
            raise ValueError("No table rows found")

        # Parse the table to find the provider's data
        provider_data = None
        for row in rows:
            cells = row.find_all("td")
            if not cells or len(cells) < 6:
                continue

            # Extract text from cells
            row_text = " ".join(cell.get_text(strip=True) for cell in cells)

            # Check if this row contains our provider
            if provider_name.lower() in row_text.lower():
                provider_data = self._parse_provider_row(cells)
                break

        if not provider_data:
            raise ValueError(f"Provider '{provider_name}' not found in table")

        return {
            "provider": provider_name,
            "prices": provider_data,
            "last_updated": response.headers.get("Date"),
        } 

    def _parse_provider_row(self, cells: list) -> dict[str, float | None]:
        """Parse price values from table cells."""
        prices = {}

        # Helper function to extract numeric value from "kr X.XX" format
        def parse_price(text: str) -> float | None:
            """Parse price from 'kr X.XX' or 'kr X,XXX' format."""
            if not text or text == "-" or text == "":
                return None

            # Match pattern: "kr" followed by number with optional comma/period
            match = re.search(r"kr\s*([0-9]+[,.]?[0-9]*)", text, re.IGNORECASE)
            if match:
                price_str = match.group(1).replace(",", "")
                try:
                    return float(price_str)
                except ValueError:
                    return None
            return None

        # Extract prices from cells (adjust indices based on table structure)
        # Typical structure: [logo, name, general, special, origin, average, notes, button]
        try:
            # Cell index 2: General Price
            if len(cells) > 2:
                prices[PRICE_GENERAL] = parse_price(cells[2].get_text(strip=True))

            # Cell index 3: Special Price
            if len(cells) > 3:
                prices[PRICE_SPECIAL] = parse_price(cells[3].get_text(strip=True))

            # Cell index 4: Origin Guarantee Price
            if len(cells) > 4:
                prices[PRICE_ORIGIN_GUARANTEE] = parse_price(
                    cells[4].get_text(strip=True)
                )

            # Cell index 5: Average Cost
            if len(cells) > 5:
                avg_text = cells[5].get_text(strip=True)
                # Average cost uses comma as thousands separator
                prices[PRICE_AVERAGE_COST] = parse_price(avg_text)

        except Exception as err:
            _LOGGER.error("Error parsing provider row: %s", err)
            raise ValueError(f"Failed to parse price data: {err}") from err

        return prices 


class IcelandEnergyPriceSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Iceland Energy Price Sensor."""

    def __init__(
        self,
        coordinator: IcelandEnergyPricesCoordinator,
        config_entry: ConfigEntry,
        price_type: str,
        name_suffix: str,
        icon: str,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        provider_name = PROVIDERS[config_entry.data[CONF_PROVIDER]]
        self._price_type = price_type
        self._attr_unique_id = f"{config_entry.entry_id}_{price_type}"
        self._attr_name = f"{provider_name} {name_suffix}"
        self._attr_icon = icon

        # Energy dashboard compatibility
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "ISK/kWh"
        self._attr_suggested_display_precision = 2

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "prices" in self.coordinator.data:
            return self.coordinator.data["prices"].get(self._price_type)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "provider": self.coordinator.data.get("provider"),
            "last_updated": self.coordinator.data.get("last_updated"),
            "currency": "ISK",
            "unit": "kr/kWh",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.native_value is not None
        )


class IcelandEnergyAverageCostSensor(CoordinatorEntity, SensorEntity):
    """Representation of an Iceland Energy Average Cost Sensor."""

    def __init__(
        self,
        coordinator: IcelandEnergyPricesCoordinator,
        config_entry: ConfigEntry,
    ) -> None:
        """Initialize the sensor."""
        super().__init__(coordinator)

        provider_name = PROVIDERS[config_entry.data[CONF_PROVIDER]]
        self._attr_unique_id = f"{config_entry.entry_id}_{PRICE_AVERAGE_COST}"
        self._attr_name = f"{provider_name} Average Cost"
        self._attr_icon = "mdi:calculator"

        # This is a total cost, not a rate
        self._attr_device_class = SensorDeviceClass.MONETARY
        self._attr_state_class = SensorStateClass.MEASUREMENT
        self._attr_native_unit_of_measurement = "ISK"
        self._attr_suggested_display_precision = 0

    @property
    def native_value(self) -> float | None:
        """Return the state of the sensor."""
        if self.coordinator.data and "prices" in self.coordinator.data:
            return self.coordinator.data["prices"].get(PRICE_AVERAGE_COST)
        return None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        """Return additional attributes."""
        if not self.coordinator.data:
            return {}

        return {
            "provider": self.coordinator.data.get("provider"),
            "last_updated": self.coordinator.data.get("last_updated"),
            "currency": "ISK",
            "description": "Average annual cost based on standard consumption",
        }

    @property
    def available(self) -> bool:
        """Return if entity is available."""
        return (
            self.coordinator.last_update_success
            and self.coordinator.data is not None
            and self.native_value is not None
        )