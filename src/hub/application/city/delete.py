from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import CitySaver, Committer
from hub.domain.models.city import CityId


@dataclass
class DeleteCityDTO:
    city_id: CityId


class DeleteCityDbGateway(Committer, CitySaver, Protocol):
    pass


class DeleteCity(Interactor[DeleteCityDTO, None]):
    def __init__(self, db_gateway: DeleteCityDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: DeleteCityDTO) -> None:
        await self.db_gateway.delete_city(data.city_id)
        await self.db_gateway.commit()
