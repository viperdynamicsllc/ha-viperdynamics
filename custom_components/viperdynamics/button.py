"""Button entities: alarm test, alarm acknowledge, restart."""

from __future__ import annotations

from homeassistant.components.button import ButtonDeviceClass, ButtonEntity, ButtonEntityDescription
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 1

BUTTONS = (
    ButtonEntityDescription(key="alarm_test", icon="mdi:alarm-check"),
    ButtonEntityDescription(key="alarm_ack", icon="mdi:alarm-off"),
    ButtonEntityDescription(
        key="restart",
        device_class=ButtonDeviceClass.RESTART,
        entity_category=EntityCategory.CONFIG,
    ),
)


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    async_add_entities(
        ViperButton(coordinator, desc)
        for desc in BUTTONS
        if desc.key in coordinator.capabilities
    )


class ViperButton(ViperEntity, ButtonEntity):
    def __init__(self, coordinator: ViperCoordinator, description: ButtonEntityDescription) -> None:
        super().__init__(coordinator, description.key)
        self.entity_description = description

    async def async_press(self) -> None:
        await self.coordinator.async_control(action=self.entity_description.key)
