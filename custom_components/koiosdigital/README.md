# Koios Digital Clock Home Assistant Integration

This is a comprehensive Home Assistant custom integration for Koios Digital Clock devices. The integration supports automatic discovery via mDNS and provides full control over all device variants.

## Features

### Device Discovery

- Automatic discovery via mDNS (`_koiosdigital._tcp`)
- Manual configuration option
- Supports all device variants: Fibonacci, Nixie, and Wordclock

### Supported Device Variants

#### Fibonacci Clock

- **Light Entity**: Theme control with brightness
- **Select Entity**: Theme selection (RGB, Mondrian, Basbrun, 80's, Pastel, Modern, Cold, Warm, Earth, Dark)
- **Number Entity**: Brightness control (0-255)

#### Nixie Clock

- **Light Entity**: Backlight LED control (RGBW) with effects
- **Light Entity**: Nixie tube brightness control
- **Switch Entities**: Military time format, Blinking dots
- **Number Entities**: LED brightness (0-255), Nixie brightness (0-100%)

#### Wordclock

- **Light Entity**: LED control (RGBW) with effects and brightness
- **Select Entity**: LED effect selection
- **Number Entity**: LED brightness control (0-255)

### Common Features (All Variants)

- **LED Effects**: Off, Solid, Blink, Breathe, Cyclic, Rainbow
- **Full Color Control**: RGB/RGBW support where applicable
- **Real-time Updates**: 30-second polling interval
- **Device Information**: Firmware version, model, hostname

## Installation

1. Copy the `hass` folder to your Home Assistant `custom_components` directory
2. Rename the folder from `hass` to `koiosdigital`
3. Restart Home Assistant
4. Go to Configuration → Integrations → Add Integration
5. Search for "Koios Digital Clock"
6. Follow the setup wizard

## Configuration

### Automatic Discovery

The integration will automatically discover Koios clocks on your network via mDNS. Simply confirm the discovered device in the Home Assistant UI.

### Manual Configuration

If automatic discovery doesn't work:

1. Add integration manually
2. Enter the device's IP address
3. Enter the port (default: 80)

## API Endpoints

The integration communicates with the device using these REST API endpoints:

- `/api/about` - Device information
- `/api/led/config` - LED configuration (all variants)
- `/api/nixie/config` - Nixie-specific configuration
- `/api/fibonacci/config` - Fibonacci configuration
- `/api/fibonacci/themes` - Available Fibonacci themes

## Device Entities

### Entity Types by Device Model

#### All Devices

- `light.koiosdigital_backlight` - Backlight LED control

#### Fibonacci Clock Additional Entities

- `light.koiosdigital_theme` - Theme and brightness control
- `select.koiosdigital_fibonacci_theme` - Theme selection
- `number.koiosdigital_fibonacci_brightness` - Brightness slider

#### Nixie Clock Additional Entities

- `light.koiosdigital_nixie_tubes` - Tube brightness control
- `switch.koiosdigital_military_time` - 24-hour format toggle
- `switch.koiosdigital_blinking_dots` - Blinking separator dots
- `number.koiosdigital_nixie_brightness` - Nixie brightness slider

#### Common Entities (All Devices)

- `select.koiosdigital_led_effect` - LED effect selection
- `number.koiosdigital_led_brightness` - LED brightness control

## Supported LED Effects

- **Off**: Turn off LEDs
- **Solid**: Solid color display
- **Blink**: Blinking effect
- **Breathe**: Breathing/pulsing effect
- **Cyclic**: Cycling through colors
- **Rainbow**: Rainbow color pattern

## Fibonacci Themes

The Fibonacci clock supports multiple color themes:

- RGB (default)
- Mondrian
- Basbrun
- 80's
- Pastel
- Modern
- Cold
- Warm
- Earth
- Dark

## Troubleshooting

### Device Not Discovered

- Ensure the device is on the same network
- Check that mDNS is working on your network
- Try manual configuration with the device IP

### Connection Issues

- Verify the device is accessible via HTTP
- Check firewall settings
- Ensure the device API is responding

### Entity Updates

- The integration polls every 30 seconds
- Changes may take up to 30 seconds to reflect in Home Assistant
- Check the integration logs for any errors

## Development

This integration is built using the modern Home Assistant integration architecture:

- **Config Flow**: Automatic discovery and manual setup
- **Data Update Coordinator**: Centralized data management
- **Multiple Platforms**: Light, Switch, Select, and Number entities
- **Device Registry**: Proper device information and identification

## License

This integration is provided as-is for use with Koios Digital Clock devices.
