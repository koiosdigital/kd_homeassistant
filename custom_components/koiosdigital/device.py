"""Device registry helper for Koios Clock integration."""
from __future__ import annotations

from homeassistant.helpers.device_registry import DeviceInfo

from .const import DOMAIN


def get_device_info(
    coordinator,
    host: str,
    port: int,
    model: str,
) -> DeviceInfo:
    """Get device info for Koios Clock device."""
    about_data = coordinator.data.get("about", {})
    
    return DeviceInfo(
        identifiers={(DOMAIN, f"{host}_{port}")},
        name=f"Koios Clock ({host})",
        manufacturer="Koios Digital",
        model=model.title(),
        sw_version=about_data.get("version"),
        configuration_url=f"http://{host}:{port}",
    )
