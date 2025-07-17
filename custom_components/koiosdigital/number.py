"""Number platform for Koios Digital Clock integration."""
from __future__ import annotations

import logging
from typing import Any

from homeassistant.components.number import NumberEntity, NumberMode
from homeassistant.config_entries import ConfigEntry
from homeassistant.core import HomeAssistant
from homeassistant.helpers.entity_platform import AddEntitiesCallback
from homeassistant.helpers.update_coordinator import CoordinatorEntity

from .const import (
    API_LEDS,
    API_NIXIE,
    API_FIBONACCI,
    DOMAIN,
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
    """Set up Koios Clock number entities based on a config entry."""
    coordinator: KoiosClockDataUpdateCoordinator = hass.data[DOMAIN][config_entry.entry_id]

    entities = []

    # LED brightness for Nixie and Wordclock models
    if coordinator.model in [MODEL_NIXIE, MODEL_WORDCLOCK]:
        entities.append(KoiosClockLEDBrightnessNumber(coordinator))

    # Model-specific number entities
    if coordinator.model == MODEL_NIXIE:
        entities.append(KoiosClockNixieBrightnessNumber(coordinator))
    elif coordinator.model == MODEL_FIBONACCI:
        entities.append(KoiosClockFibonacciBrightnessNumber(coordinator))

    if entities:
        async_add_entities(entities, True)


class KoiosClockNumberEntity(CoordinatorEntity, NumberEntity):
    """Base class for Koios Clock number entities."""

    def __init__(
        self,
        coordinator: KoiosClockDataUpdateCoordinator,
        number_type: str,
        name: str,
    ) -> None:
        """Initialize the number entity."""
        super().__init__(coordinator)
        self.coordinator = coordinator
        self.number_type = number_type
        self._attr_unique_id = f"{coordinator.host}_{coordinator.port}_{number_type}"
        self._attr_name = f"Koios Clock {name}"
        self._attr_mode = NumberMode.SLIDER
        self._attr_device_info = {
            "identifiers": {(DOMAIN, f"{coordinator.host}_{coordinator.port}")},
            "name": f"Koios Clock ({coordinator.host})",
            "manufacturer": "Koios Digital",
            "model": coordinator.model.title(),
            "sw_version": coordinator.data.get("about", {}).get("version"),
        }


class KoiosClockLEDBrightnessNumber(KoiosClockNumberEntity):
    """Number entity for LED brightness."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the LED brightness number."""
        super().__init__(coordinator, "led_brightness", "LED Brightness")
        self._attr_icon = "mdi:brightness-6"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 255
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self) -> float | None:
        """Return the current LED brightness."""
        led_data = self.coordinator.data.get("leds", {})
        return led_data.get("brightness", 255)

    async def async_set_native_value(self, value: float) -> None:
        """Set the LED brightness."""
        data = {"brightness": int(value)}
        success = await self.coordinator.async_post_data(API_LEDS, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockNixieBrightnessNumber(KoiosClockNumberEntity):
    """Number entity for Nixie tube brightness."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the Nixie brightness number."""
        super().__init__(coordinator, "nixie_brightness", "Nixie Brightness")
        self._attr_icon = "mdi:brightness-4"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 100
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = "%"

    @property
    def native_value(self) -> float | None:
        """Return the current Nixie brightness."""
        nixie_data = self.coordinator.data.get("nixie", {})
        return nixie_data.get("brightness", 80)

    async def async_set_native_value(self, value: float) -> None:
        """Set the Nixie brightness."""
        data = {"brightness": int(value)}
        success = await self.coordinator.async_post_data(API_NIXIE, data)
        if success:
            await self.coordinator.async_request_refresh()


class KoiosClockFibonacciBrightnessNumber(KoiosClockNumberEntity):
    """Number entity for Fibonacci display brightness."""

    def __init__(self, coordinator: KoiosClockDataUpdateCoordinator) -> None:
        """Initialize the Fibonacci brightness number."""
        super().__init__(coordinator, "fibonacci_brightness", "Fibonacci Brightness")
        self._attr_icon = "mdi:brightness-5"
        self._attr_native_min_value = 0
        self._attr_native_max_value = 255
        self._attr_native_step = 1
        self._attr_native_unit_of_measurement = None

    @property
    def native_value(self) -> float | None:
        """Return the current Fibonacci brightness."""
        fib_data = self.coordinator.data.get("fibonacci", {})
        return fib_data.get("brightness", 255)

    async def async_set_native_value(self, value: float) -> None:
        """Set the Fibonacci brightness."""
        data = {"brightness": int(value)}
        success = await self.coordinator.async_post_data(API_FIBONACCI, data)
        if success:
            await self.coordinator.async_request_refresh()
