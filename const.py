"""Constants for the Koios Digital Clock integration."""

DOMAIN = "koios_clock"

# Device models
MODEL_FIBONACCI = "fibonacci"
MODEL_NIXIE = "nixie"
MODEL_WORDCLOCK = "wordclock"

# API endpoints
API_ABOUT = "/api/about"
API_LED_CONFIG = "/api/led/config"
API_NIXIE_CONFIG = "/api/nixie/config"
API_FIBONACCI_CONFIG = "/api/fibonacci/config"
API_FIBONACCI_THEMES = "/api/fibonacci/themes"

# LED effects
LED_EFFECTS = {
    "off": "Off",
    "solid": "Solid",
    "blink": "Blink",
    "breathe": "Breathe",
    "cyclic": "Cyclic",
    "rainbow": "Rainbow",
}

# Default update interval
DEFAULT_UPDATE_INTERVAL = 30

# zeroconf service type
ZEROCONF_TYPE = "_koiosdigital._tcp.local."
