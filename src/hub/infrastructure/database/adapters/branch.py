from sqlalchemy import delete, update

from hub.application.branch.exceptions import BranchIdNotExistsError
from hub.application.common.interfaces import BranchReader, BranchSaver
from hub.domain.models.branch import Branch, BranchAddress, BranchId, BranchName
from hub.infrastructure.database.adapters.base import BaseDbGateway, CommiterImpl
from hub.infrastructure.database.converters import branch_converter
from hub.infrastructure.database.models import BranchModel


class BranchDbGateway(BaseDbGateway, CommiterImpl, BranchReader, BranchSaver):
    async def save_branch(self, branch: Branch) -> BranchId:
        branch_model = BranchModel()
        branch_model.name = branch.name
        branch_model.address = branch.address
        branch_model.city_id = branch.city_id
        self._session.add(branch_model)
        await self._session.flush()
        return branch_model.id

    async def get_branch(self, branch_id: BranchId) -> Branch:
        branch = await self._session.get(BranchModel, branch_id)
        if branch is None:
            raise BranchIdNotExistsError
        return branch_converter(branch)

    async def update_branch_name(self, branch_id: BranchId, name: BranchName) -> None:
        await self._session.execute(
            update(BranchModel).where(BranchModel.id == branch_id).values(name=name),
        )

    async def update_branch_address(self, branch_id: BranchId, address: BranchAddress) -> None:
        await self._session.execute(
            update(BranchModel).where(BranchModel.id == branch_id).values(address=address),
        )

    async def delete_branch(self, branch_id: BranchId) -> None:
        await self._session.execute(
            delete(BranchModel).where(BranchModel.id == branch_id),
        )
