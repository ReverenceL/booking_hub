from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Button, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Jinja
from dishka import FromDishka

from hub.application.bot.get import GetBot, GetBotDTO
from hub.infrastructure.di.injectors import inject_getter
from hub.presentation.admin_bot.state_groups.bot_panel import (
    BotPanelSG,
    BranchSG,
    CitySG,
    GeneralSettingsSG,
    MasterSG,
    ServiceSG,
)
from hub.presentation.admin_bot.state_groups.main import BotsListSG
from ..common import open_with_bot_id


@inject_getter
async def get_bot_data(
    dialog_manager: DialogManager,
    get_bot: FromDishka[GetBot],
    **_: Any,
) -> dict[str, Any]:
    bot = await get_bot(
        GetBotDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {"bot_name": bot.name}


bot_panel_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Бот «{{ bot_name }}»."),
        Button(Const("Настройки городов"), id="open.cities", on_click=open_with_bot_id(CitySG.LIST)),
        Button(Const("Настройки отделений"), id="open.branches", on_click=open_with_bot_id(BranchSG.LIST)),
        Button(Const("Настройки мастеров"), id="open.masters", on_click=open_with_bot_id(MasterSG.LIST)),
        Button(Const("Настройки услуг"), id="open.services", on_click=open_with_bot_id(ServiceSG.LIST)),
        Button(Const("Общие настройки"), id="open.settings", on_click=open_with_bot_id(GeneralSettingsSG.LIST)),
        Start(Const("↩️ Назад"), id="close.panel", state=BotsListSG.LIST),
        state=BotPanelSG.MENU,
        getter=get_bot_data,
    ),
    launch_mode=LaunchMode.ROOT,
)
