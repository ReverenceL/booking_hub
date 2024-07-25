from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Start
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const

from ..state_groups.appointments import ClientAppointmentsSG
from ..state_groups.main_menu import MainMenuSG

client_appointments_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Встречи"),
        Start(Const("Назад"), id="close", state=MainMenuSG.MENU),
        state=ClientAppointmentsSG.LIST,
    ),
)
