from aiogram import Dispatcher

from .add_bot import add_bot_dialog
from .bot_panel.branches import add_branch_dialog, branches_dialog
from .bot_panel.cities import add_city_dialog, cities_dialog
from .bot_panel.masters import (
    add_master_dialog,
    edit_master_break_time_dialog,
    edit_master_work_time_dialog,
    masters_dialog,
)
from .bot_panel.menu import bot_panel_dialog
from .bot_panel.services import add_service_dialog, services_dialog
from .main_menu import bots_list_dialog


def setup_dialogs(dispatcher: Dispatcher) -> None:
    dispatcher.include_routers(
        bots_list_dialog,
        add_bot_dialog,
        bot_panel_dialog,
        branches_dialog,
        add_branch_dialog,
        cities_dialog,
        add_city_dialog,
        masters_dialog,
        add_master_dialog,
        services_dialog,
        add_service_dialog,
        edit_master_work_time_dialog,
        edit_master_break_time_dialog,
    )
