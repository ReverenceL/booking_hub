from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, MasterReader, MasterSaver
from hub.domain.models.branch import Branch
from hub.domain.models.master import MasterId
from hub.domain.models.service import Service


@dataclass
class UpdateServiceTimeDTO:
    service: Service
    work_time: int | None = None
    break_time: int | None = None


@dataclass
class UpdateMasterDTO:
    master_id: MasterId
    name: str | None = None
    branch: Branch | None = None
    service: Service | None = None
    service_time: UpdateServiceTimeDTO | None = None


class UpdateMasterDbGateway(Committer, MasterReader, MasterSaver, Protocol):
    pass


class UpdateMaster(Interactor[UpdateMasterDTO, None]):
    def __init__(self, db_gateway: UpdateMasterDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: UpdateMasterDTO) -> None:
        if data.name:
            await self.db_gateway.update_master_name(data.master_id, data.name)
        if data.branch:
            attached = await self.db_gateway.check_master_attached_to_branch(data.master_id, data.branch.id)
            if attached:
                await self.db_gateway.detach_master_from_branch(data.master_id, data.branch.id)
            else:
                await self.db_gateway.attach_master_to_branch(data.master_id, data.branch.id)
        if data.service:
            provides = await self.db_gateway.check_master_provides_service(data.master_id, data.service.id)
            if provides:
                await self.db_gateway.master_withhold_service(data.master_id, data.service.id)
            else:
                await self.db_gateway.master_provide_service(data.master_id, data.service.id)
        if data.service_time:
            if data.service_time.work_time:
                await self.db_gateway.update_master_work_time(
                    master_id=data.master_id,
                    service_id=data.service_time.service.id,
                    work_time=data.service_time.work_time,
                )
            if data.service_time.break_time:
                await self.db_gateway.update_master_break_time(
                    master_id=data.master_id,
                    service_id=data.service_time.service.id,
                    break_time=data.service_time.break_time,
                )

        await self.db_gateway.commit()
