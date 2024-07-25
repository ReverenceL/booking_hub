from datetime import date, datetime
from typing import Any

from aiogram_dialog import DialogManager
from aiogram_dialog.widgets.kbd import Calendar, CalendarScope, CalendarUserConfig
from aiogram_dialog.widgets.kbd.calendar_kbd import (
    CalendarDaysView,
    CalendarMonthView,
    CalendarScopeView,
    CalendarYearsView,
)
from aiogram_dialog.widgets.text import Const, Text
from babel.dates import get_day_names, get_month_names
from pytz import timezone


class RuWeekDay(Text):
    def __init__(self, locale):
        super().__init__()
        self.locale = locale

    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        return get_day_names(width="short", context="stand-alone", locale=self.locale)[selected_date.weekday()].title()


class RuMonth(Text):
    def __init__(self, locale):
        super().__init__()
        self.locale = locale

    async def _render_text(self, data, manager: DialogManager) -> str:
        selected_date: date = data["date"]
        return get_month_names("wide", context="stand-alone", locale=self.locale)[selected_date.month].title()


class BookingCalendar(Calendar):
    async def _get_user_config(
        self,
        data: dict[str, Any],
        manager: DialogManager,
    ) -> CalendarUserConfig:
        tz = timezone(data["timezone"])
        return CalendarUserConfig(
            timezone=tz,
            min_date=datetime.now(tz=tz).date(),
        )

    def _init_views(self) -> dict[CalendarScope, CalendarScopeView]:
        return {
            CalendarScope.DAYS: CalendarDaysView(
                self._item_callback_data,
                header_text=Const("Дни за месяц: ") + RuMonth("ru_RU"),
                weekday_text=RuWeekDay("ru_RU"),
                next_month_text=RuMonth("ru_RU") + " >>",
                prev_month_text="<< " + RuMonth("ru_RU"),
                zoom_out_text=Const(""),
            ),
            CalendarScope.MONTHS: CalendarMonthView(
                self._item_callback_data,
                month_text=RuMonth("ru_RU"),
                this_month_text=Const("[") + RuMonth("ru_RU") + Const("]"),
            ),
            CalendarScope.YEARS: CalendarYearsView(
                self._item_callback_data,
            ),
        }
