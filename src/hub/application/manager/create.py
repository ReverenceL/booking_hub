from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.manager import Manager, ManagerId, ManagerTelegramId
from ..common.exceptions import ApplicationError
from ..common.interactor import Interactor
from ..common.interfaces import Committer, ManagerReader, ManagerSaver
from .exceptions import ManagerTelegramIdNotExistsError


@dataclass
class CreateManagerDTO:
    telegram_id: ManagerTelegramId


class CreateManagerDbGateway(Committer, ManagerReader, ManagerSaver, Protocol):
    pass


class ManagerAlreadyExistsError(ApplicationError):
    pass


class CreateManager(Interactor[CreateManagerDTO, ManagerId]):
    def __init__(
        self,
        db_gateway: CreateManagerDbGateway,
    ):
        self.db_gateway = db_gateway

    async def __call__(self, data: CreateManagerDTO) -> ManagerId:
        try:
            await self.db_gateway.get_manager_by_telegram_id(data.telegram_id)
            raise ManagerAlreadyExistsError
        except ManagerTelegramIdNotExistsError:
            pass
        manager = Manager(
            id=None,
            telegram_id=data.telegram_id,
        )
        await self.db_gateway.save_manager(manager)
        await self.db_gateway.commit()
        return manager.id
