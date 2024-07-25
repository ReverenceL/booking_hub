from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.bot import Bot
from hub.domain.models.manager import ManagerId, ManagerTelegramId
from ..common.exceptions import InsufficientDataError
from ..common.interactor import Interactor
from ..common.interfaces import ManagerReader


@dataclass
class GetManagerBotsDTO:
    manager_id: ManagerId | None = None
    telegram_id: ManagerTelegramId | None = None


class GetManagerBotsDbGateway(ManagerReader, Protocol):
    pass


class GetManagerBots(Interactor[GetManagerBotsDTO, list[Bot]]):
    def __init__(self, db_gateway: GetManagerBotsDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetManagerBotsDTO) -> list[Bot]:
        if data.manager_id:
            return await self.db_gateway.get_manager_bots(data.manager_id)
        elif data.telegram_id:
            manager = await self.db_gateway.get_manager_by_telegram_id(data.telegram_id)
            return await self.db_gateway.get_manager_bots(manager.id)
        else:
            raise InsufficientDataError
