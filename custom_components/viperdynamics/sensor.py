"""Sensor entity: linked game character (Nether Portal / Dark Portal player mode)."""

from __future__ import annotations

from typing import Any

from homeassistant.components.sensor import SensorEntity
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    if "player" in coordinator.capabilities:
        async_add_entities([ViperPlayerSensor(coordinator)])


class ViperPlayerSensor(ViperEntity, SensorEntity):
    _attr_icon = "mdi:account-circle"

    def __init__(self, coordinator: ViperCoordinator) -> None:
        super().__init__(coordinator, "player")

    @property
    def _player(self) -> dict[str, Any]:
        return self.coordinator.data.get("player") or {}

    @property
    def native_value(self) -> str | None:
        return self._player.get("name") or None

    @property
    def extra_state_attributes(self) -> dict[str, Any]:
        return {k: v for k, v in self._player.items() if k != "name"}
