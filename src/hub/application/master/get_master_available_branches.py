from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import MasterReader
from hub.domain.models.bot import BotId
from hub.domain.models.branch import Branch
from hub.domain.models.master import MasterId


@dataclass
class GetMasterAvailableBranchesDTO:
    bot_id: BotId
    master_id: MasterId


class GetMasterAvailableBranchesDbGateway(MasterReader, Protocol):
    pass


class GetMasterAvailableBranches(Interactor[GetMasterAvailableBranchesDTO, tuple[tuple[bool, Branch], ...]]):
    def __init__(self, db_gateway: GetMasterAvailableBranchesDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetMasterAvailableBranchesDTO) -> tuple[tuple[bool, Branch], ...]:
        return await self.db_gateway.get_available_branches(data.bot_id, data.master_id)
