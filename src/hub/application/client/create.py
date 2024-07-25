from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.bot import BotTelegramId
from hub.domain.models.city import CityId
from hub.domain.models.client import Client, ClientId, ClientName, ClientTelegramId
from ..bot.get import GetBotDbGateway
from ..common.interactor import Interactor
from ..common.interfaces import ClientReader, ClientSaver, Committer
from .exceptions import ClientAlreadyExistsError, ClientTelegramIdNotExistsError


@dataclass(slots=True)
class CreateClientDTO:
    name: ClientName
    telegram_id: ClientTelegramId
    bot_telegram_id: BotTelegramId
    city_id: CityId


class CreateClientDbGateway(Committer, ClientReader, ClientSaver, Protocol):
    pass


class CreateClient(Interactor[CreateClientDTO, ClientId]):
    def __init__(self, db_gateway: CreateClientDbGateway, bot_db_gateway: GetBotDbGateway):
        self.db_gateway = db_gateway
        self.bot_db_gateway = bot_db_gateway

    async def __call__(self, data: CreateClientDTO) -> ClientId:
        bot = await self.bot_db_gateway.get_bot_by_telegram_id(data.bot_telegram_id)
        try:
            await self.db_gateway.get_client_by_telegram_id(
                bot_id=bot.id,
                telegram_id=data.telegram_id,
            )
            raise ClientAlreadyExistsError
        except ClientTelegramIdNotExistsError:
            pass
        client_id = await self.db_gateway.save_client(
            client=Client(
                id=None,
                telegram_id=data.telegram_id,
                name=data.name,
                bot_id=bot.id,
                city_id=data.city_id,
            ),
        )
        await self.db_gateway.commit()
        return client_id
