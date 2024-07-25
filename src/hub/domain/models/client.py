from dataclasses import dataclass

from hub.domain.models.bot import BotId
from hub.domain.models.city import CityId
from hub.domain.new_type import new_type

ClientId = new_type("ClientId", int)
ClientTelegramId = new_type("ClientTelegramId", int)
ClientName = new_type("ClientName", str)


@dataclass
class Client:
    id: ClientId
    telegram_id: ClientTelegramId
    name: ClientName

    bot_id: BotId
    city_id: CityId
