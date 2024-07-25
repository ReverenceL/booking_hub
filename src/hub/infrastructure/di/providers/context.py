from aiogram.types import TelegramObject
from dishka import Provider, Scope, from_context

from hub.main.config import Config


class ContextDataProvider(Provider):
    config = from_context(provides=Config, scope=Scope.APP)
    tgobj = from_context(provides=TelegramObject, scope=Scope.REQUEST)
