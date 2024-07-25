from adaptix.conversion import convert
from sqlalchemy import delete, insert, literal, select, update

from hub.application.common.interfaces import MasterReader, MasterSaver
from hub.application.master.exceptions import MasterIdNotExistsError
from hub.domain.models.bot import BotId
from hub.domain.models.branch import AvailableBranch, BranchId
from hub.domain.models.master import Master, MasterId, MasterName
from hub.domain.models.service import AvailableService, ServiceId
from hub.infrastructure.database.adapters.base import BaseDbGateway, CommiterImpl
from hub.infrastructure.database.converters import master_converter
from hub.infrastructure.database.models import (
    BranchMasterAssociationModel,
    BranchModel,
    CityModel,
    MasterModel,
    ServiceMasterAssociationModel,
    ServiceModel,
)


class MasterDbGateway(BaseDbGateway, CommiterImpl, MasterReader, MasterSaver):
    async def save_master(self, master: Master) -> MasterId:
        master_model = MasterModel()
        master_model.name = master.name
        master_model.city_id = master.city_id
        master_model.bot_id = master.bot_id

        self._session.add(master_model)
        await self._session.flush()
        return master_model.id

    async def update_master_name(self, master_id: MasterId, name: MasterName) -> None:
        await self._session.execute(
            update(MasterModel).where(MasterModel.id == master_id).values(name=name),
        )

    async def attach_master_to_branch(self, master_id: MasterId, branch_id: BranchId) -> None:
        await self._session.execute(
            insert(BranchMasterAssociationModel).values(
                master_id=master_id,
                branch_id=branch_id,
            ),
        )

    async def detach_master_from_branch(self, master_id: MasterId, branch_id: BranchId) -> None:
        await self._session.execute(
            delete(BranchMasterAssociationModel).where(
                BranchMasterAssociationModel.master_id == master_id,
                BranchMasterAssociationModel.branch_id == branch_id,
            ),
        )

    async def master_provide_service(self, master_id: MasterId, service_id: ServiceId) -> None:
        await self._session.execute(
            insert(ServiceMasterAssociationModel).values(
                master_id=master_id,
                service_id=service_id,
            ),
        )

    async def master_withhold_service(self, master_id: MasterId, service_id: ServiceId) -> None:
        await self._session.execute(
            delete(ServiceMasterAssociationModel).where(
                ServiceMasterAssociationModel.master_id == master_id,
                ServiceMasterAssociationModel.service_id == service_id,
            ),
        )

    async def delete_master(self, master_id: MasterId) -> None:
        await self._session.execute(delete(MasterModel).where(MasterModel.id == master_id))

    async def get_master(self, master_id: MasterId) -> Master:
        master = await self._session.get(MasterModel, master_id)
        if master is None:
            raise MasterIdNotExistsError
        return master_converter(master)

    async def get_available_branches(self, bot_id: BotId, master_id: MasterId) -> list[AvailableBranch]:
        subquery = select(BranchModel.id).join(CityModel).where(CityModel.bot_id == bot_id)

        branches = await self._session.scalars(
            select(
                literal(value=True).label("is_associated"),
                BranchModel,
            )
            .join(BranchMasterAssociationModel, BranchModel.id == BranchMasterAssociationModel.branch_id)
            .filter(BranchMasterAssociationModel.master_id == master_id, BranchModel.id.in_(subquery))
            .union_all(
                select(
                    literal(value=False).label("is_associated"),
                    BranchModel,
                ).filter(BranchModel.id.in_(subquery), ~BranchModel.masters.any(MasterModel.id == master_id)),
            ),
        )
        return [convert(branch, AvailableBranch) for branch in branches]

    async def get_available_services(self, bot_id: BotId, master_id: MasterId) -> list[AvailableService]:
        subquery = select(ServiceModel.id).where(ServiceModel.bot_id == bot_id)

        services = await self._session.execute(
            select(
                literal(value=True).label("is_associated"),
                ServiceModel,
            )
            .join(
                ServiceMasterAssociationModel,
                ServiceModel.id == ServiceMasterAssociationModel.service_id,
            )
            .filter(ServiceMasterAssociationModel.master_id == master_id, ServiceModel.id.in_(subquery))
            .union_all(
                select(
                    literal(value=False).label("is_associated"),
                    ServiceModel,
                ).filter(
                    ServiceModel.id.in_(subquery),
                    ~ServiceModel.masters.any(MasterModel.id == master_id),
                ),
            ),
        )
        return [convert(service, AvailableService) for service in services]

    async def check_master_attached_to_branch(self, master_id: MasterId, branch_id: BranchId) -> bool:
        model = await self._session.scalar(
            select(BranchMasterAssociationModel).where(
                BranchMasterAssociationModel.master_id == master_id,
                BranchMasterAssociationModel.branch_id == branch_id,
            ),
        )
        return model is not None

    async def check_master_provides_service(self, master_id: MasterId, service_id: ServiceId) -> bool:
        model = await self._session.scalar(
            select(ServiceMasterAssociationModel).where(
                ServiceMasterAssociationModel.master_id == master_id,
                ServiceMasterAssociationModel.service_id == service_id,
            ),
        )
        return model is not None

    async def update_master_work_time(self, master_id: MasterId, service_id: ServiceId, work_time: int) -> None:
        await self._session.execute(
            update(ServiceMasterAssociationModel)
            .where(
                ServiceMasterAssociationModel.master_id == master_id,
                ServiceMasterAssociationModel.service_id == service_id,
            )
            .values(work_time=work_time),
        )

    async def update_master_break_time(self, master_id: MasterId, service_id: ServiceId, break_time: int) -> None:
        await self._session.execute(
            update(ServiceMasterAssociationModel)
            .where(
                ServiceMasterAssociationModel.master_id == master_id,
                ServiceMasterAssociationModel.service_id == service_id,
            )
            .values(break_time=break_time),
        )
