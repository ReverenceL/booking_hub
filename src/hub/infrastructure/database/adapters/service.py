from sqlalchemy import delete, update

from hub.application.common.interfaces import ServiceReader, ServiceSaver
from hub.application.service.exceptions import ServiceIdNotExistsError
from hub.domain.models.bot import BotId
from hub.domain.models.service import Service, ServiceDescription, ServiceId, ServiceName
from hub.infrastructure.database.adapters.base import BaseDbGateway, CommiterImpl
from hub.infrastructure.database.converters import service_converter
from hub.infrastructure.database.models import ServiceModel


class ServiceDbGateway(BaseDbGateway, CommiterImpl, ServiceReader, ServiceSaver):
    async def save_service(self, bot_id: BotId, service: Service) -> ServiceId:
        service_model = ServiceModel()
        service_model.name = service.name
        service_model.bot_id = bot_id
        service_model.description = service.description
        self._session.add(service_model)
        await self._session.flush()
        return service_model.id

    async def update_service_name(self, service_id: ServiceId, name: ServiceName) -> None:
        await self._session.execute(
            update(ServiceModel).where(ServiceModel.id == service_id).values(name=name),
        )

    async def update_service_description(self, service_id: ServiceId, description: ServiceDescription) -> None:
        await self._session.execute(
            update(ServiceModel).where(ServiceModel.id == service_id).values(description=description),
        )

    async def get_service(self, service_id: ServiceId) -> Service:
        service_model = await self._session.get(ServiceModel, service_id)
        if service_model is None:
            raise ServiceIdNotExistsError
        return service_converter(service_model)

    async def delete_service(self, service_id: ServiceId) -> None:
        await self._session.execute(
            delete(ServiceModel).where(ServiceModel.id == service_id),
        )
