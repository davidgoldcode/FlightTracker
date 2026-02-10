# FlightTracker Configuration
# Copy this file to config.py and customize for your location

# =============================================================================
# LOCATION SETTINGS
# =============================================================================

# Zone is the bounding box for flight detection
# Get coordinates from Google Maps (right-click your location)
# Make this big enough to cover your viewable sky; the window view
# filter below handles directional precision
ZONE_HOME = {
    "tl_y": 40.14,    # north boundary
    "tl_x": -105.39,  # west boundary
    "br_y": 39.34,    # south boundary
    "br_x": -104.59   # east boundary
}

LOCATION_HOME = [39.74, -104.99, 1.609]  # lat, long, altitude in km

WEATHER_LOCATION = "Denver, CO"
JOURNEY_CODE_SELECTED = "DEN"  # nearby airport to highlight

# =============================================================================
# WINDOW VIEW FILTER (optional)
# =============================================================================

# Filter flights to only show ones visible from your window
# Set to the compass direction your window faces and your field of view
# Omit or comment out to disable (shows all flights in zone)
#
# WINDOW_BEARING: degrees from north, clockwise (0=N, 90=E, 180=S, 270=W)
# WINDOW_FOV: total degrees of visible sky from your window
#
# To calculate: find your location and a landmark you can see in Google Maps,
# right-click both, note coordinates, then use a bearing calculator
WINDOW_BEARING = 250  # WSW (example: facing Manhattan from Brooklyn)
WINDOW_FOV = 120      # degrees of visible sky

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

# =============================================================================
# DEBUG / TESTING
# =============================================================================

# Override the date for testing holiday animations without changing system clock
# Format: "MM-DD" (e.g., "12-31" for New Year's Eve, "10-31" for Halloween)
# Time (hours/minutes/seconds) stays real, only the date changes
# Comment out or set to "" to use the real date
# DEBUG_DATE = "12-31"
