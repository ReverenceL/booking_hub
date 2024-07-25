from dataclasses import dataclass
from typing import Protocol

from hub.application.common.exceptions import InsufficientDataError
from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BotReader
from hub.domain.models.bot import BotId, BotTelegramId
from hub.domain.models.city import City


@dataclass
class GetBotCitiesDTO:
    bot_id: BotId | None = None
    bot_telegram_id: BotTelegramId | None = None


class GetBotCitiesDbGateway(BotReader, Protocol):
    pass


class GetBotCities(Interactor[GetBotCitiesDTO, list[City]]):
    def __init__(self, db_gateway: GetBotCitiesDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetBotCitiesDTO) -> list[City]:
        if data.bot_id is not None:
            return await self.db_gateway.get_bot_cities(data.bot_id)
        elif data.bot_telegram_id is not None:
            bot = await self.db_gateway.get_bot_by_telegram_id(data.bot_telegram_id)
            return await self.db_gateway.get_bot_cities(bot.id)
        else:
            raise InsufficientDataError
