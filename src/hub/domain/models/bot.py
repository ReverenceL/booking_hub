from dataclasses import dataclass

from hub.domain.models.manager import ManagerId
from hub.domain.new_type import new_type

BotId = int
BotTelegramId = int
BotToken = str
BotName = str


@dataclass
class Bot:
    id: BotId | None
    token: BotToken
    telegram_id: BotTelegramId
    name: BotName

    manager_id: ManagerId
