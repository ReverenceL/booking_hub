from dataclasses import dataclass

from hub.domain.models.bot import BotId
from hub.domain.models.timezone import TimeZone
from hub.domain.new_type import new_type

CityId = int
CityName = str


@dataclass
class City:
    id: CityId | None
    name: CityName
    timezone: TimeZone

    bot_id: BotId
