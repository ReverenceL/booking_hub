from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Column, Select, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Jinja, Multi
from dishka import FromDishka

from hub.application.bot.get import GetBot, GetBotDTO
from hub.application.bot.get_cities import GetBotCities, GetBotCitiesDTO
from hub.application.client.create import CreateClient, CreateClientDTO
from hub.application.client.exceptions import ClientTelegramIdNotExistsError
from hub.application.client.get import GetClient, GetClientDTO
from hub.domain.models.city import CityId
from hub.infrastructure.di.injectors import inject_getter, inject_handler, inject_trigger
from ..state_groups.appointments import ClientAppointmentsSG
from ..state_groups.booking import BookingSG
from ..state_groups.main_menu import MainMenuSG, RegistrationSG


@inject_trigger
async def check_client_register(
    _: Any,
    dialog_manager: DialogManager,
    get_bot: FromDishka[GetBot],
    get_client: FromDishka[GetClient],
    get_bot_cities: FromDishka[GetBotCities],
    create_client: FromDishka[CreateClient],
) -> None:
    bot = await get_bot(GetBotDTO(telegram_id=dialog_manager.middleware_data["bot"].id))
    if dialog_manager.event.from_user is None:
        raise ValueError("User cannot be None")
    try:
        await get_client(
            GetClientDTO(
                bot_id=bot.id,
                telegram_id=dialog_manager.event.from_user.id,
            ),
        )
        await dialog_manager.start(MainMenuSG.MENU)
    except ClientTelegramIdNotExistsError:
        cities = await get_bot_cities(GetBotCitiesDTO(bot_id=bot.id))
        if len(cities) == 1:
            await create_client(
                CreateClientDTO(
                    name=dialog_manager.event.from_user.full_name,
                    telegram_id=dialog_manager.event.from_user.id,
                    bot_telegram_id=bot.telegram_id,
                    city_id=cities[0].id,
                ),
            )
            await dialog_manager.start(MainMenuSG.MENU)


@inject_getter
async def registration_get_city_getter(
    dialog_manager: DialogManager,
    get_bot_cities: FromDishka[GetBotCities],
    **_: Any,
) -> dict[str, Any]:
    if dialog_manager.event.bot is None:
        raise ValueError("Bot cannot be None")
    cities = await get_bot_cities(
        GetBotCitiesDTO(
            bot_telegram_id=dialog_manager.event.bot.id,
        ),
    )
    return {
        "cities": cities,
    }


@inject_handler
async def process_select_city(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    city_id: CityId,
    create_client: FromDishka[CreateClient],
) -> None:
    if dialog_manager.event.from_user is None:
        raise ValueError("User cannot be None")
    await create_client(
        CreateClientDTO(
            name=dialog_manager.event.from_user.full_name,
            telegram_id=dialog_manager.event.from_user.id,
            bot_telegram_id=dialog_manager.middleware_data["bot"].id,
            city_id=city_id,
        ),
    )
    await dialog_manager.start(MainMenuSG.MENU)


registration_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Привет, для прохождения регистрации выберите ваш город:"),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="select.city",
                items="cities",
                item_id_getter=lambda city: city.id,
                type_factory=CityId,
                on_click=process_select_city,
            ),
        ),
        state=RegistrationSG.GET_CITY,
        getter=registration_get_city_getter,
    ),
    on_start=check_client_register,
)

main_menu_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("👋 Привет!"),
            Const("Это бот для записи на услуги. Поможет записаться в пару кликов к нам на прием!"),
            Const("⚡️ Удобнее, чем через сайт. Быстрее, чем через звонок!"),
            sep="\n\n",
        ),
        Start(Const("😎 Хочу записаться"), id="open.booking", state=BookingSG.GET_SERVICE),
        Start(Const("📋 Мои записи"), id="open.appointments", state=ClientAppointmentsSG.LIST),
        state=MainMenuSG.MENU,
    ),
    launch_mode=LaunchMode.ROOT,
)
