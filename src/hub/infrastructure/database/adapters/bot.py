from sqlalchemy import select

from hub.application.bot.exceptions import BotIdNotExistsError, BotTelegramIdNotExistsError, BotTokenNotExistsError
from hub.application.common.interfaces import BotReader, BotSaver
from hub.domain.models.bot import Bot, BotId, BotTelegramId, BotToken
from hub.domain.models.branch import Branch
from hub.domain.models.city import City
from hub.domain.models.manager import ManagerId
from hub.domain.models.master import Master
from hub.domain.models.service import Service
from ..converters import (
    bot_converter,
    branch_converter,
    city_converter,
    master_converter,
    service_converter,
)
from ..models import BotModel, BranchModel, CityModel, MasterModel, ServiceModel
from .base import BaseDbGateway, CommiterImpl


class BotDbGateway(BaseDbGateway, CommiterImpl, BotReader, BotSaver):
    async def get_bot(self, bot_id: BotId) -> Bot:
        bot = await self._session.get(BotModel, bot_id)
        if bot is None:
            raise BotIdNotExistsError
        return bot_converter(bot)

    async def get_bot_by_token(self, bot_token: BotToken) -> Bot:
        bot = await self._session.scalar(select(BotModel).where(BotModel.token == bot_token))
        if bot is None:
            raise BotTokenNotExistsError
        return bot_converter(bot)

    async def get_bot_by_telegram_id(self, telegram_id: BotTelegramId) -> Bot:
        bot = await self._session.scalar(select(BotModel).where(BotModel.telegram_id == telegram_id))
        if bot is None:
            raise BotTelegramIdNotExistsError
        return bot_converter(bot)

    async def get_bots_by_manager_id(self, manager_id: ManagerId) -> list[Bot]:
        scalar_bots = await self._session.scalars(select(BotModel).where(BotModel.manager_id == manager_id))
        return [bot_converter(bot) for bot in scalar_bots]

    async def get_bot_cities(self, bot_id: BotId) -> list[City]:
        scalar_cities = await self._session.scalars(select(CityModel).where(CityModel.bot_id == bot_id))
        return [city_converter(city) for city in scalar_cities]

    async def get_bot_services(self, bot_id: BotId) -> list[Service]:
        scalar_services = await self._session.scalars(select(ServiceModel).where(ServiceModel.bot_id == bot_id))
        return [service_converter(service) for service in scalar_services]

    async def get_bot_branches(self, bot_id: BotId) -> list[Branch]:
        scalar_branches = await self._session.scalars(
            select(BranchModel).join(CityModel).join(BotModel).where(BotModel.id == bot_id),
        )
        return [branch_converter(branch) for branch in scalar_branches]

    async def get_bot_masters(self, bot_id: BotId) -> list[Master]:
        scalar_masters = await self._session.scalars(select(MasterModel).where(MasterModel.bot_id == bot_id))
        return [master_converter(master) for master in scalar_masters]

    async def save_bot(self, bot: Bot) -> BotId:
        bot_model = BotModel()
        bot_model.token = bot.token
        bot_model.telegram_id = bot.telegram_id
        bot_model.name = bot.name
        bot_model.manager_id = bot.manager_id
        self._session.add(bot_model)
        await self._session.flush()
        return bot_model.id
