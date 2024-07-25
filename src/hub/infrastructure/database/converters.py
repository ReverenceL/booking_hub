from adaptix import Retort
from adaptix.conversion import get_converter

from hub.domain.models.bot import Bot
from hub.domain.models.branch import Branch
from hub.domain.models.city import City
from hub.domain.models.client import Client
from hub.domain.models.manager import Manager
from hub.domain.models.master import Master
from hub.domain.models.service import Service
from hub.domain.new_type import NewTypeUnwrappingProvider
from hub.infrastructure.database.models import (
    BotModel,
    BranchModel,
    CityModel,
    ClientModel,
    ManagerModel,
    MasterModel,
    ServiceModel,
)

retort = Retort(recipe=[NewTypeUnwrappingProvider()])

bot_converter = get_converter(BotModel, Bot)
branch_converter = get_converter(BranchModel, Branch)
city_converter = get_converter(CityModel, City)
client_converter = get_converter(ClientModel, Client)
manager_converter = get_converter(ManagerModel, Manager)
master_converter = get_converter(MasterModel, Master)
service_converter = get_converter(ServiceModel, Service)
