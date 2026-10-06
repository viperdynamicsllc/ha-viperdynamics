"""Number entities: brightness, volumes, screen rotation."""

from __future__ import annotations

from dataclasses import dataclass

from homeassistant.components.number import NumberEntity, NumberEntityDescription, NumberMode
from homeassistant.const import PERCENTAGE, EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 1


@dataclass(frozen=True, kw_only=True)
class ViperNumberDescription(NumberEntityDescription):
    min_key: str | None = None  # info key overriding native_min_value
    max_key: str | None = None  # info key overriding native_max_value


NUMBERS = (
    ViperNumberDescription(
        key="brightness",
        icon="mdi:brightness-6",
        native_min_value=0,
        native_max_value=100,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
        min_key="brightness_min",
    ),
    ViperNumberDescription(
        key="volume",
        icon="mdi:volume-high",
        native_min_value=0,
        native_max_value=100,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
    ),
    ViperNumberDescription(
        key="alarm_volume",
        icon="mdi:alarm-bell",
        native_min_value=0,
        native_max_value=100,
        native_unit_of_measurement=PERCENTAGE,
        mode=NumberMode.SLIDER,
    ),
    ViperNumberDescription(
        key="rotation",
        icon="mdi:phone-rotate-landscape",
        native_min_value=-10,
        native_max_value=10,
        mode=NumberMode.BOX,
        entity_category=EntityCategory.CONFIG,
        min_key="rotation_min",
        max_key="rotation_max",
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        ViperNumber(coordinator, desc)
        for desc in NUMBERS
        if desc.key in coordinator.capabilities
    )


class ViperNumber(ViperEntity, NumberEntity):
    entity_description: ViperNumberDescription

    def __init__(self, coordinator: ViperCoordinator, description: ViperNumberDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description
        info = coordinator.info
        if description.min_key and description.min_key in info:
            self._attr_native_min_value = info[description.min_key]
        if description.max_key and description.max_key in info:
            self._attr_native_max_value = info[description.max_key]

    @property
    def native_value(self) -> float | None:
        return self.coordinator.data.get(self.entity_description.key)

    async def async_set_native_value(self, value: float) -> None:
        await self.coordinator.async_control(**{self.entity_description.key: int(value)})
