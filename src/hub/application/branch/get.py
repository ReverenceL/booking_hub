from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BranchReader
from hub.domain.models.branch import Branch, BranchId


@dataclass
class GetBranchDTO:
    branch_id: BranchId


class GetBranchDbGateway(BranchReader, Protocol):
    pass


class GetBranch(Interactor[GetBranchDTO, Branch]):
    def __init__(self, db_gateway: GetBranchDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetBranchDTO) -> Branch:
        return await self.db_gateway.get_branch(data.branch_id)
