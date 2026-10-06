"""Constants for the Viper Dynamics integration."""

from datetime import timedelta

DOMAIN = "viperdynamics"
MANUFACTURER = "Viper Dynamics"
SCAN_INTERVAL = timedelta(seconds=10)

STATIC_URL = f"/{DOMAIN}_static"

MODEL_NAMES = {
    "stargate_p1s": "Stargate P1S",
    "stargate_p3m": "Stargate P3M",
    "stargate_p4x": "Stargate P4X",
    "nether_portal": "Nether Portal",
    "nether_portal_7_pro": "Nether Portal 7 Pro",
    "dark_portal": "WoW Dark Portal",
}

CONF_DEVICE_ID = "device_id"
CONF_MODEL = "model"
