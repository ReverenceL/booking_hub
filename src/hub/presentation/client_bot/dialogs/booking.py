from typing import Any

from aiogram import F
from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.kbd import NextPage, PrevPage, Row, ScrollingGroup, Select, Start, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Jinja, Multi
from dishka import FromDishka

from hub.application.bot.get import GetBot, GetBotDTO
from hub.application.bot.get_services import GetBotServices, GetBotServicesDTO
from hub.application.city.get import GetCity, GetCityDTO
from hub.application.client.get import GetClient, GetClientDTO
from hub.application.service.get import GetService, GetServiceDTO
from hub.domain.models.service import ServiceId
from hub.infrastructure.di.injectors import inject_getter
from hub.presentation.client_bot.custom_widgets.calendar import BookingCalendar
from hub.presentation.client_bot.state_groups.booking import BookingSG
from hub.presentation.client_bot.state_groups.main_menu import MainMenuSG

SERVICE_SCROLL_ID = "service.scroll"


@inject_getter
async def booking_get_service_getter(
    dialog_manager: DialogManager,
    get_bot_services: FromDishka[GetBotServices],
    **_: Any,
) -> dict[str, Any]:
    if dialog_manager.event.bot is None:
        raise ValueError("Bot cannot be None")
    services = await get_bot_services(GetBotServicesDTO(bot_telegram_id=dialog_manager.event.bot.id))
    return {
        "services": services,
    }


@inject_getter
async def booking_get_date_getter(
    dialog_manager: DialogManager,
    get_bot: FromDishka[GetBot],
    get_client: FromDishka[GetClient],
    get_city: FromDishka[GetCity],
    **_: Any,
) -> dict[str, Any]:
    if dialog_manager.event.bot is None:
        raise ValueError("Bot cannot be None")
    elif dialog_manager.event.from_user is None:
        raise ValueError("User cannot be None")
    bot = await get_bot(GetBotDTO(telegram_id=dialog_manager.event.bot.id))
    client = await get_client(
        GetClientDTO(
            bot_id=bot.id,
            telegram_id=dialog_manager.event.from_user.id,
        ),
    )
    city = await get_city(GetCityDTO(city_id=client.city_id))
    return {
        "client": client,
        "timezone": city.timezone,
    }


@inject_getter
async def booking_get_time_getter(
    dialog_manager: DialogManager,  # noqa: ARG001
    **_: Any,
) -> dict[str, Any]:
    return {}


@inject_getter
async def booking_service_description_getter(
    dialog_manager: DialogManager,
    get_service: FromDishka[GetService],
    **_: Any,
) -> dict[str, Any]:
    service = await get_service(GetServiceDTO(service_id=dialog_manager.dialog_data["service_id"]))
    return {"service": service}


async def process_get_service(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    service_id: ServiceId,
) -> None:
    dialog_manager.dialog_data["service_id"] = service_id
    await dialog_manager.switch_to(BookingSG.GET_DATE)


booking_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("📜 Список услуг, которые мы оказываем."),
            Const("Выбирайте, куда на что хотите записаться 👇"),
            sep="\n\n",
        ),
        ScrollingGroup(
            Select(
                Jinja("{{ item.name }}"),
                id="select.service",
                item_id_getter=lambda service: service.id,
                type_factory=ServiceId,
                items="services",
                on_click=process_get_service,
            ),
            id=SERVICE_SCROLL_ID,
            width=1,
            height=6,
            hide_pager=True,
        ),
        Row(
            PrevPage(scroll=SERVICE_SCROLL_ID, text=Const("⬅️"), when=F["pages"] > 1),
            NextPage(scroll=SERVICE_SCROLL_ID, text=Const("➡️"), when=F["pages"] > 1),
        ),
        Start(Const("↩️ Назад"), id="close", state=MainMenuSG.MENU),
        state=BookingSG.GET_SERVICE,
        getter=booking_get_service_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("📆 Когда Вам удобнее прийти?"),
            Const("Если хотите побольше узнать об услуге, нажмите кнопку «📋 Об услуге»"),
            Const("Нажмите на день, в который хотите прийти 👇"),
            sep="\n\n",
        ),
        SwitchTo(Const("📋 Об услуге"), id="open.description", state=BookingSG.SERVICE_DESCRIPTION),
        BookingCalendar(id="calendar"),
        SwitchTo(Const("↩️ Назад"), id="open.menu", state=BookingSG.GET_SERVICE),
        state=BookingSG.GET_DATE,
        getter=booking_get_date_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("🕰 День назначили, а время?"),
            Const("Нажмите на время, к которому придете 👇"),
            sep="\n\n",
        ),
        state=BookingSG.GET_TIME,
        getter=booking_get_time_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("{{ service.description }}"),
        SwitchTo(Const("↩️ Назад"), id="back.to.date", state=BookingSG.GET_DATE),
        state=BookingSG.SERVICE_DESCRIPTION,
        getter=booking_service_description_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("👍 Вы записаны!"),
            Multi(
                Jinja("Дата: {{ dialog_data.booking_date }}"),
                Jinja("Время начала: {{ dialog_data.booking_time }}"),
                Jinja("Записан к: {{ dialog_data.master_name }}"),
                sep="\n",
            ),
            Const("Ждем Вас, не опаздывайте! 🤗"),
            sep="\n\n",
        ),
        state=BookingSG.SUCCESS_BOOKING,
    ),
)
