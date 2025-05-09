"""AVM FRITZ!Box SMS platform for notify component."""

from __future__ import annotations

import logging

from homeassistant.components.notify import NotifyEntity
from homeassistant.config_entries import ConfigSubentry
from homeassistant.const import CONF_HOST, CONF_PASSWORD, CONF_TARGET, CONF_USERNAME
from homeassistant.core import HomeAssistant
from homeassistant.helpers import device_registry as dr
from homeassistant.helpers.entity_platform import AddConfigEntryEntitiesCallback

from . import FritzBoxConfigEntry
from .const import DOMAIN

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: FritzBoxConfigEntry,
    async_add_entities: AddConfigEntryEntitiesCallback,
) -> None:
    """Set up the SMS notification targets from a config entry."""
    device_registry = dr.async_get(hass)
    device_registry.async_get_or_create(
        config_entry_id=config_entry.entry_id,
        identifiers={(DOMAIN, config_entry.entry_id)},
        name=config_entry.title,
        configuration_url=f"http://{config_entry.data[CONF_HOST]}/",
    )
    for subentry_id, subentry in config_entry.subentries.items():
        async_add_entities(
            [
                FritzBoxNotifyEntity(
                    config_entry,
                    subentry,
                )
            ],
            config_subentry_id=subentry_id,
        )


class FritzBoxNotifyEntity(NotifyEntity):
    """Implement the notification service for the AVM FRITZ!Box SMS service."""

    _attr_has_entity_name = True
    _attr_icon = "mdi:message-text"

    def __init__(self, entry: FritzBoxConfigEntry, subentry: ConfigSubentry) -> None:
        """Initialize the service."""
        self.entry = entry
        self.subentry = subentry
        self._attr_name = subentry.title
        self._attr_unique_id = subentry.subentry_id
        self._attr_device_info = dr.DeviceInfo(
            identifiers={(DOMAIN, subentry.subentry_id)},
            name=subentry.title,
            via_device=(DOMAIN, entry.entry_id),
        )

    async def async_send_message(self, message: str, title: str | None = None) -> None:
        """Send SMS to specified target user cell."""
        box = self.entry.runtime_data
        cfg = self.entry.data
        sub = self.subentry.data

        await box.login(cfg[CONF_USERNAME], cfg[CONF_PASSWORD])

        uid = await box.send_sms(sub[CONF_TARGET], message)
        if uid:
            await box.delete_sms(uid)

        await box.logout()
