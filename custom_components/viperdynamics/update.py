"""Firmware update entity, backed by the device's own OTA manifest check."""

from __future__ import annotations

from typing import Any

from homeassistant.components.update import UpdateEntity, UpdateEntityFeature
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 1


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    if "ota" in coordinator.capabilities:
        async_add_entities([ViperUpdate(coordinator)])


class ViperUpdate(ViperEntity, UpdateEntity):
    def __init__(self, coordinator: ViperCoordinator) -> None:
        super().__init__(coordinator, "firmware")

    @property
    def _update(self) -> dict[str, Any]:
        return self.coordinator.data.get("update") or {}

    @property
    def supported_features(self) -> UpdateEntityFeature:
        features = UpdateEntityFeature.RELEASE_NOTES
        # Devices that can only be updated from their own web page say so.
        if self._update.get("can_install", True):
            features |= UpdateEntityFeature.INSTALL | UpdateEntityFeature.PROGRESS
        return features

    @property
    def installed_version(self) -> str | None:
        return self._update.get("installed") or self.coordinator.info.get("fw")

    @property
    def latest_version(self) -> str | None:
        # No manifest result yet: report "up to date" rather than unknown.
        return self._update.get("latest") or self.installed_version

    @property
    def in_progress(self) -> bool:
        return bool(self._update.get("in_progress"))

    @property
    def update_percentage(self) -> int | None:
        return self._update.get("percent") if self.in_progress else None

    async def async_release_notes(self) -> str | None:
        return self._update.get("notes") or None

    async def async_install(self, version: str | None, backup: bool, **kwargs: Any) -> None:
        await self.coordinator.async_control(action="install_update")
