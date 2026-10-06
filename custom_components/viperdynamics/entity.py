"""Base entity for Viper Dynamics devices."""

from __future__ import annotations

from homeassistant.helpers.device_registry import CONNECTION_NETWORK_MAC, DeviceInfo
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import DOMAIN, MANUFACTURER, MODEL_NAMES
from .coordinator import ViperCoordinator


class ViperEntity(CoordinatorEntity[ViperCoordinator]):
    """Entity bound to one device, keyed by its MAC-based id."""

    _attr_has_entity_name = True

    def __init__(self, coordinator: ViperCoordinator, key: str) -> None:
        super().__init__(coordinator)
        info = coordinator.info
        device_id = info["id"]
        mac = ":".join(device_id[i : i + 2] for i in range(0, 12, 2))
        self._attr_unique_id = f"{device_id}_{key}"
        self._attr_translation_key = key
        self._attr_device_info = DeviceInfo(
            identifiers={(DOMAIN, device_id)},
            connections={(CONNECTION_NETWORK_MAC, mac)},
            manufacturer=MANUFACTURER,
            model=info.get("model_name") or MODEL_NAMES.get(info.get("model", ""), "Unknown"),
            name=info.get("name"),
            sw_version=info.get("fw"),
            configuration_url=coordinator.client.base_url,
        )
