"""Image entity showing the product photo on the device page."""

from __future__ import annotations

from homeassistant.components.image import ImageEntity
from homeassistant.const import EntityCategory
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback
from homeassistant.util import dt as dt_util

from . import IMAGES_DIR
from .coordinator import ViperConfigEntry, ViperCoordinator
from .entity import ViperEntity

PARALLEL_UPDATES = 0


async def async_setup_entry(
    hass: HomeAssistant,
    entry: ViperConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    coordinator = entry.runtime_data
    path = IMAGES_DIR / f"{coordinator.info.get('model', '')}.png"
    photo = await hass.async_add_executor_job(lambda: path.read_bytes() if path.is_file() else None)
    if photo:
        async_add_entities([ViperProductImage(hass, coordinator, photo)])


class ViperProductImage(ViperEntity, ImageEntity):
    _attr_content_type = "image/png"
    _attr_entity_category = EntityCategory.DIAGNOSTIC

    def __init__(self, hass: HomeAssistant, coordinator: ViperCoordinator, photo: bytes) -> None:
        ViperEntity.__init__(self, coordinator, "product_photo")
        ImageEntity.__init__(self, hass)
        self._photo = photo
        self._attr_image_last_updated = dt_util.utcnow()

    @property
    def available(self) -> bool:
        return True

    async def async_image(self) -> bytes | None:
        return self._photo
