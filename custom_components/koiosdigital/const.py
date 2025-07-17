"""Constants for the Koios Digital Clock integration."""

DOMAIN = "koiosdigital"

# Device models
MODEL_FIBONACCI = "fibonacci"
MODEL_NIXIE = "nixie"
MODEL_WORDCLOCK = "wordclock"

# API endpoints
API_ABOUT = "/api/about"
API_SYSTEM_CONFIG = "/api/system/config"
API_TIME_ZONEDB = "/api/time/zonedb"
API_LEDS = "/api/leds"
API_LEDS_WS = "/api/leds/ws"
API_NIXIE = "/api/nixie"
API_NIXIE_WS = "/api/nixie/ws"
API_FIBONACCI = "/api/fibonacci"
API_FIBONACCI_WS = "/api/fibonacci/ws"

# LED effects (updated to match swagger)
LED_EFFECTS = {
    "solid": "Solid",
    "blink": "Blink", 
    "breathe": "Breathe",
    "cyclic": "Cyclic",
    "rainbow": "Rainbow",
    "color_wipe": "Color Wipe",
    "theater_chase": "Theater Chase",
    "sparkle": "Sparkle",
}

# Default update interval
DEFAULT_UPDATE_INTERVAL = 30

# Default update interval
DEFAULT_UPDATE_INTERVAL = 30

# zeroconf service type
ZEROCONF_TYPE = "_koiosdigital._tcp.local."
