"""HTTP client for the Viper HA API (see docs/api.md)."""

from __future__ import annotations

import asyncio
from typing import Any

import aiohttp

TIMEOUT = aiohttp.ClientTimeout(total=8)


class ViperError(Exception):
    """Device could not be reached or returned an error."""


class ViperClient:
    """Talks to one device."""

    def __init__(self, session: aiohttp.ClientSession, host: str) -> None:
        self._session = session
        self.host = host

    @property
    def base_url(self) -> str:
        return f"http://{self.host}"

    async def _request(self, method: str, path: str, json: Any = None) -> dict[str, Any]:
        try:
            async with self._session.request(
                method, f"{self.base_url}{path}", json=json, timeout=TIMEOUT
            ) as resp:
                if resp.status != 200:
                    raise ViperError(f"{path} returned HTTP {resp.status}: {await resp.text()}")
                return await resp.json(content_type=None)
        except (aiohttp.ClientError, asyncio.TimeoutError, ValueError) as err:
            raise ViperError(f"{path} failed: {err}") from err

    async def get_info(self) -> dict[str, Any]:
        return await self._request("GET", "/api/info")

    async def get_state(self) -> dict[str, Any]:
        return await self._request("GET", "/api/state")

    async def control(self, **values: Any) -> dict[str, Any]:
        return await self._request("POST", "/api/control", json=values)
