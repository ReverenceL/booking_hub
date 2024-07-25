from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import CitySaver, Committer
from hub.domain.models.city import CityId, CityName
from hub.domain.models.timezone import TimeZone


@dataclass
class CityUpdateDTO:
    city_id: CityId
    name: CityName | None = None
    timezone: TimeZone | None = None


class CityUpdateDbGateway(Committer, CitySaver, Protocol):
    pass


class CityUpdate(Interactor[CityUpdateDTO, None]):
    def __init__(self, db_gateway: CityUpdateDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: CityUpdateDTO) -> None:
        if data.name:
            await self.db_gateway.update_city_name(data.city_id, data.name)
        if data.timezone:
            await self.db_gateway.update_city_timezone(data.city_id, data.timezone)
        await self.db_gateway.commit()
