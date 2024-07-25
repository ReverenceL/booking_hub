from collections.abc import Callable
from datetime import datetime
from typing import Any

import pytz


def current_time_with_timezone(tz: str, date_format: str = "%H:%M") -> str:
    return datetime.now(tz=pytz.timezone(tz)).strftime(date_format)


jinja_filters: dict[str, Callable[..., Any]] = {
    "current_time_with_timezone": current_time_with_timezone,
}
