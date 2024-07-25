from typing import Any

from aiogram_dialog import Dialog, DialogManager, LaunchMode, Window
from aiogram_dialog.widgets.kbd import Column, Select, Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format
from dishka import FromDishka

from hub.application.manager.get_bots import GetManagerBots, GetManagerBotsDTO
from hub.domain.models.bot import BotId
from hub.domain.models.manager import ManagerTelegramId
from hub.infrastructure.di.injectors import inject_getter
from ..state_groups.bot_panel import BotPanelSG
from ..state_groups.main import AddBotSG, BotsListSG


@inject_getter
async def manager_bots_getter(
    dialog_manager: DialogManager,
    get_manager_bots: FromDishka[GetManagerBots],
    **_: Any,
) -> dict[str, Any]:
    if dialog_manager.event.from_user is None:
        raise ValueError("User cannot be None")
    bots = await get_manager_bots(
        GetManagerBotsDTO(
            telegram_id=ManagerTelegramId(dialog_manager.event.from_user.id),
        ),
    )
    return {
        "bots": bots,
    }


async def process_select_bot(
    _: Any,
    __: Any,
    manager: DialogManager,
    bot_id: BotId,
) -> None:
    await manager.start(BotPanelSG.MENU, data=bot_id)


bots_list_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Список ваших ботов:"),
        Column(
            Select(
                text=Format("🤖 «{item.name}»"),
                id="select.bot",
                item_id_getter=lambda bot: bot.id,
                items="bots",
                type_factory=BotId,
                on_click=process_select_bot,
            ),
        ),
        Start(
            Const("➕ Добавить бота"),
            id="add.bot",
            state=AddBotSG.GET_TOKEN,
        ),
        state=BotsListSG.LIST,
        getter=manager_bots_getter,
    ),
    launch_mode=LaunchMode.ROOT,
)
