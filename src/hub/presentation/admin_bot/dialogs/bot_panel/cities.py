from datetime import datetime
from operator import itemgetter
from typing import Any

import pytz
from aiogram import F
from aiogram.types import CallbackQuery
from aiogram.utils.i18n import gettext as _
from aiogram_dialog import Dialog, DialogManager, LaunchMode, SubManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Column, Group, Row, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from babel.dates import get_timezone_name
from dishka import FromDishka

from hub.application.bot.get_cities import GetBotCities, GetBotCitiesDTO
from hub.application.city.create import CreateCity, CreateCityDTO
from hub.application.city.delete import DeleteCity, DeleteCityDTO
from hub.application.city.get import GetCity, GetCityDTO
from hub.application.city.update import CityUpdate, CityUpdateDTO
from hub.domain.models.city import CityId, CityName
from hub.domain.models.timezone import TimeZone
from hub.infrastructure.di.injectors import inject_getter, inject_handler
from hub.presentation.admin_bot.state_groups.bot_panel import AddCitySG, BotPanelSG, CitySG
from ..common import TimeZoneName, open_with_bot_id, timezones_getter


@inject_getter
async def city_list_getter(
    dialog_manager: DialogManager,
    get_bot_cities: FromDishka[GetBotCities],
    **_: Any,
) -> dict[str, Any]:
    cities = await get_bot_cities(
        GetBotCitiesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "cities": cities,
    }


@inject_getter
async def city_getter(
    dialog_manager: DialogManager,
    get_city: FromDishka[GetCity],
    **_: Any,
) -> dict[str, Any]:
    city = await get_city(GetCityDTO(city_id=dialog_manager.dialog_data["city_id"]))
    return {
        "city": city,
        "city_timezone": get_timezone_name(city.timezone, locale="ru_RU"),
    }


@inject_handler
async def process_delete_city(
    callback_query: CallbackQuery,
    widget: Any,
    dialog_manager: DialogManager,
    delete_city: FromDishka[DeleteCity],
) -> None:
    await delete_city(
        DeleteCityDTO(
            city_id=dialog_manager.dialog_data["city_id"],
        ),
    )
    await dialog_manager.switch_to(state=CitySG.LIST)


@inject_handler
async def process_update_name(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    name: str,
    update_city: FromDishka[CityUpdate],
) -> None:
    await update_city(
        CityUpdateDTO(
            city_id=dialog_manager.dialog_data["city_id"],
            name=name,
        ),
    )
    await dialog_manager.switch_to(state=CitySG.LIST)


@inject_handler
async def process_update_timezone(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    timezone: TimeZone,
    update_city: FromDishka[CityUpdate],
) -> None:
    await update_city(
        CityUpdateDTO(
            city_id=dialog_manager.dialog_data["city_id"],
            timezone=timezone,
        ),
    )
    await dialog_manager.switch_to(state=CitySG.LIST)


@inject_handler
async def process_select_city(_: Any, __: Any, dialog_manager: DialogManager, city_id: CityId) -> None:
    dialog_manager.dialog_data["city_id"] = city_id
    await dialog_manager.switch_to(state=CitySG.EDITOR)


cities_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Список городов в боте:", when=F["cities"]),
        Multi(
            Const("Похоже, Вы не добавили ни одного города."),
            Const("Давайте добавим!"),
            sep="\n\n",
            when=~F["cities"],
        ),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="select.city",
                items=F["cities"],
                item_id_getter=lambda city: city.id,
                type_factory=CityId,
                on_click=process_select_city,
            ),
        ),
        Row(
            Button(Const("⬅️ Назад"), id="back.to.menu", on_click=open_with_bot_id(BotPanelSG.MENU)),
            Button(Const("➕ Добавить город"), id="add.city", on_click=open_with_bot_id(AddCitySG.GET_NAME)),

        ),
        state=CitySG.LIST,
        getter=city_list_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Настройки города: {{ city.name }}"),
            Jinja("Часовой пояс: {{ city_timezone }}"),
            sep="\n\n",
        ),
        SwitchTo(Const("Сменить название"), id="open.edit.name", state=CitySG.EDIT_NAME),
        SwitchTo(Const("Сменить часовой пояс"), id="open.edit.timezone", state=CitySG.EDIT_TIMEZONE),
        Row(
            SwitchTo(Const("↩️ Назад"), id="open.list", state=CitySG.LIST),
            SwitchTo(Const("❌ Удалить"), id="open.delete.city", state=CitySG.DELETE),
        ),
        state=CitySG.EDITOR,
        getter=city_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Меняем название города: {{ city.name }}!"),
            Const("Отправьте новое название:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.name",
            on_success=process_update_name,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.editor", state=CitySG.EDITOR),
        state=CitySG.EDIT_NAME,
        getter=city_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Меняем часовой пояс города: {{ city.name }}"),
            Jinja("Часовой пояс сейчас: {{ city_timezone }}"),
            Const("Выберите новый часовой пояс 👇"),
            sep="\n\n",
        ),
        Group(
            Select(
                Format("{item.zone_name}"),
                id="get.timezone",
                items="timezones",
                item_id_getter=lambda tz: tz.timezone,
                type_factory=TimeZone,
                on_click=process_update_timezone,
            ),
            width=3,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.editor", state=CitySG.EDITOR),
        state=CitySG.EDIT_TIMEZONE,
        getter=(city_getter, timezones_getter),
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Удалить город?"),
            Const("Все отделения которые находятся в городе будут так же удалены."),
            sep="\n\n",
        ),
        Button(Const("✅ Да!"), id="delete.city", on_click=process_delete_city),
        SwitchTo(Const("↩️ Я передумал"), id="open.list", state=CitySG.LIST),
        state=CitySG.DELETE,
    ),
    launch_mode=LaunchMode.ROOT,
)


async def process_new_city_name(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    city_name: CityName,
) -> None:
    dialog_manager.dialog_data["city_name"] = city_name
    await dialog_manager.next()


@inject_handler
async def process_new_city_timezone(
    callback_query: CallbackQuery,
    _: Any,
    dialog_manager: DialogManager,
    timezone: TimeZone,
    create_city: FromDishka[CreateCity],
) -> None:
    await create_city(
        CreateCityDTO(
            bot_id=dialog_manager.start_data,
            name=dialog_manager.dialog_data["city_name"],
            timezone=timezone,
        ),
    )
    await dialog_manager.done()
    await callback_query.answer(text="Город добавлен!", show_alert=True)


add_city_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем город!"),
            Const("Отправьте название:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.city.name",
            on_success=process_new_city_name,
            type_factory=CityName,
        ),
        Cancel(Const("⬅️ Назад")),
        state=AddCitySG.GET_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем город!"),
            Jinja("Название: {{ dialog_data.city_name }}"),
            Const("Теперь боту нужно узнать часовой пояс города."),
            sep="\n\n",
        ),
        Group(
            Select(
                Format("{item.zone_name}"),
                id="get.timezone",
                items="timezones",
                item_id_getter=lambda tz: tz.timezone,
                on_click=process_new_city_timezone,
                type_factory=TimeZone,
            ),
            width=3,
        ),
        Cancel(Const("⬅️ Назад")),
        state=AddCitySG.GET_TIMEZONE,
        getter=timezones_getter,
    ),
)
