"""Light platform for Koios Digital Clock integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.light import (
    ATTR_BRIGHTNESS,
    ATTR_EFFECT,
    ATTR_RGB_COLOR,
    ATTR_RGBW_COLOR,
    ColorMode,
    LightEntity,
    LightEntityFeature,
)
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_LED_CONFIG,
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
    """Set up Koios Clock lights based on a config entry."""
    coordinator: KoiosClockDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # All models have backlight LEDs
    entities.append(KoiosClockBacklight(coordinator))

    # Model-specific lights
    if coordinator.model == MODEL_NIXIE:
        entities.append(KoiosClockNixieTubes(coordinator))
    elif coordinator.model == MODEL_FIBONACCI:
        entities.append(KoiosClockFibonacciTheme(coordinator))

    async_add_entities(entities, True)


class KoiosClockLightEntity(CoordinatorEntity, LightEntity):
    """Base class for Koios Clock light entities."""

    def __init__(
        self,
        coordinator: KoiosClockDataUpdateCoordinator,
        light_type: str,
    ) -> None:
        """Initialize the light."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.light_type = light_type
        self._attr_unique_id = f"{coordinator.host}_{coordinator.port}_{light_type}"
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.host}_{coordinator.port}")},
            "name": f"Koios Clock ({coordinator.host})",
            "manufacturer": "Koios Digital",
            "model": coordinator.model.title(),
            "sw_version": coordinator.data.get("about", {}).get("version"),
        }


