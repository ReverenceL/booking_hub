from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.bot import BotId
from hub.domain.models.client import Client, ClientId, ClientTelegramId
from ..common.exceptions import InsufficientDataError
from ..common.interactor import Interactor
from ..common.interfaces import ClientReader


@dataclass
class GetClientDTO:
    client_id: ClientId | None = None
    telegram_id: ClientTelegramId | None = None
    bot_id: BotId | None = None


class GetClientDbGateway(ClientReader, Protocol):
    pass


class GetClient(Interactor[GetClientDTO, Client]):
    def __init__(self, db_gateway: GetClientDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetClientDTO) -> Client:
        if data.client_id:
            return await self.db_gateway.get_client(data.client_id)
        elif data.telegram_id and data.bot_id:
            return await self.db_gateway.get_client_by_telegram_id(
                bot_id=data.bot_id,
                telegram_id=data.telegram_id,
            )
        else:
            raise InsufficientDataError
