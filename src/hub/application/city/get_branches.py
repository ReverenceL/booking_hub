from collections.abc import Iterable
from dataclasses import dataclass
from typing import Protocol

from hub.domain.models.branch import Branch
from hub.domain.models.city import CityId
from ..common.interactor import Interactor
from ..common.interfaces import CityReader


@dataclass
class GetCityBranchesDTO:
    city_id: CityId


class GetCityBranchesDbGateway(CityReader, Protocol):
    pass


class GetCityBranches(Interactor[GetCityBranchesDTO, Iterable[Branch]]):
    def __init__(self, db_gateway: GetCityBranchesDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetCityBranchesDTO) -> Iterable[Branch]:
        return await self.db_gateway.get_branches(data.city_id)
