from aiogram import Dispatcher

from .appointments import client_appointments_dialog
from .booking import booking_dialog
from .main_menu import main_menu_dialog, registration_dialog


def setup_dialogs(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(
        registration_dialog,
        main_menu_dialog,
        client_appointments_dialog,
        booking_dialog,
    )
