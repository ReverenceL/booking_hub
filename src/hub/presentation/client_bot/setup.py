from aiogram import Dispatcher

from .dialogs import setup_dialogs
from .middlewares import setup_middlewares
from .routes import setup_routes


def setup(dispatcher: Dispatcher) -> Dispatcher:
    setup_routes(dispatcher)
    setup_dialogs(dispatcher)
    setup_middlewares(dispatcher)
    return dispatcher
