from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.bot import Bot, BotId, BotTelegramId, BotToken
from ..common.exceptions import InsufficientDataError
from ..common.interactor import Interactor
from ..common.interfaces import BotReader


@dataclass
class GetBotDTO:
    bot_id: BotId | None = None
    token: BotToken | None = None
    telegram_id: BotTelegramId | None = None


class GetBotDbGateway(BotReader, Protocol):
    pass


class GetBot(Interactor[GetBotDTO, Bot]):
    def __init__(self, db_gateway: GetBotDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetBotDTO) -> Bot:
        if data.bot_id:
            return await self.db_gateway.get_bot(data.bot_id)
        elif data.token:
            return await self.db_gateway.get_bot_by_token(data.token)
        elif data.telegram_id:
            return await self.db_gateway.get_bot_by_telegram_id(data.telegram_id)
        else:
            raise InsufficientDataError
