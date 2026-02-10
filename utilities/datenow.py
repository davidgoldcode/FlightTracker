"""centralized date/time helper with optional DEBUG_DATE override."""
import sys
from datetime import datetime


def get_now():
    """get current datetime, with optional date override from config.

    if DEBUG_DATE is set in config (format: "MM-DD"), returns a datetime
    with that month/day but real hours/minutes/seconds. this allows
    testing holiday animations without changing the system clock.
    """
    now = datetime.now()

    try:
        from config import DEBUG_DATE
    except (ImportError, NameError):
        return now

    if not DEBUG_DATE:
        return now

    try:
        month, day = map(int, DEBUG_DATE.split("-"))
        return now.replace(month=month, day=day)
    except (ValueError, AttributeError):
        print(f"[WARNING] invalid DEBUG_DATE '{DEBUG_DATE}', using real date", file=sys.stderr)
        return now
