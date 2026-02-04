# FlightTracker Configuration
# Copy this file to config.py and customize for your location

# =============================================================================
# LOCATION SETTINGS
# =============================================================================

# Zone is ~20km box around your location
# Get coordinates from Google Maps (right-click your location)
ZONE_HOME = {
    "tl_y": 40.85,    # lat + 0.1
    "tl_x": -74.10,   # long - 0.1
    "br_y": 40.65,    # lat - 0.1
    "br_x": -73.90    # long + 0.1
}

LOCATION_HOME = [40.75, -74.00, 0.010]  # lat, long, altitude in km

WEATHER_LOCATION = "New York, NY"
JOURNEY_CODE_SELECTED = "LGA"  # nearby airport to highlight

# =============================================================================
# DISPLAY SETTINGS
# =============================================================================

BRIGHTNESS = 50
GPIO_SLOWDOWN = 4
MIN_ALTITUDE = 100
TEMPERATURE_UNITS = "imperial"  # or "metric"
JOURNEY_BLANK_FILLER = " ? "
HAT_PWM_ENABLED = False
HARDWARE_PULSE = False
LED_RGB_SEQUENCE = "RGB"  # try "BGR" or "GRB" if colors look wrong

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
    "Mom": "01-01",
    "Dad": {"date": "01-01", "countdown": 5},
}

# =============================================================================
# HOLIDAYS (set False to disable)
# =============================================================================

HOLIDAYS = {
    "valentines": True,         # Feb 14
    "st_patricks": False,       # Mar 17
    "easter": False,            # variable
    "independence_day": False,  # Jul 4
    "halloween": True,          # Oct 31
    "thanksgiving": False,      # 4th Thu Nov
    "chanukah": False,          # variable (~Dec)
    "christmas": False,         # Dec 25
    "new_years": True,          # Dec 31
    "chinese_new_year": False,  # variable (Jan/Feb)
}

# =============================================================================
# QUIET HOURS (dim/off schedules)
# =============================================================================

# NEW: Enhanced quiet hours with separate weekday/weekend schedules
# Each schedule can have "dim" and "off" periods
# Times are in 24-hour format (HH:MM)
# "off" takes priority over "dim" when both overlap
QUIET_SCHEDULE = {
    "weekday": {
        "dim": {
            "start": "22:00",
            "end": "02:00",
            "brightness": 30,
        },
        "off": {
            "start": "02:00",
            "end": "06:00",
        },
    },
    "weekend": {
        "dim": {
            "start": "23:00",
            "end": "02:00",
            "brightness": 30,
        },
        "off": {
            "start": "02:00",
            "end": "07:00",
        },
    },
}

# LEGACY: Simple quiet hours (deprecated, use QUIET_SCHEDULE instead)
# If QUIET_SCHEDULE is not defined, these values are used as fallback
QUIET_HOURS_START = "23:00"  # 24-hour format
QUIET_HOURS_END = "07:00"
QUIET_MODE = "off"           # options: off, dim
QUIET_BRIGHTNESS = 20        # 0-100 (only used when mode is "dim")

# =============================================================================
# CUSTOM MESSAGES
# =============================================================================

# rotating love messages shown when no flights overhead
# leave empty or remove to use defaults
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
