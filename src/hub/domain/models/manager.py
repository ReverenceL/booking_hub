from dataclasses import dataclass

from hub.domain.new_type import new_type

ManagerId = new_type("ManagerId", int)
ManagerTelegramId = new_type("ManagerTelegramId", int)


@dataclass
class Manager:
    id: ManagerId | None
    telegram_id: ManagerTelegramId | None
