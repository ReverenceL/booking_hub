from dataclasses import dataclass

from hub.domain.models.bot import BotId
from hub.domain.models.city import CityId
from hub.domain.new_type import new_type

MasterId = new_type("MasterId", int)
MasterName = new_type("MasterName", str)


@dataclass
class Master:
    id: MasterId | None
    name: MasterName

    bot_id: BotId
    city_id: CityId
