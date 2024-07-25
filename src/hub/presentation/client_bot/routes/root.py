from typing import Any

from aiogram import Router, Bot
from aiogram.filters import CommandStart
from aiogram.types import InputMedia, InputMediaPhoto, FSInputFile
from aiogram_dialog import DialogManager

from hub.presentation.client_bot.state_groups.main_menu import RegistrationSG

router = Router()


async def show_main_menu(bot: Bot, chat_id: int) -> None:
    await bot.send_photo(
        chat_id=chat_id,
        photo=InputMediaPhoto(
            media=FSInputFile(path="./resources/media/main_bot/stub.png"),
        ),
        caption=
    )


@router.message(CommandStart())
async def process_start(_: Any, dialog_manager: DialogManager) -> None:
    await dialog_manager.start(RegistrationSG.GET_CITY)
