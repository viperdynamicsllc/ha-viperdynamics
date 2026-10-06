"""Polling coordinator for one device."""

from __future__ import annotations

import logging
from typing import Any

from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.exceptions import HomeAssistantError
from homeassistant.helpers.update_coordinator import DataUpdateCoordinator, UpdateFailed

from .api import ViperClient, ViperError
from .const import DOMAIN, SCAN_INTERVAL

_LOGGER = logging.getLogger(__name__)

type ViperConfigEntry = ConfigEntry[ViperCoordinator]


class ViperCoordinator(DataUpdateCoordinator[dict[str, Any]]):
    """Fetches /api/state; holds /api/info from setup."""

    config_entry: ViperConfigEntry

    def __init__(
        self,
        hass: HomeAssistant,
        entry: ViperConfigEntry,
        client: ViperClient,
        info: dict[str, Any],
    ) -> None:
        super().__init__(
            hass,
            _LOGGER,
            config_entry=entry,
            name=f"{DOMAIN} {info.get('name', client.host)}",
            update_interval=SCAN_INTERVAL,
        )
        self.client = client
        self.info = info

    @property
    def capabilities(self) -> set[str]:
        return set(self.info.get("capabilities", []))

    async def _async_update_data(self) -> dict[str, Any]:
        try:
            return await self.client.get_state()
        except ViperError as err:
            raise UpdateFailed(str(err)) from err

    async def async_control(self, **values: Any) -> None:
        """Send a control request and apply the returned state immediately."""
        try:
            state = await self.client.control(**values)
        except ViperError as err:
            raise HomeAssistantError(str(err)) from err
        self.async_set_updated_data(state)
