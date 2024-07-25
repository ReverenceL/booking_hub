from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.manager import Manager, ManagerId, ManagerTelegramId
from ..common.exceptions import InsufficientDataError
from ..common.interactor import Interactor
from ..common.interfaces import ManagerReader


@dataclass
class GetManagerDTO:
    manager_id: ManagerId | None = None
    telegram_id: ManagerTelegramId | None = None


class GetManagerDbGateway(ManagerReader, Protocol):
    pass


class GetManager(Interactor[GetManagerDTO, Manager]):
    def __init__(
        self,
        db_gateway: GetManagerDbGateway,
    ):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetManagerDTO) -> Manager:
        if data.manager_id:
            return await self.db_gateway.get_manager(data.manager_id)
        elif data.telegram_id:
            return await self.db_gateway.get_manager_by_telegram_id(data.telegram_id)
        else:
            raise InsufficientDataError
