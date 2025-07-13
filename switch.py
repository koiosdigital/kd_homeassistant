"""Switch platform for Koios Digital Clock integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.switch import SwitchEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_NIXIE_CONFIG,
    DOMAIN,
    MODEL_NIXIE,
)
from .coordinator import KoiosClockDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Koios Clock switches based on a config entry."""
    coordinator: KoiosClockDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # Nixie-specific switches
    if coordinator.model == MODEL_NIXIE:
        entities.extend([
            KoiosClockMilitaryTimeSwitch(coordinator),
            KoiosClockBlinkingDotsSwitch(coordinator),
        ])

    if entities:
        async_add_entities(entities, True)


class KoiosClockSwitchEntity(CoordinatorEntity, SwitchEntity):
    """Base class for Koios Clock switch entities."""

    def __init__(
        self,
        coordinator: KoiosClockDataUpdateCoordinator,
        switch_type: str,
        name: str,
    ) -> None:
        """Initialize the switch."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.switch_type = switch_type
        self._attr_unique_id = f"{coordinator.host}_{coordinator.port}_{switch_type}"
        self._attr_name = f"Koios Clock {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.host}_{coordinator.port}")},
            "name": f"Koios Clock ({coordinator.host})",
            "manufacturer": "Koios Digital",
            "model": coordinator.model.title(),
            "sw_version": coordinator.data.get("about", {}).get("version"),
        }


class KoiosClockMilitaryTimeSwitch(KoiosClockSwitchEntity):
    """Switch to control military time format."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the military time switch."""
        super().__init__(coordinator, "military_time", "Military Time")
        self._attr_icon = "mdi:clock-time-eight"

    @property
    def is_on(self) -> bool:
        """Return true if military time is enabled."""
        nixie_data = self.coordinator.data.get("nixie", {})
        return nixie_data.get("military_time", False)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on military time."""
        data = {"military_time": True}
        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off military time."""
        data = {"military_time": False}
        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockBlinkingDotsSwitch(KoiosClockSwitchEntity):
    """Switch to control blinking dots."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the blinking dots switch."""
        super().__init__(coordinator, "blinking_dots", "Blinking Dots")
        self._attr_icon = "mdi:dots-horizontal"

    @property
    def is_on(self) -> bool:
        """Return true if blinking dots are enabled."""
        nixie_data = self.coordinator.data.get("nixie", {})
        return nixie_data.get("blinking_dots", True)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on blinking dots."""
        data = {"blinking_dots": True}
        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off blinking dots."""
        data = {"blinking_dots": False}
        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()
