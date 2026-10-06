"""Switch entities: automatic backlight, sound."""

from __future__ import annotations

from typing import Any

from homeassistant.components.switch import SwitchEntity, SwitchEntityDescription
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 1

SWITCHES = (
    SwitchEntityDescription(key="backlight_auto", icon="mdi:theme-light-dark"),
    SwitchEntityDescription(key="sound", icon="mdi:music-note"),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        ViperSwitch(coordinator, desc)
        for desc in SWITCHES
        if desc.key in coordinator.capabilities
    )


class ViperSwitch(ViperEntity, SwitchEntity):
    def __init__(self, coordinator: ViperCoordinator, description: SwitchEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    @property
    def is_on(self) -> bool | None:
        return self.coordinator.data.get(self.entity_description.key)

    async def async_turn_on(self, **kwargs: Any) -> None:
        await self.coordinator.async_control(**{self.entity_description.key: True})

    async def async_turn_off(self, **kwargs: Any) -> None:
        await self.coordinator.async_control(**{self.entity_description.key: False})
