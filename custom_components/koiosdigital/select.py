"""Select platform for Koios Digital Clock integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.select import SelectEntity
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_LEDS,
    API_FIBONACCI,
    DOMAIN,
    LED_EFFECTS,
    MODEL_FIBONACCI,
    MODEL_NIXIE,
    MODEL_WORDCLOCK,
)
from .coordinator import KoiosClockDataUpdateCoordinator

_LOGGER = logging.getLogger(__name__)


async def async_setup_entry(
    hass: HomeAssistant,
    config_entry: ConfigEntry,
    async_add_entities: AddEntitiesCallback,
) -> None:
    """Set up Koios Clock selects based on a config entry."""
    coordinator: KoiosClockDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # LED effects available for Nixie and Wordclock models
    if coordinator.model in [MODEL_NIXIE, MODEL_WORDCLOCK]:
        entities.append(KoiosClockLEDEffectSelect(coordinator))

    # Fibonacci-specific selects
    if coordinator.model == MODEL_FIBONACCI:
        entities.append(KoiosClockFibonacciThemeSelect(coordinator))

    if entities:
        async_add_entities(entities, True)


class KoiosClockSelectEntity(CoordinatorEntity, SelectEntity):
    """Base class for Koios Clock select entities."""

    def __init__(
        self,
        coordinator: KoiosClockDataUpdateCoordinator,
        select_type: str,
        name: str,
    ) -> None:
        """Initialize the select."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.select_type = select_type
        self._attr_unique_id = f"{coordinator.host}_{coordinator.port}_{select_type}"
        self._attr_name = f"Koios Clock {name}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.host}_{coordinator.port}")},
            "name": f"Koios Clock ({coordinator.host})",
            "manufacturer": "Koios Digital",
            "model": coordinator.model.title(),
            "sw_version": coordinator.data.get("about", {}).get("version"),
        }


class KoiosClockLEDEffectSelect(KoiosClockSelectEntity):
    """Select entity for LED effects."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the LED effect select."""
        super().__init__(coordinator, "led_effect", "LED Effect")
        self._attr_icon = "mdi:lightbulb"
        self._attr_options = list(LED_EFFECTS.values())

    @property
    def current_option(self) -> str | None:
        """Return the current LED effect."""
        led_data = self.coordinator.data.get("leds", {})
        mode = led_data.get("mode", "solid")
        return LED_EFFECTS.get(mode, mode)

    async def async_select_option(self, option: str) -> None:
        """Change the LED effect."""
        # Find the mode key for the effect name
        mode = next((k for k, v in LED_EFFECTS.items() if v == option), "solid")
        data = {"mode": mode}
        success = await self.coordinator.async_post_data(API_LEDS, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockFibonacciThemeSelect(KoiosClockSelectEntity):
    """Select entity for Fibonacci themes."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the Fibonacci theme select."""
        super().__init__(coordinator, "fibonacci_theme", "Fibonacci Theme")
        self._attr_icon = "mdi:palette"

    @property
    def options(self) -> list[str]:
        """Return the list of available themes."""
        fib_data = self.coordinator.data.get("fibonacci", {})
        themes_data = fib_data.get("themes", [])
        return [theme.get("name", f"Theme {theme.get('id', '')}") for theme in themes_data]

    @property
    def current_option(self) -> str | None:
        """Return the current theme."""
        fib_data = self.coordinator.data.get("fibonacci", {})
        theme_id = fib_data.get("theme_id", 0)
        themes_data = fib_data.get("themes", [])
        theme = next((t for t in themes_data if t.get("id") == theme_id), None)
        return theme.get("name", "RGB") if theme else "RGB"

    async def async_select_option(self, option: str) -> None:
        """Change the Fibonacci theme."""
        # Find the theme ID for the option name
        fib_data = self.coordinator.data.get("fibonacci", {})
        themes_data = fib_data.get("themes", [])
        theme_id = next(
            (theme["id"] for theme in themes_data if theme.get("name") == option),
            0
        )
        data = {"theme_id": theme_id}
        success = await self.coordinator.async_post_data(API_FIBONACCI, data)
        if success:
            await self.coordinator.async_request_refresh()
