from aiogram import Dispatcher

from ..routes import root


def setup_routes(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(
        root.router,
    )
