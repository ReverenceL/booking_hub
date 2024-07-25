from sqlalchemy import select

from hub.application.common.interfaces import ManagerReader, ManagerSaver
from hub.application.manager.exceptions import ManagerIdNotExistsError, ManagerTelegramIdNotExistsError
from hub.domain.models.bot import Bot
from hub.domain.models.manager import Manager, ManagerId, ManagerTelegramId
from hub.infrastructure.database.adapters.base import BaseDbGateway, CommiterImpl
from hub.infrastructure.database.converters import bot_converter, manager_converter
from hub.infrastructure.database.models import BotModel, ManagerModel


class ManagerDbGateway(BaseDbGateway, CommiterImpl, ManagerReader, ManagerSaver):
    async def get_manager(self, manager_id: ManagerId) -> Manager:
        manager = await self._session.get(ManagerModel, manager_id)
        if manager is None:
            raise ManagerIdNotExistsError
        return manager_converter(manager)

    async def get_manager_by_telegram_id(self, telegram_id: ManagerTelegramId) -> Manager:
        manager = await self._session.scalar(
            select(ManagerModel).where(ManagerModel.telegram_id == telegram_id),
        )
        if manager is None:
            raise ManagerTelegramIdNotExistsError
        return manager_converter(manager)

    async def get_manager_bots(self, manager_id: ManagerId) -> list[Bot]:
        bots = await self._session.scalars(
            select(BotModel).where(BotModel.manager_id == manager_id),
        )
        return [bot_converter(bot) for bot in bots]

    async def save_manager(self, manager: Manager) -> ManagerId:
        manager_model = ManagerModel()
        manager_model.telegram_id = manager.telegram_id

        self._session.add(manager_model)
        await self._session.flush()
        return manager_model.id
