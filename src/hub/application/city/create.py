from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.bot import BotId
from hub.domain.models.city import City, CityId, CityName
from ...domain.models.timezone import TimeZone
from ..common.interactor import Interactor
from ..common.interfaces import CitySaver, Committer


@dataclass
class CreateCityDTO:
    bot_id: BotId
    name: CityName
    timezone: TimeZone


class CreateCityDbGateway(Committer, CitySaver, Protocol):
    pass


class CreateCity(Interactor[CreateCityDTO, CityId]):
    def __init__(self, db_gateway: CreateCityDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: CreateCityDTO) -> CityId:
        city = City(
            id=None,
            name=data.name,
            timezone=data.timezone,
            bot_id=data.bot_id,
        )
        await self.db_gateway.save_city(city=city)
        await self.db_gateway.commit()
        return city.id
