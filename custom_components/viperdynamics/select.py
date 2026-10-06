"""Select entities: display mode, clock animation, mascot."""

from __future__ import annotations

from homeassistant.components.select import SelectEntity
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
    caps = coordinator.capabilities
    entities: list[SelectEntity] = []
    if "mode" in caps and coordinator.info.get("modes"):
        entities.append(ViperModeSelect(coordinator))
    for key, options_key in (("clock_anim", "clock_anims"), ("mascot", "mascots")):
        if key in caps and coordinator.info.get(options_key):
            entities.append(ViperListSelect(coordinator, key, options_key))
    async_add_entities(entities)


class ViperModeSelect(ViperEntity, SelectEntity):
    """Display mode; the device reports it as an index into info.modes."""

    def __init__(self, coordinator: ViperCoordinator) -> None:
        super().__init__(coordinator, "mode")
        self._attr_options = list(coordinator.info["modes"])

    @property
    def current_option(self) -> str | None:
        idx = self.coordinator.data.get("mode")
        if isinstance(idx, int) and 0 <= idx < len(self.options):
            return self.options[idx]
        return None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_control(mode=self.options.index(option))


class ViperListSelect(ViperEntity, SelectEntity):
    """String-valued option chosen from a list published in /api/info."""

    def __init__(self, coordinator: ViperCoordinator, key: str, options_key: str) -> None:
        super().__init__(coordinator, key)
        self._key = key
        self._attr_options = list(coordinator.info[options_key])

    @property
    def current_option(self) -> str | None:
        value = self.coordinator.data.get(self._key)
        return value if value in self.options else None

    async def async_select_option(self, option: str) -> None:
        await self.coordinator.async_control(**{self._key: option})
