from sqlalchemy import select

from hub.application.client.exceptions import ClientIdNotExistsError, ClientTelegramIdNotExistsError
from hub.application.common.interfaces import ClientReader, ClientSaver
from hub.domain.models.bot import BotId
from hub.domain.models.client import Client, ClientId, ClientTelegramId
from ..converters import client_converter
from ..models import CityModel, ClientModel
from .base import BaseDbGateway, CommiterImpl


class ClientDbGateway(BaseDbGateway, CommiterImpl, ClientReader, ClientSaver):
    async def get_client(self, client_id: ClientId) -> Client:
        client = await self._session.get(CityModel, client_id)
        if client is None:
            raise ClientIdNotExistsError
        return client_converter(client)

    async def get_client_by_telegram_id(self, bot_id: BotId, telegram_id: ClientTelegramId) -> Client:
        client = await self._session.scalar(
            select(ClientModel).where(
                ClientModel.bot_id == bot_id,
                ClientModel.telegram_id == telegram_id,
            ),
        )
        if client is None:
            raise ClientTelegramIdNotExistsError
        return client_converter(client)

    async def save_client(self, client: Client) -> ClientId:
        client_model = ClientModel()
        client_model.bot_id = client.bot_id
        client_model.telegram_id = client.telegram_id
        client_model.name = client.name
        client_model.city_id = client.city_id

        self._session.add(client_model)
        await self._session.flush()
        return client_model.id
