"""Setup and entity tests."""

from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viperdynamics.const import DOMAIN


async def _setup(hass: HomeAssistant) -> MockConfigEntry:
    entry = MockConfigEntry(
        domain=DOMAIN, unique_id="a1b2c3d4e5f6", data={CONF_HOST: "192.168.1.50"}
    )
    entry.add_to_hass(hass)
    assert await hass.config_entries.async_setup(entry.entry_id)
    await hass.async_block_till_done()
    return entry


async def test_entities_from_capabilities(hass: HomeAssistant, mock_client) -> None:
    await _setup(hass)

    assert hass.states.get("select.p4x_1a2_mode").state == "Continuous Stargate"
    assert hass.states.get("number.p4x_1a2_brightness").state == "80"
    assert hass.states.get("number.p4x_1a2_brightness").attributes["min"] == 22
    assert hass.states.get("switch.p4x_1a2_automatic_brightness").state == "off"
    assert hass.states.get("cover.p4x_1a2_gate").state == "closed"
    assert hass.states.get("update.p4x_1a2_firmware").state == "on"
    assert hass.states.get("image.p4x_1a2_product_photo") is not None
    # Not in capabilities:
    assert hass.states.get("number.p4x_1a2_volume") is None
    assert hass.states.get("sensor.p4x_1a2_player") is None


async def test_control(hass: HomeAssistant, mock_client) -> None:
    await _setup(hass)

    await hass.services.async_call(
        "select", "select_option",
        {"entity_id": "select.p4x_1a2_mode", "option": "Photo Frame"}, blocking=True,
    )
    mock_client.control.assert_awaited_with(mode=2)
    assert hass.states.get("select.p4x_1a2_mode").state == "Photo Frame"

    await hass.services.async_call(
        "number", "set_value",
        {"entity_id": "number.p4x_1a2_brightness", "value": 55}, blocking=True,
    )
    mock_client.control.assert_awaited_with(brightness=55)

    await hass.services.async_call(
        "cover", "open_cover", {"entity_id": "cover.p4x_1a2_gate"}, blocking=True
    )
    mock_client.control.assert_awaited_with(gate="open")

    await hass.services.async_call(
        "button", "press", {"entity_id": "button.p4x_1a2_test_alarm"}, blocking=True
    )
    mock_client.control.assert_awaited_with(action="alarm_test")


async def test_unload(hass: HomeAssistant, mock_client) -> None:
    entry = await _setup(hass)
    assert await hass.config_entries.async_unload(entry.entry_id)
