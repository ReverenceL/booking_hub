from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, ServiceSaver
from hub.domain.models.bot import BotId
from hub.domain.models.service import Service, ServiceDescription, ServiceId, ServiceName


@dataclass
class CreateServiceDTO:
    bot_id: BotId
    name: ServiceName
    description: ServiceDescription


class CreateServiceDbGateway(Committer, ServiceSaver, Protocol):
    pass


class CreateService(Interactor[CreateServiceDTO, ServiceId]):
    def __init__(self, db_gateway: CreateServiceDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: CreateServiceDTO) -> ServiceId:
        service = Service(
            id=None,
            name=data.name,
            bot_id=data.bot_id,
            description=data.description,
        )
        service_id = await self.db_gateway.save_service(data.bot_id, service)
        await self.db_gateway.commit()
        return service_id
