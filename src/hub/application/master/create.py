from dataclasses import dataclass
from typing import Protocol

from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import Committer, MasterSaver
from hub.domain.models.bot import BotId
from hub.domain.models.city import CityId
from hub.domain.models.master import Master, MasterId, MasterName


@dataclass
class CreateMasterDTO:
    name: MasterName
    bot_id: BotId
    city_id: CityId


class CreateMasterDbGateway(Committer, MasterSaver, Protocol):
    pass


class CreateMaster(Interactor[CreateMasterDTO, MasterId]):
    def __init__(self, db_gateway: CreateMasterDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: CreateMasterDTO) -> MasterId:
        master = Master(
            id=None,
            name=data.name,
            bot_id=data.bot_id,
            city_id=data.city_id,
        )
        master_id = await self.db_gateway.save_master(master=master)
        await self.db_gateway.commit()
        return master_id
