from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import MasterReader
from hub.domain.models.master import Master, MasterId


@dataclass
class GetMasterDTO:
    master_id: MasterId


class GetMasterDbGateway(MasterReader, Protocol):
    pass


class GetMaster(Interactor[GetMasterDTO, Master]):
    def __init__(self, db_gateway: GetMasterDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetMasterDTO) -> Master:
        return await self.db_gateway.get_master(data.master_id)
