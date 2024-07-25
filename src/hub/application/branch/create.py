from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BranchSaver, Committer
from hub.domain.models.branch import Branch, BranchAddress, BranchId, BranchName
from hub.domain.models.city import CityId


@dataclass
class CreateBranchDTO:
    city_id: CityId
    name: BranchName
    address: BranchAddress


class CreateBranchDbGateway(Committer, BranchSaver, Protocol):
    pass


class CreateBranch(Interactor[CreateBranchDTO, BranchId]):
    def __init__(self, db_gateway: CreateBranchDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: CreateBranchDTO) -> BranchId:
        branch = Branch(
            id=None,
            name=data.name,
            address=data.address,
            city_id=data.city_id,
        )
        branch_id = await self.db_gateway.save_branch(branch)
        await self.db_gateway.commit()
        return branch_id
