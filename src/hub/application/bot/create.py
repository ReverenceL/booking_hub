from dataclasses import dataclass
from typing import Protocol

from aiogram import Bot as AiogramBot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.exceptions import TelegramUnauthorizedError
from aiogram.utils.token import TokenValidationError

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BotReader, BotSaver, Committer
from hub.domain.models.bot import Bot, BotId, BotToken
from hub.domain.models.manager import ManagerId
from hub.infrastructure.webhook_url import MultibotWebhookUrl
from .exceptions import BotAlreadyExistsError, BotTokenNotExistsError, InvalidBotTokenError


@dataclass
class NewBotDTO:
    token: BotToken
    manager_id: ManagerId


class CreateBotDbGateway(
    Committer,
    BotReader,
    BotSaver,
    Protocol,
):
    pass


class CreateBot(Interactor[NewBotDTO, BotId]):
    def __init__(
        self,
        db_gateway: CreateBotDbGateway,
        multibot_webhook_url: MultibotWebhookUrl,
    ):
        self.db_gateway = db_gateway
        self.multibot_webhook_url = multibot_webhook_url

    async def __call__(self, data: NewBotDTO) -> BotId:
        try:
            await self.db_gateway.get_bot_by_token(data.token)
            raise BotAlreadyExistsError
        except BotTokenNotExistsError:
            pass
        session = AiohttpSession()
        aiogram_bot = AiogramBot(data.token, session=session)
        try:
            aiogram_bot_data = await aiogram_bot.get_me()
        except (TokenValidationError, TelegramUnauthorizedError) as err:
            raise InvalidBotTokenError from err
        else:
            await aiogram_bot.delete_webhook(drop_pending_updates=True)
            webhook_url = self.multibot_webhook_url.format(bot_token=data.token)
            await aiogram_bot.set_webhook(webhook_url)
        finally:
            await session.close()
        bot_id = await self.db_gateway.save_bot(
            Bot(
                id=None,
                token=data.token,
                telegram_id=aiogram_bot_data.id,
                manager_id=data.manager_id,
                name=aiogram_bot_data.full_name,
            ),
        )
        await self.db_gateway.commit()
        return bot_id
