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
OTHER_BIRTHDAYS = {
    "Mom": "01-01",
    "Dad": "01-01",
}

# =============================================================================
# HOLIDAYS (set False to disable)
# =============================================================================

HOLIDAYS = {
    "valentines": True,         # Feb 14
    "st_patricks": False,       # Mar 17
    "easter": False,            # variable
    "july_4th": False,          # Jul 4
    "halloween": True,          # Oct 31
    "thanksgiving": False,      # 4th Thu Nov
    "chanukah": False,          # variable (~Dec)
    "christmas": False,         # Dec 25
    "new_years": True,          # Dec 31
    "chinese_new_year": False,  # variable (Jan/Feb)
}

# =============================================================================
# QUIET HOURS (dim/ambient mode)
# =============================================================================

QUIET_HOURS_START = "23:00"  # 24-hour format
QUIET_HOURS_END = "07:00"
QUIET_MODE = "starfield"     # options: starfield, off, dim
QUIET_BRIGHTNESS = 20        # 0-100
