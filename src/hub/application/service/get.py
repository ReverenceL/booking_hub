from dataclasses import dataclass
from typing import Protocol

from hub.application.common.exceptions import InsufficientDataError
from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import ServiceReader
from hub.domain.models.service import Service, ServiceId


@dataclass
class GetServiceDTO:
    service_id: ServiceId | None = None


class GetServiceDbGateway(ServiceReader, Protocol):
    pass


class GetService(Interactor[GetServiceDTO, Service]):
    def __init__(self, db_gateway: GetServiceDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetServiceDTO) -> Service:
        if data.service_id:
            return await self.db_gateway.get_service(data.service_id)
        else:
            raise InsufficientDataError
