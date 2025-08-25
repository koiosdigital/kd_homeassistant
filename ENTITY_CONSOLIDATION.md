# Entity Consolidation Changes

## Summary

Consolidated the Koios Digital Clock Home Assistant component to remove separate brightness and effect entities, integrating these controls directly into the light entities as requested.

## Changes Made

### 1. Light Entities (`light.py`)

- **KoiosClockBacklight**: Now includes brightness control (0-255) and effect selection
- **KoiosClockNixieTubes**: Now includes brightness control (0-100% converted to 0-255 for HA)
- **KoiosClockFibonacciTheme**: Already had brightness control and theme effects

### 2. Effect List from API (`coordinator.py` & `light.py`)

- **Coordinator**: Now fetches available effects from `/api/led/effects` endpoint
- **Light Entity**: `effect_list` property dynamically populated from API data
- **Fallback**: If API data unavailable, falls back to hardcoded `LED_EFFECTS` mapping
- **Effect Mapping**: Translates between API effect names and IDs correctly

### 3. Removed Separate Entities

#### Number Entities (`number.py`)

- ❌ Removed `KoiosClockLEDBrightnessNumber`
- ❌ Removed `KoiosClockNixieBrightnessNumber`
- ❌ Removed `KoiosClockFibonacciBrightnessNumber`
- ✅ Brightness now controlled via light entities

#### Select Entities (`select.py`)

- ❌ Removed `KoiosClockLEDEffectSelect`
- ✅ Effects now controlled via light entity effect feature
- ✅ Kept `KoiosClockFibonacciThemeSelect` (still needed for theme selection)

### 4. Updated Entity Mapping

| Device Type   | Light Entities          | Controls                                                  |
| ------------- | ----------------------- | --------------------------------------------------------- |
| **Nixie**     | Backlight + Nixie Tubes | Backlight: brightness + effects<br>Nixie: brightness only |
| **Wordclock** | Backlight only          | Brightness + effects                                      |
| **Fibonacci** | Theme light             | Brightness + theme effects                                |

### 5. Services Updated (`services.py`)

- Updated `set_led_effect` service to use API effect data for proper ID mapping
- Services now work with the consolidated light entities

## Benefits

### ✅ **Simplified Entity Structure**

- Fewer entities in Home Assistant UI
- Related controls grouped logically in light entities
- Standard Home Assistant light controls (brightness slider, effect dropdown)

### ✅ **Dynamic Effect Discovery**

- Effect list populated from `/api/led/effects` endpoint
- Supports new effects added to firmware without component updates
- Proper mapping between effect names and API IDs

### ✅ **Better User Experience**

- Brightness and effects in same control panel
- Standard light entity behavior users expect
- Native Home Assistant light card support

### ✅ **Maintained Functionality**

- All previous functionality preserved
- Brightness control: 0-255 for LEDs, 0-100% for Nixie (auto-converted)
- Effect selection with proper API ID mapping
- Immediate state updates after changes

## Technical Implementation

### Effect List Population

```python
# From API data (preferred)
led_effects_data = coordinator.data.get("led_effects", [])
effects = [effect.get("name") for effect in led_effects_data]

# Fallback to hardcoded
effects = list(LED_EFFECTS.values())
```

### Effect ID Mapping

```python
# Find API effect ID from display name
for effect in led_effects_data:
    if effect.get("name") == effect_name:
        effect_id = effect.get("id", "SOLID")
        break
```

### Entity Capabilities

- **Backlight Light**: Brightness (0-255) + Effects + RGBW Color
- **Nixie Light**: Brightness (0-255, converted from 0-100%)
- **Fibonacci Light**: Brightness (0-255) + Theme Effects

The component now provides a cleaner, more intuitive interface while maintaining all functionality and adding dynamic effect discovery from the API.
