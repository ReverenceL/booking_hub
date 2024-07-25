from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BranchSaver, Committer
from hub.domain.models.branch import BranchId


@dataclass
class DeleteBranchDTO:
    branch_id: BranchId


class DeleteBranchDbGateway(Committer, BranchSaver, Protocol):
    pass


class DeleteBranch(Interactor[DeleteBranchDTO, None]):
    def __init__(self, db_gateway: DeleteBranchDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: DeleteBranchDTO) -> None:
        await self.db_gateway.delete_branch(data.branch_id)
        await self.db_gateway.commit()
