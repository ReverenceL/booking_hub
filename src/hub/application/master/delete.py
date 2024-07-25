from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, MasterSaver
from hub.domain.models.master import MasterId


@dataclass
class DeleteMasterDTO:
    master_id: MasterId


class DeleteMasterDbGateway(Committer, MasterSaver, Protocol):
    pass


class DeleteMaster(Interactor[DeleteMasterDTO, None]):
    def __init__(self, db_gateway: DeleteMasterDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: DeleteMasterDTO) -> None:
        await self.db_gateway.delete_master(data.master_id)
        await self.db_gateway.commit()
