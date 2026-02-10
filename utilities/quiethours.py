"""
Quiet hours utility for FlightTracker.

Provides functions to check if the display should be dimmed or off
based on configurable weekday/weekend schedules.
"""
from datetime import datetime, time
from utilities.datenow import get_now


def _parse_time(time_str):
    """Parse HH:MM time string to time object."""
    try:
        hour, minute = map(int, time_str.split(':'))
        return time(hour, minute)
    except (ValueError, AttributeError):
        return None


def _time_in_range(start_str, end_str, check_time=None):
    """Check if current time is within a time range.

    Handles ranges that cross midnight (e.g., 22:00 to 02:00).
    """
    if check_time is None:
        check_time = get_now().time()

    start = _parse_time(start_str)
    end = _parse_time(end_str)

    if start is None or end is None:
        return False

    if start <= end:
        # normal range (e.g., 09:00 to 17:00)
        return start <= check_time <= end
    else:
        # crosses midnight (e.g., 22:00 to 02:00)
        return check_time >= start or check_time <= end


def _is_weekend():
    """Check if today is a weekend (Saturday=5, Sunday=6)."""
    return get_now().weekday() >= 5


def _load_schedule():
    """Load quiet schedule from config."""
    try:
        from config import QUIET_SCHEDULE
        return QUIET_SCHEDULE
    except (ImportError, NameError):
        return None


def _load_legacy_config():
    """Load legacy quiet hours config."""
    try:
        from config import QUIET_HOURS_START, QUIET_HOURS_END, QUIET_MODE, QUIET_BRIGHTNESS
        return {
            "start": QUIET_HOURS_START,
            "end": QUIET_HOURS_END,
            "mode": QUIET_MODE,
            "brightness": QUIET_BRIGHTNESS,
        }
    except (ImportError, NameError):
        return None


def get_quiet_status():
    """Get current quiet hours status.

    Returns:
        dict with:
            'mode': 'normal', 'dim', or 'off'
            'brightness': brightness level (0-100) if dim mode
    """
    schedule = _load_schedule()

    if schedule:
        # use new schedule system
        day_type = "weekend" if _is_weekend() else "weekday"
        day_schedule = schedule.get(day_type, {})

        # check if in "off" period first (takes priority)
        off_config = day_schedule.get("off", {})
        if off_config:
            start = off_config.get("start")
            end = off_config.get("end")
            if start and end and _time_in_range(start, end):
                return {"mode": "off", "brightness": 0}

        # check if in "dim" period
        dim_config = day_schedule.get("dim", {})
        if dim_config:
            start = dim_config.get("start")
            end = dim_config.get("end")
            brightness = dim_config.get("brightness", 30)
            if start and end and _time_in_range(start, end):
                return {"mode": "dim", "brightness": brightness}

        return {"mode": "normal", "brightness": 100}

    # fall back to legacy config
    legacy = _load_legacy_config()
    if legacy:
        mode = legacy.get("mode", "off")
        if mode == "off":
            return {"mode": "normal", "brightness": 100}

        start = legacy.get("start")
        end = legacy.get("end")
        if start and end and _time_in_range(start, end):
            if mode == "dim":
                return {"mode": "dim", "brightness": legacy.get("brightness", 30)}
            else:
                return {"mode": "off", "brightness": 0}

        return {"mode": "normal", "brightness": 100}

    # no config, return normal
    return {"mode": "normal", "brightness": 100}


def should_display_be_off():
    """Check if display should be completely off."""
    return get_quiet_status()["mode"] == "off"


def should_display_be_dim():
    """Check if display should be dimmed."""
    return get_quiet_status()["mode"] == "dim"


def get_brightness():
    """Get current brightness level based on quiet hours."""
    status = get_quiet_status()
    return status["brightness"]
