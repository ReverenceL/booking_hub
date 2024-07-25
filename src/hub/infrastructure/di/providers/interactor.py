from dishka import Provider, Scope, provide

from hub.application.bot.create import CreateBot
from hub.application.bot.get import GetBot
from hub.application.bot.get_branches import GetBotBranches
from hub.application.bot.get_cities import GetBotCities
from hub.application.bot.get_masters import GetBotMasters
from hub.application.bot.get_services import GetBotServices
from hub.application.branch.create import CreateBranch
from hub.application.branch.delete import DeleteBranch
from hub.application.branch.get import GetBranch
from hub.application.branch.update import UpdateBranch
from hub.application.city.create import CreateCity
from hub.application.city.delete import DeleteCity
from hub.application.city.get import GetCity
from hub.application.city.update import CityUpdate
from hub.application.client.create import CreateClient
from hub.application.client.get import GetClient
from hub.application.manager.create import CreateManager
from hub.application.manager.get import GetManager
from hub.application.manager.get_bots import GetManagerBots
from hub.application.master.create import CreateMaster
from hub.application.master.delete import DeleteMaster
from hub.application.master.get import GetMaster
from hub.application.master.get_master_available_branches import GetMasterAvailableBranches
from hub.application.master.get_master_available_services import GetMasterAvailableServices
from hub.application.master.update import UpdateMaster
from hub.application.service.create import CreateService
from hub.application.service.delete import DeleteService
from hub.application.service.get import GetService
from hub.application.service.update import ServiceUpdate


class MainBotInteractorProvider(Provider):
    scope = Scope.REQUEST

    # Bot providers
    create_bot = provide(CreateBot)
    get_bot = provide(GetBot)
    get_bot_cities = provide(GetBotCities)
    get_bot_services = provide(GetBotServices)
    get_bot_branches = provide(GetBotBranches)
    get_bot_masters = provide(GetBotMasters)

    # Manager providers
    create_manager = provide(CreateManager)
    get_manager = provide(GetManager)
    get_manager_bots = provide(GetManagerBots)

    # City provider
    create_city = provide(CreateCity)
    get_city = provide(GetCity)
    delete_city = provide(DeleteCity)
    update_city = provide(CityUpdate)

    # Branch provider
    create_branch = provide(CreateBranch)
    get_branch = provide(GetBranch)
    update_branch = provide(UpdateBranch)
    delete_branch = provide(DeleteBranch)

    # Master provider
    create_master = provide(CreateMaster)
    get_master = provide(GetMaster)
    update_master = provide(UpdateMaster)
    delete_master = provide(DeleteMaster)
    get_available_branches = provide(GetMasterAvailableBranches)
    get_available_services = provide(GetMasterAvailableServices)

    # Service provider
    create_service = provide(CreateService)
    update_service = provide(ServiceUpdate)
    get_service = provide(GetService)
    delete_service = provide(DeleteService)


class ClientBotInteractorProvider(Provider):
    scope = Scope.REQUEST

    # Bot providers
    get_bot = provide(GetBot)
    get_bot_cities = provide(GetBotCities)
    get_bot_services = provide(GetBotServices)
    get_bot_branches = provide(GetBotBranches)
    get_bot_masters = provide(GetBotMasters)

    # Client providers
    create_client = provide(CreateClient)
    get_client = provide(GetClient)

    # City provider
    get_city = provide(GetCity)

    # Service provider
    get_service = provide(GetService)
