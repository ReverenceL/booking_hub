from typing import Any

from aiogram_dialog import Dialog, DialogManager, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Cancel
from aiogram_dialog.widgets.text import Const, Format, Multi
from dishka import FromDishka

from hub.application.bot.create import CreateBot, NewBotDTO
from hub.application.bot.exceptions import BotAlreadyExistsError, InvalidBotTokenError
from hub.application.bot.get import GetBot, GetBotDTO
from hub.application.manager.get import GetManager, GetManagerDTO
from hub.domain.models.bot import BotToken
from hub.domain.models.manager import ManagerId
from hub.infrastructure.di.injectors import inject_handler
from hub.presentation.admin_bot.state_groups.main import AddBotSG


@inject_handler
async def process_new_bot_token(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    token: BotToken,
    get_manager: FromDishka[GetManager],
    create_bot: FromDishka[CreateBot],
    get_bot: FromDishka[GetBot],
) -> None:
    if dialog_manager.event.from_user is None:
        raise ValueError("User cannot be None")
    manager = await get_manager(GetManagerDTO(telegram_id=dialog_manager.event.from_user.id))
    try:
        bot_id = await create_bot(
            NewBotDTO(
                token=BotToken(token),
                manager_id=ManagerId(manager.id),
            ),
        )
        bot = await get_bot(GetBotDTO(bot_id=bot_id))
    except BotAlreadyExistsError:
        await dialog_manager.switch_to(state=AddBotSG.ALREADY_EXISTS)
    except InvalidBotTokenError:
        await dialog_manager.switch_to(state=AddBotSG.INVALID_TOKEN)
    else:
        dialog_manager.dialog_data["bot_name"] = bot.name
        await dialog_manager.switch_to(state=AddBotSG.SUCCESS)


add_bot_dialog = Dialog(
    Window(
        Const("💡 Отправьте токен нового бота:"),
        TextInput(
            id="get.new.bot.token",
            on_success=process_new_bot_token,
        ),
        Cancel(Const("✖️ Закрыть")),
        state=AddBotSG.GET_TOKEN,
    ),
    Window(
        Multi(
            Const("⚠️ Вы отправили недействительный токен."),
            Const("💡 Отправьте токен нового бота:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.new.bot.token",
            on_success=process_new_bot_token,
        ),
        Cancel(Const("✖️ Закрыть")),
        state=AddBotSG.INVALID_TOKEN,
    ),
    Window(
        Const("⚠️ Такой бот уже существует."),
        Cancel(Const("✖️ Закрыть")),
        state=AddBotSG.ALREADY_EXISTS,
    ),
    Window(
        Format("✔️ Бот «{dialog_data[bot_name]}» успешно добавлен."),
        Cancel(Const("✖️ Закрыть")),
        state=AddBotSG.SUCCESS,
    ),
)
