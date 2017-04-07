"""Init file for HassIO homeassistant rest api."""
import asyncio
import logging

import voluptuous as vol

from .util import api_process, api_validate
from ..const import ATTR_VERSION, ATTR_CURRENT

_LOGGER = logging.getLogger(__name__)

SCHEMA_VERSION = vol.Schema({
    vol.Optional(ATTR_VERSION): vol.Coerce(str),
})


class APIHomeAssistant(object):
    """Handle rest api for homeassistant functions."""

    def __init__(self, config, loop, dock_hass):
        """Initialize homeassistant rest api part."""
        self.config = config
        self.loop = loop
        self.dock_hass = dock_hass

    @api_process
    async def info(self, request):
        """Return host information."""
        info = {
            ATTR_VERSION: self.dock_hass.version,
            ATTR_CURRENT: self.config.current_homeassistant,
        }

        return info

    @api_process
    async def update(self, request):
        """Update host OS."""
        body = await api_validate(SCHEMA_VERSION, request)
        version = body.get(ATTR_VERSION, self.config.current_homeassistant)

        if self.dock_hass.in_progress:
            raise RuntimeError("Other task is in progress.")

        if version == self.dock_hass.version:
            raise RuntimeError("%s is already in use.", version)

        return await asyncio.shield(self.dock_hass.update(version))
