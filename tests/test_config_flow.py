"""Config flow tests."""

from ipaddress import ip_address

from homeassistant import config_entries
from homeassistant.const import CONF_HOST
from homeassistant.core import HomeAssistant
from homeassistant.data_entry_flow import FlowResultType
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo
from pytest_homeassistant_custom_component.common import MockConfigEntry

from custom_components.viperdynamics.api import ViperError
from custom_components.viperdynamics.const import DOMAIN

DISCOVERY = ZeroconfServiceInfo(
    ip_address=ip_address("192.168.1.50"),
    ip_addresses=[ip_address("192.168.1.50")],
    hostname="P4X-1A2.local.",
    name="P4X-1A2._viperdyn._tcp.local.",
    port=80,
    type="_viperdyn._tcp.local.",
    properties={"id": "a1b2c3d4e5f6", "model": "stargate_p4x", "fw": "2.0.58", "api": "1"},
)


async def test_zeroconf_discovery(hass: HomeAssistant, mock_client) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=DISCOVERY
    )
    assert result["type"] is FlowResultType.FORM
    assert result["step_id"] == "zeroconf_confirm"
    assert result["description_placeholders"]["name"] == "Stargate P4X (P4X-1A2)"
    assert "/viperdynamics_static/stargate_p4x.png" in result["description_placeholders"]["image"]

    result = await hass.config_entries.flow.async_configure(result["flow_id"], {})
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["title"] == "Stargate P4X (P4X-1A2)"
    assert result["data"][CONF_HOST] == "192.168.1.50"
    assert result["result"].unique_id == "a1b2c3d4e5f6"


async def test_zeroconf_updates_host_of_existing(hass: HomeAssistant, mock_client) -> None:
    entry = MockConfigEntry(domain=DOMAIN, unique_id="a1b2c3d4e5f6", data={CONF_HOST: "10.0.0.9"})
    entry.add_to_hass(hass)
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=DISCOVERY
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "already_configured"
    assert entry.data[CONF_HOST] == "192.168.1.50"


async def test_zeroconf_without_id_aborts(hass: HomeAssistant, mock_client) -> None:
    info = ZeroconfServiceInfo(
        ip_address=DISCOVERY.ip_address,
        ip_addresses=DISCOVERY.ip_addresses,
        hostname=DISCOVERY.hostname,
        name=DISCOVERY.name,
        port=80,
        type=DISCOVERY.type,
        properties={},
    )
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_ZEROCONF}, data=info
    )
    assert result["type"] is FlowResultType.ABORT
    assert result["reason"] == "not_viper_device"


async def test_user_flow(hass: HomeAssistant, mock_client) -> None:
    result = await hass.config_entries.flow.async_init(
        DOMAIN, context={"source": config_entries.SOURCE_USER}
    )
    assert result["type"] is FlowResultType.FORM

    mock_client.get_info.side_effect = ViperError("down")
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.50"}
    )
    assert result["errors"] == {"base": "cannot_connect"}

    mock_client.get_info.side_effect = None
    result = await hass.config_entries.flow.async_configure(
        result["flow_id"], {CONF_HOST: "192.168.1.50"}
    )
    assert result["type"] is FlowResultType.CREATE_ENTRY
    assert result["result"].unique_id == "a1b2c3d4e5f6"
