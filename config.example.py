# FlightTracker Configuration
# Copy this file to config.py and customize for your location

# =============================================================================
# LOCATION SETTINGS
# =============================================================================

# Zone is ~45km box around your location
# Get coordinates from Google Maps (right-click your location)
ZONE_HOME = {
    "tl_y": 41.15,    # lat + 0.4 (~45km box)
    "tl_x": -74.40,   # long - 0.4
    "br_y": 40.35,    # lat - 0.4
    "br_x": -73.60    # long + 0.4
}

LOCATION_HOME = [40.75, -74.00, 0.010]  # lat, long, altitude in km

WEATHER_LOCATION = "New York, NY"
JOURNEY_CODE_SELECTED = "LGA"  # nearby airport to highlight

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

BRIGHTNESS = 80
GPIO_SLOWDOWN = 4
MIN_ALTITUDE = 5000  # feet - filters out high-altitude cruising flights
TEMPERATURE_UNITS = "imperial"  # or "metric"
JOURNEY_BLANK_FILLER = " ? "
HAT_PWM_ENABLED = False
HARDWARE_PULSE = False
LED_RGB_SEQUENCE = "RGB"  # try "RBG", "BGR", or "GRB" if colors look wrong

# =============================================================================
# API KEYS
# =============================================================================

# Get free key from https://openweathermap.org/api
OPENWEATHER_API_KEY = ""

# =============================================================================
# SPECIAL DATES (MM-DD format)
# =============================================================================

MY_BIRTHDAY = "01-01"
PARTNER_BIRTHDAY = "01-01"
ANNIVERSARY = "01-01"

# OTHER_BIRTHDAYS supports two formats:
# Simple: just the date string
#   "Mom": "03-15"
# With countdown: dict with date and countdown days (default: 3)
#   "Mom": {"date": "03-15", "countdown": 5}
#
# MY_BIRTHDAY and PARTNER_BIRTHDAY show on the day only (no countdown)
# OTHER_BIRTHDAYS will show countdown X days before
OTHER_BIRTHDAYS = {
    "Mom": {"date": "01-01", "countdown": 5},
    "Dad": {"date": "01-01", "countdown": 5},
}

# =============================================================================
# HOLIDAYS (set False to disable)
# =============================================================================

HOLIDAYS = {
    "valentines": True,         # Feb 14
    "st_patricks": True,        # Mar 17
    "easter": False,            # variable
    "independence_day": True,   # Jul 4
    "halloween": True,          # Oct 31
    "thanksgiving": True,       # 4th Thu Nov
    "chanukah": True,           # variable (~Dec)
    "christmas": False,         # Dec 25
    "new_years": True,          # Dec 31
    "chinese_new_year": True,   # variable (Jan/Feb)
}

# =============================================================================
# QUIET HOURS (dim/off schedules)
# =============================================================================

# Enhanced quiet hours with separate weekday/weekend schedules
# Each schedule can have "dim" and "off" periods
# Times are in 24-hour format (HH:MM)
# "off" takes priority over "dim" when both overlap
QUIET_SCHEDULE = {
    "weekday": {
        "dim": {"start": "22:00", "end": "02:00", "brightness": 30},
        "off": {"start": "02:00", "end": "06:00"},
    },
    "weekend": {
        "dim": {"start": "23:00", "end": "02:00", "brightness": 30},
        "off": {"start": "02:00", "end": "07:00"},
    },
}

# Legacy quiet hours (deprecated, use QUIET_SCHEDULE instead)
# If QUIET_SCHEDULE is not defined, these values are used as fallback
QUIET_HOURS_START = "23:00"  # 24-hour format
QUIET_HOURS_END = "07:00"
QUIET_MODE = "off"           # options: off, dim
QUIET_BRIGHTNESS = 20        # 0-100 (only used when mode is "dim")

# =============================================================================
# CUSTOM MESSAGES
# =============================================================================

# Love messages and quotes appear randomly every 60-90 minutes when idle
# (no flights overhead). They display for up to 3 minutes with a pulsing
# heart, then return to the normal heartbeat idle animation.
# Flights will interrupt early if detected.

# rotating love messages
LOVE_MESSAGES = [
    "I love you",
    "You're amazing",
    "Thinking of you",
    "Miss you",
    "You make me happy",
    "XOXO",
    "Forever yours",
    "My favorite person",
]

# inspirational quotes
# recommended: 40 chars max for best readability
# - 12 chars or fewer: displays centered on screen
# - 13-40 chars: scrolls smoothly across the display
# - 40+ chars: still works but takes longer per scroll cycle
QUOTES = [
    "Be the change",
    "Stay curious",
    "One day at a time",
    "Do what you love",
]
