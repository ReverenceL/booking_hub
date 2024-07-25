from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, ServiceSaver
from hub.domain.models.service import ServiceId


@dataclass
class DeleteServiceDTO:
    service_id: ServiceId


class DeleteServiceDbGateway(Committer, ServiceSaver, Protocol):
    pass


class DeleteService(Interactor[DeleteServiceDTO, None]):
    def __init__(self, db_gateway: DeleteServiceDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: DeleteServiceDTO) -> None:
        await self.db_gateway.delete_service(data.service_id)
        await self.db_gateway.commit()
