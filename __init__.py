"""The AVM FRITZ!Box SMS integration."""

from __future__ import annotations

from fritzsms.fritzbox import FritzBox
from homeassistant.config_entries import ConfigEntry
from homeassistant.const import CONF_HOST, CONF_TOKEN, Platform
from homeassistant.core import HomeAssistant
from homeassistant.helpers.aiohttp_client import async_get_clientsession

_PLATFORMS: list[Platform] = [Platform.NOTIFY]

type FritzBoxConfigEntry = ConfigEntry[FritzBox]


async def async_setup_entry(hass: HomeAssistant, entry: FritzBoxConfigEntry) -> bool:
    """Set up AVM FRITZ!Box SMS from a config entry."""

    host = entry.data[CONF_HOST]
    session = async_get_clientsession(hass)
    box = FritzBox(host, session)
    box.set_otp(entry.data[CONF_TOKEN])
    entry.runtime_data = box
    entry.async_on_unload(entry.add_update_listener(async_update_options))

    await hass.config_entries.async_forward_entry_setups(entry, _PLATFORMS)

    return True


async def async_update_options(hass: HomeAssistant, entry: FritzBoxConfigEntry) -> None:
    """Update options."""
    await hass.config_entries.async_reload(entry.entry_id)


async def async_unload_entry(hass: HomeAssistant, entry: FritzBoxConfigEntry) -> bool:
    """Unload a config entry."""
    return await hass.config_entries.async_unload_platforms(entry, _PLATFORMS)
