from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.city import City, CityId
from ..common.exceptions import InsufficientDataError
from ..common.interactor import Interactor
from ..common.interfaces import CityReader


@dataclass
class GetCityDTO:
    city_id: CityId


class GetCityDbGateway(CityReader, Protocol):
    pass


class GetCity(Interactor[GetCityDTO, City]):
    def __init__(self, db_gateway: GetCityDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetCityDTO) -> City:
        if data.city_id:
            return await self.db_gateway.get_city(data.city_id)
        else:
            raise InsufficientDataError
