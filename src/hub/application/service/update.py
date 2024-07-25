from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, ServiceSaver
from hub.domain.models.service import ServiceId


@dataclass
class ServiceUpdateDTO:
    service_id: ServiceId
    name: str | None = None
    description: str | None = None


class ServiceUpdateDbGateway(Committer, ServiceSaver, Protocol):
    pass


class ServiceUpdate(Interactor[ServiceUpdateDTO, None]):
    def __init__(self, db_gateway: ServiceUpdateDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: ServiceUpdateDTO) -> None:
        if data.name:
            await self.db_gateway.update_service_name(data.service_id, data.name)
        if data.description:
            await self.db_gateway.update_service_description(data.service_id, data.description)
        await self.db_gateway.commit()
