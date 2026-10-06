"""Fixtures for Viper Dynamics tests."""

from __future__ import annotations

from copy import deepcopy
from unittest.mock import AsyncMock, patch

import pytest

INFO = {
    "manufacturer": "Viper Dynamics",
    "model": "stargate_p4x",
    "model_name": "Stargate P4X",
    "id": "a1b2c3d4e5f6",
    "name": "P4X-1A2",
    "fw": "2.0.58",
    "api": 1,
    "capabilities": ["mode", "brightness", "backlight_auto", "alarm_volume", "rotation",
                     "alarm_test", "restart", "ota", "gate"],
    "modes": ["Clock", "Continuous Stargate", "Photo Frame"],
    "brightness_min": 22,
    "rotation_min": -10,
    "rotation_max": 10,
}

STATE = {
    "mode": 1,
    "brightness": 80,
    "backlight_auto": False,
    "alarm_volume": 50,
    "rotation": 0,
    "gate": {"open": False, "busy": False},
    "update": {"installed": "2.0.58", "latest": "2.0.59", "notes": "Fixes", "in_progress": False, "percent": 0},
}


@pytest.fixture(autouse=True)
def auto_enable_custom_integrations(enable_custom_integrations):
    yield


@pytest.fixture
def mock_client():
    """Patch ViperClient everywhere it is constructed."""
    client = AsyncMock()
    client.host = "192.168.1.50"
    client.base_url = "http://192.168.1.50"
    client.get_info.return_value = deepcopy(INFO)
    client.get_state.return_value = deepcopy(STATE)

    async def control(**values):
        state = deepcopy(STATE)
        state.update(values)
        return state

    client.control.side_effect = control
    with (
        patch("custom_components.viperdynamics.ViperClient", return_value=client),
        patch("custom_components.viperdynamics.config_flow.ViperClient", return_value=client),
    ):
        yield client
