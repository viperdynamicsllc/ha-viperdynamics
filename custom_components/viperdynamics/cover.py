"""Cover entity: the Stargate iris/gate."""

from __future__ import annotations

from typing import Any

from homeassistant.components.cover import CoverDeviceClass, CoverEntity, CoverEntityFeature
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
    if "gate" in coordinator.capabilities:
        async_add_entities([ViperGate(coordinator)])


class ViperGate(ViperEntity, CoverEntity):
    _attr_device_class = CoverDeviceClass.GATE
    _attr_supported_features = CoverEntityFeature.OPEN | CoverEntityFeature.CLOSE

    def __init__(self, coordinator: ViperCoordinator) -> None:
        super().__init__(coordinator, "gate")

    @property
    def _gate(self) -> dict[str, Any]:
        return self.coordinator.data.get("gate") or {}

    @property
    def is_closed(self) -> bool | None:
        if "open" not in self._gate:
            return None
        return not self._gate["open"]

    @property
    def is_opening(self) -> bool:
        # The firmware only reports "busy"; while busy it is heading away from its last state.
        return bool(self._gate.get("busy")) and not self._gate.get("open")

    @property
    def is_closing(self) -> bool:
        return bool(self._gate.get("busy")) and bool(self._gate.get("open"))

    async def async_open_cover(self, **kwargs: Any) -> None:
        await self.coordinator.async_control(gate="open")

    async def async_close_cover(self, **kwargs: Any) -> None:
        await self.coordinator.async_control(gate="close")
