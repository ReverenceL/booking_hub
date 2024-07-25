from dataclasses import dataclass

from hub.domain.models.bot import BotId
from hub.domain.new_type import new_type

ServiceId = new_type("ServiceId", int)
ServiceName = new_type("ServiceName", str)
ServiceDescription = new_type("ServiceDescription", str)


@dataclass
class Service:
    id: ServiceId | None
    name: ServiceName
    description: ServiceDescription | None

    bot_id: BotId


@dataclass
class AvailableService(Service):
    is_associated: bool
