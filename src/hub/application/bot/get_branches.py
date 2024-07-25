from dataclasses import dataclass
from typing import Protocol

from hub.application.common.exceptions import InsufficientDataError
from hub.application.common.interactor import Interactor
from hub.application.common.interfaces import BotReader
from hub.domain.models.bot import BotId, BotTelegramId
from hub.domain.models.branch import Branch


@dataclass
class GetBotBranchesDTO:
    bot_id: BotId | None = None
    bot_telegram_id: BotTelegramId | None = None


class GetBotBranchesDbGateway(BotReader, Protocol):
    pass


class GetBotBranches(Interactor[GetBotBranchesDTO, list[Branch]]):
    def __init__(self, db_gateway: GetBotBranchesDbGateway):
        self.db_gateway = db_gateway

    async def __call__(self, data: GetBotBranchesDTO) -> list[Branch]:
        if data.bot_id:
            return await self.db_gateway.get_bot_branches(data.bot_id)
        elif data.bot_telegram_id:
            bot = await self.db_gateway.get_bot_by_telegram_id(data.bot_telegram_id)
            return await self.db_gateway.get_bot_branches(bot.id)
        else:
            raise InsufficientDataError
