"""Config flow: zeroconf discovery plus manual host entry."""

from __future__ import annotations

from typing import Any

import voluptuous as vol

from homeassistant.config_entries import ConfigFlow, ConfigFlowResult
from homeassistant.const import CONF_HOST
from homeassistant.helpers.aiohttp_client import async_get_clientsession
from homeassistant.helpers.service_info.zeroconf import ZeroconfServiceInfo

from . import IMAGES_DIR, async_register_static
from .api import ViperClient, ViperError
from .const import CONF_DEVICE_ID, CONF_MODEL, DOMAIN, MODEL_NAMES, STATIC_URL


def _title(info: dict[str, Any]) -> str:
    model = info.get("model_name") or MODEL_NAMES.get(info.get("model", ""), "Viper device")
    return f"{model} ({info['name']})" if info.get("name") else model


class ViperConfigFlow(ConfigFlow, domain=DOMAIN):
    """Handle a config flow for Viper Dynamics."""

    VERSION = 1

    def __init__(self) -> None:
        self._host: str | None = None
        self._info: dict[str, Any] = {}

    async def _fetch_info(self, host: str) -> dict[str, Any]:
        return await ViperClient(async_get_clientsession(self.hass), host).get_info()

    def _create_entry(self) -> ConfigFlowResult:
        assert self._host is not None
        return self.async_create_entry(
            title=_title(self._info),
            data={
                CONF_HOST: self._host,
                CONF_DEVICE_ID: self._info["id"],
                CONF_MODEL: self._info.get("model"),
            },
        )

    async def async_step_user(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        errors: dict[str, str] = {}
        if user_input is not None:
            host = user_input[CONF_HOST].strip()
            try:
                info = await self._fetch_info(host)
            except ViperError:
                errors["base"] = "cannot_connect"
            else:
                await self.async_set_unique_id(info["id"])
                self._abort_if_unique_id_configured(updates={CONF_HOST: host})
                self._host, self._info = host, info
                return self._create_entry()
        return self.async_show_form(
            step_id="user",
            data_schema=vol.Schema({vol.Required(CONF_HOST): str}),
            errors=errors,
        )

    async def async_step_zeroconf(
        self, discovery_info: ZeroconfServiceInfo
    ) -> ConfigFlowResult:
        device_id = discovery_info.properties.get("id")
        if not device_id:
            return self.async_abort(reason="not_viper_device")
        host = discovery_info.host

        await self.async_set_unique_id(device_id)
        self._abort_if_unique_id_configured(updates={CONF_HOST: host})

        try:
            info = await self._fetch_info(host)
        except ViperError:
            return self.async_abort(reason="cannot_connect")

        self._host, self._info = host, info
        self.context["title_placeholders"] = {"name": _title(info)}
        return await self.async_step_zeroconf_confirm()

    async def async_step_zeroconf_confirm(
        self, user_input: dict[str, Any] | None = None
    ) -> ConfigFlowResult:
        if user_input is not None:
            return self._create_entry()

        model = self._info.get("model", "")
        image = ""
        has_photo = await self.hass.async_add_executor_job(
            (IMAGES_DIR / f"{model}.png").is_file
        )
        if has_photo:
            await async_register_static(self.hass)
            image = f"![{model}]({STATIC_URL}/{model}.png)"

        self._set_confirm_only()
        return self.async_show_form(
            step_id="zeroconf_confirm",
            description_placeholders={"name": _title(self._info), "image": image},
        )
