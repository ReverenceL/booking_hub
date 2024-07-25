from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BranchSaver, Committer
from hub.domain.models.branch import BranchAddress, BranchId, BranchName


@dataclass
class UpdateBranchDTO:
    branch_id: BranchId
    name: BranchName | None = None
    address: BranchAddress | None = None


class UpdateBranchDbGateway(Committer, BranchSaver, Protocol):
    pass


class UpdateBranch(Interactor[UpdateBranchDTO, None]):
    def __init__(self, db_gateway: UpdateBranchDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: UpdateBranchDTO) -> None:
        if data.name:
            await self.db_gateway.update_branch_name(data.branch_id, data.name)
        if data.address:
            await self.db_gateway.update_branch_address(data.branch_id, data.address)
        await self.db_gateway.commit()
