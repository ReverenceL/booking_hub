from contextlib import suppress

from aiogram import Router
from aiogram.filters import CommandStart
from aiogram.types import Message
from aiogram_dialog import DialogManager
from dishka import FromDishka

from hub.application.manager.create import CreateManager, CreateManagerDTO, ManagerAlreadyExistsError
from hub.domain.models.manager import ManagerTelegramId
from hub.presentation.admin_bot.state_groups.main import BotsListSG

router = Router()


@router.message(CommandStart())
async def process_start(
    message: Message,
    dialog_manager: DialogManager,
    create_manager: FromDishka[CreateManager],
) -> None:
    if message.from_user is None:
        raise ValueError("User cannot be None")
    with suppress(ManagerAlreadyExistsError):
        await create_manager(
            CreateManagerDTO(
                telegram_id=ManagerTelegramId(message.from_user.id),
            ),
        )

    await dialog_manager.start(state=BotsListSG.LIST)
