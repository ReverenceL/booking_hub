from collections.abc import AsyncIterable

from dishka import AnyOf, Provider, Scope, provide
from sqlalchemy.ext.asyncio import (
    AsyncEngine,
    AsyncSession,
    async_sessionmaker,
    create_async_engine,
)

from hub.application.bot.create import CreateBotDbGateway
from hub.application.bot.get import GetBotDbGateway
from hub.application.bot.get_branches import GetBotBranchesDbGateway
from hub.application.bot.get_cities import GetBotCitiesDbGateway
from hub.application.bot.get_masters import GetBotMastersDbGateway
from hub.application.bot.get_services import GetBotServicesDbGateway
from hub.application.branch.create import CreateBranchDbGateway
from hub.application.branch.delete import DeleteBranchDbGateway
from hub.application.branch.get import GetBranchDbGateway
from hub.application.branch.update import UpdateBranchDbGateway
from hub.application.city.create import CreateCityDbGateway
from hub.application.city.delete import DeleteCityDbGateway
from hub.application.city.get import GetCityDbGateway
from hub.application.city.update import CityUpdateDbGateway
from hub.application.client.create import CreateClientDbGateway
from hub.application.client.get import GetClientDbGateway
from hub.application.manager.create import CreateManagerDbGateway
from hub.application.manager.get import GetManagerDbGateway
from hub.application.manager.get_bots import GetManagerBotsDbGateway
from hub.application.master.create import CreateMasterDbGateway
from hub.application.master.delete import DeleteMasterDbGateway
from hub.application.master.get import GetMasterDbGateway
from hub.application.master.get_master_available_branches import GetMasterAvailableBranchesDbGateway
from hub.application.master.get_master_available_services import GetMasterAvailableServicesDbGateway
from hub.application.master.update import UpdateMasterDbGateway
from hub.application.service.create import CreateServiceDbGateway
from hub.application.service.delete import DeleteServiceDbGateway
from hub.application.service.get import GetServiceDbGateway
from hub.application.service.update import ServiceUpdateDbGateway
from hub.infrastructure.database.adapters.bot import BotDbGateway
from hub.infrastructure.database.adapters.branch import BranchDbGateway
from hub.infrastructure.database.adapters.city import CityDbGateway
from hub.infrastructure.database.adapters.client import ClientDbGateway
from hub.infrastructure.database.adapters.manager import ManagerDbGateway
from hub.infrastructure.database.adapters.master import MasterDbGateway
from hub.infrastructure.database.adapters.service import ServiceDbGateway
from hub.main.config import Config


class DatabaseProvider(Provider):
    scope = Scope.APP

    @provide
    async def get_engine(self, config: Config) -> AsyncIterable[AsyncEngine]:
        engine = create_async_engine(config.db.full_url)
        yield engine
        await engine.dispose(close=True)

    @provide
    async def get_sessionmaker(self, engine: AsyncEngine) -> async_sessionmaker[AsyncSession]:
        sessionmaker = async_sessionmaker(
            bind=engine,
            expire_on_commit=False,
            autoflush=False,
        )
        return sessionmaker

    @provide(scope=Scope.REQUEST)
    async def get_session(self, sessionmaker: async_sessionmaker[AsyncSession]) -> AsyncIterable[AsyncSession]:
        async with sessionmaker() as session:
            yield session


class MainBotGatewayProvider(Provider):
    scope = Scope.REQUEST

    bot = provide(
        BotDbGateway,
        provides=AnyOf[
            CreateBotDbGateway,
            GetBotDbGateway,
            GetBotCitiesDbGateway,
            GetBotServicesDbGateway,
            GetBotBranchesDbGateway,
            GetBotMastersDbGateway,
        ],
    )
    manager = provide(
        ManagerDbGateway,
        provides=AnyOf[
            GetManagerDbGateway,
            CreateManagerDbGateway,
            GetManagerBotsDbGateway,
        ],
    )
    city = provide(
        CityDbGateway,
        provides=AnyOf[
            CreateCityDbGateway,
            GetCityDbGateway,
            DeleteCityDbGateway,
            CityUpdateDbGateway,
        ],
    )
    branch = provide(
        BranchDbGateway,
        provides=AnyOf[
            CreateBranchDbGateway,
            GetBranchDbGateway,
            DeleteBranchDbGateway,
            UpdateBranchDbGateway,
        ],
    )
    master = provide(
        MasterDbGateway,
        provides=AnyOf[
            CreateMasterDbGateway,
            UpdateMasterDbGateway,
            DeleteMasterDbGateway,
            GetMasterDbGateway,
            GetMasterAvailableBranchesDbGateway,
            GetMasterAvailableServicesDbGateway,
        ],
    )
    service = provide(
        ServiceDbGateway,
        provides=AnyOf[
            CreateServiceDbGateway,
            ServiceUpdateDbGateway,
            GetServiceDbGateway,
            DeleteServiceDbGateway,
        ],
    )


class ClientBotGatewayProvider(Provider):
    scope = Scope.REQUEST

    bot = provide(
        BotDbGateway,
        provides=AnyOf[
            GetBotDbGateway,
            GetBotCitiesDbGateway,
            GetBotServicesDbGateway,
            GetBotBranchesDbGateway,
            GetBotMastersDbGateway,
        ],
    )
    client = provide(
        ClientDbGateway,
        provides=AnyOf[
            CreateClientDbGateway,
            GetClientDbGateway,
        ],
    )
    city = provide(
        CityDbGateway,
        provides=AnyOf[GetCityDbGateway,],
    )
    service = provide(
        ServiceDbGateway,
        provides=AnyOf[GetServiceDbGateway,],
    )
