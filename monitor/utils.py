from datetime import datetime
from typing import Optional
from dateutil.parser import parse as parse_date


def date_or_none(datetime_string: Optional[str]) -> Optional[datetime]:
    if not datetime_string:
        return None

    return parse_date(datetime_string)


def angle_to_compass(angle):
    """
    Convert an angle in degrees to a compass direction.
    """
    val = int((angle / 45) + .5)
    arr = ["N", "NE", "E", "SE", "S", "SW", "W", "NW"]
    return arr[(val % 8)]
