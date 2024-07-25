from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import MasterReader
from hub.domain.models.bot import BotId
from hub.domain.models.master import MasterId
from hub.domain.models.service import Service


@dataclass
class GetMasterAvailableServicesDTO:
    bot_id: BotId
    master_id: MasterId


class GetMasterAvailableServicesDbGateway(MasterReader, Protocol):
    pass


class GetMasterAvailableServices(Interactor[GetMasterAvailableServicesDTO, tuple[tuple[bool, Service], ...]]):
    def __init__(self, db_gateway: GetMasterAvailableServicesDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetMasterAvailableServicesDTO) -> tuple[tuple[bool, Service], ...]:
        return await self.db_gateway.get_available_services(data.bot_id, data.master_id)
