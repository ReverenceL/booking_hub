from collections.abc import Awaitable, Callable
from dataclasses import dataclass
from datetime import tzinfo
from typing import Any

from aiogram.fsm.state import State
from aiogram_dialog import DialogManager
from babel.dates import get_timezone, get_timezone_location

from hub.domain.models.timezone import TimeZone


@dataclass
class TimeZoneName:
    """A dataclass containing the time zone and the current time in the time zone."""

    zone_name: str
    timezone: TimeZone


def get_city_name_from_timezone(timezone: tzinfo) -> str:
    timezone = get_timezone(timezone)
    location = get_timezone_location(timezone, locale="ru_RU")
    city_name = location.split(",")[0]
    if "(" in city_name:
        return city_name.split("(")[1].split(")")[0]
    return city_name


async def timezones_getter(**_: Any) -> dict[str, list[TimeZoneName]]:
    """Get the available time zones and the current time in each of them.

    :return: dictionary with timezones
    """

    timezones = []
    for timezone in TimeZone:
        timezones.append(  # noqa: PERF401
            TimeZoneName(
                zone_name=get_city_name_from_timezone(timezone),
                timezone=TimeZone(timezone),
            ),
        )
    return {"timezones": timezones}


def open_with_bot_id(state: State) -> Callable[[Any, Any, DialogManager], Awaitable[None]]:
    async def open_window(_: Any, __: Any, dialog_manager: DialogManager) -> None:
        await dialog_manager.start(state, data=dialog_manager.start_data)

    return open_window


async def put_start_data_to_dialog_data(start_data: dict[str, Any], dialog_manager: DialogManager) -> None:
    dialog_manager.dialog_data.update(start_data)