class KoiosClockBacklight(KoiosClockLightEntity):
    """Representation of the Koios Clock backlight LEDs."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the backlight."""
        super().__init__(coordinator, "backlight")
        self._attr_name = f"Koios Clock Backlight"
        self._attr_supported_color_modes = {ColorMode.RGBW}
        self._attr_color_mode = ColorMode.RGBW
        self._attr_supported_features = LightEntityFeature.EFFECT

    @property
    def is_on(self) -> bool:
        """Return true if light is on."""
        led_data = self.coordinator.data.get("led", {})
        return led_data.get("mode", "off") != "off"

    @property
    def brightness(self) -> int | None:
        """Return the brightness of this light between 0..255."""
        led_data = self.coordinator.data.get("led", {})
        brightness = led_data.get("brightness", 255)
        return brightness

    @property
    def rgbw_color(self) -> tuple[int, int, int, int] | None:
        """Return the rgbw color value."""
        led_data = self.coordinator.data.get("led", {})
        color = led_data.get("color", {})
        return (
            color.get("r", 255),
            color.get("g", 255),
            color.get("b", 255),
            color.get("w", 0),
        )

    @property
    def effect(self) -> str | None:
        """Return the current effect."""
        led_data = self.coordinator.data.get("led", {})
        mode = led_data.get("mode", "off")
        return LED_EFFECTS.get(mode, mode)

    @property
    def effect_list(self) -> list[str]:
        """Return the list of supported effects."""
        return list(LED_EFFECTS.values())

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Instruct the light to turn on."""
        data = {}

        if ATTR_BRIGHTNESS in kwargs:
            data["brightness"] = kwargs[ATTR_BRIGHTNESS]

        if ATTR_RGBW_COLOR in kwargs:
            r, g, b, w = kwargs[ATTR_RGBW_COLOR]
            data["color"] = {"r": r, "g": g, "b": b, "w": w}
        elif ATTR_RGB_COLOR in kwargs:
            r, g, b = kwargs[ATTR_RGB_COLOR]
            data["color"] = {"r": r, "g": g, "b": b, "w": 0}

        if ATTR_EFFECT in kwargs:
            # Find the mode key for the effect name
            effect_name = kwargs[ATTR_EFFECT]
            mode = next((k for k, v in LED_EFFECTS.items() if v == effect_name), "solid")
            data["mode"] = mode

        # If no mode specified and turning on, use solid
        if "mode" not in data and not self.is_on:
            data["mode"] = "solid"

        success = await self.coordinator.async_post_data(API_LED_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Instruct the light to turn off."""
        data = {"mode": "off"}
        success = await self.coordinator.async_post_data(API_LED_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockNixieTubes(KoiosClockLightEntity):
    """Representation of the Nixie tubes as a light for brightness control."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the nixie tubes."""
        super().__init__(coordinator, "nixie_tubes")
        self._attr_name = f"Koios Clock Nixie Tubes"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS

    @property
    def is_on(self) -> bool:
        """Return true if nixie tubes are enabled."""
        nixie_data = self.coordinator.data.get("nixie", {})
        return nixie_data.get("enabled", True)

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the nixie tubes (0-255 scale)."""
        nixie_data = self.coordinator.data.get("nixie", {})
        brightness_percent = nixie_data.get("brightness", 80)
        # Convert from 0-100% to 0-255 scale
        return int(brightness_percent * 255 / 100)

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Turn on the nixie tubes."""
        from .const import API_NIXIE_CONFIG

        data = {"enabled": True}

        if ATTR_BRIGHTNESS in kwargs:
            # Convert from 0-255 to 0-100% scale
            brightness_percent = int(kwargs[ATTR_BRIGHTNESS] * 100 / 255)
            data["brightness"] = brightness_percent

        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Turn off the nixie tubes."""
        from .const import API_NIXIE_CONFIG

        data = {"enabled": False}
        success = await self.coordinator.async_post_data(API_NIXIE_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockFibonacciTheme(KoiosClockLightEntity):
    """Representation of the Fibonacci theme as a light entity."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the fibonacci theme light."""
        super().__init__(coordinator, "fibonacci_theme")
        self._attr_name = f"Koios Clock Theme"
        self._attr_supported_color_modes = {ColorMode.BRIGHTNESS}
        self._attr_color_mode = ColorMode.BRIGHTNESS
        self._attr_supported_features = LightEntityFeature.EFFECT

    @property
    def is_on(self) -> bool:
        """Return true if the fibonacci display is active."""
        # Fibonacci is always "on" - brightness controls intensity
        return True

    @property
    def brightness(self) -> int | None:
        """Return the brightness of the fibonacci display."""
        fib_data = self.coordinator.data.get("fibonacci", {})
        return fib_data.get("brightness", 255)

    @property
    def effect(self) -> str | None:
        """Return the current theme as an effect."""
        fib_data = self.coordinator.data.get("fibonacci", {})
        return fib_data.get("theme_name", "RGB")

    @property
    def effect_list(self) -> list[str]:
        """Return the list of available themes."""
        themes_data = self.coordinator.data.get("fibonacci_themes", [])
        return [theme.get("name", f"Theme {theme.get('id', '')}") for theme in themes_data]

    async def async_turn_on(self, **kwargs: Any) -> None:
        """Adjust fibonacci settings."""
        from .const import API_FIBONACCI_CONFIG

        data = {}

        if ATTR_BRIGHTNESS in kwargs:
            data["brightness"] = kwargs[ATTR_BRIGHTNESS]

        if ATTR_EFFECT in kwargs:
            # Find the theme ID for the effect name
            effect_name = kwargs[ATTR_EFFECT]
            themes_data = self.coordinator.data.get("fibonacci_themes", [])
            theme_id = next(
                (theme["id"] for theme in themes_data if theme.get("name") == effect_name),
                0
            )
            data["theme_id"] = theme_id

        if data:
            success = await self.coordinator.async_post_data(API_FIBONACCI_CONFIG, data)
            if success:
                await self.coordinator.async_request_refresh()

    async def async_turn_off(self, **kwargs: Any) -> None:
        """Fibonacci display cannot be turned off, set to minimum brightness."""
        from .const import API_FIBONACCI_CONFIG

        data = {"brightness": 1}
        success = await self.coordinator.async_post_data(API_FIBONACCI_CONFIG, data)
        if success:
            await self.coordinator.async_request_refresh()
