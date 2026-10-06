"""Viper Dynamics smart devices."""

from __future__ import annotations

from pathlib import Path

from homeassistant.components.http import StaticPathConfig
from homeassistant.const import CONF_HOST, Platform
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import ConfigEntryNotReady
from homeassistant.helpers import config_validation as cv
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.typing import ConfigType

from .api import ViperClient, ViperError
from .const import DOMAIN, STATIC_URL
from .coordinator import ViperConfigEntry, ViperCoordinator

PLATFORMS = [
    Platform.BUTTON,
    Platform.COVER,
    Platform.IMAGE,
    Platform.NUMBER,
    Platform.SELECT,
    Platform.SENSOR,
    Platform.SWITCH,
    Platform.UPDATE,
]

CONFIG_SCHEMA = cv.config_entry_only_config_schema(DOMAIN)

IMAGES_DIR = Path(__file__).parent / "static"


async def async_register_static(hass: HomeAssistant) -> None:
    """Serve product photos at /viperdynamics_static/<model>.png (once)."""
    if hass.data.setdefault(DOMAIN, {}).get("static"):
        return
    hass.data[DOMAIN]["static"] = True
    await hass.http.async_register_static_paths(
        [StaticPathConfig(STATIC_URL, str(IMAGES_DIR), True)]
    )


async def async_setup(hass: HomeAssistant, config: ConfigType) -> bool:
    await async_register_static(hass)
    return True


async def async_setup_entry(hass: HomeAssistant, entry: ViperConfigEntry) -> bool:
    client = ViperClient(async_get_clientsession(hass), entry.data[CONF_HOST])
    try:
        info = await client.get_info()
    except ViperError as err:
        raise ConfigEntryNotReady(str(err)) from err

    coordinator = ViperCoordinator(hass, entry, client, info)
    await coordinator.async_config_entry_first_refresh()
    entry.runtime_data = coordinator

    await hass.config_entries.async_forward_entry_setups(entry, PLATFORMS)
    return True


async def async_unload_entry(hass: HomeAssistant, entry: ViperConfigEntry) -> bool:
    return await hass.config_entries.async_unload_platforms(entry, PLATFORMS)
