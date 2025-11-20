"""Constants for Iceland Energy Prices integration."""
from typing import Final

DOMAIN: Final = "iceland_energy_prices"
DEFAULT_NAME: Final = "Iceland Energy Price"
DEFAULT_UPDATE_INTERVAL: Final = 24  # hours

# Configuration keys
CONF_PROVIDER: Final = "provider"
CONF_UPDATE_INTERVAL: Final = "update_interval"

# Data URL
DATA_URL: Final = "https://aurbjorg.is/en/samanburdur/rafmagn"

# Energy providers in Iceland
PROVIDERS: Final = {
    "orkusalan": "Orkusalan",
    "straumlind": "Straumlind",
    "orkubu_vestfjarda": "Orkubú Vestfjarða",
    "atlantsorka": "Atlantsorka",
    "orka_heimilanna": "Orka Heimilanna",
    "n1_rafmagn": "N1 Rafmagn",
    "orka_natturunnar": "Orka náttúrunnar",
    "hs_orka": "HS Orka",
}

# Price types
PRICE_GENERAL: Final = "general_price"
PRICE_SPECIAL: Final = "special_price"
PRICE_ORIGIN_GUARANTEE: Final = "origin_guarantee_price"
PRICE_AVERAGE_COST: Final = "average_cost"