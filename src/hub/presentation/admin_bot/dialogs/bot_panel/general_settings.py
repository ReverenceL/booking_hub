from aiogram_dialog import Dialog, Window
from aiogram_dialog.widgets.kbd import Button, Group
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Jinja, Multi

from hub.presentation.admin_bot.dialogs.common import open_with_bot_id
from hub.presentation.admin_bot.state_groups.bot_panel import GeneralSettingsSG, WorkingHoursEditorSG

general_settings_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Это общие настройки бота:"),
        Group(
            Button(Const("Настроить рабочее время"), id="open.time.editor", on_click=open_with_bot_id),
        ),
        state=GeneralSettingsSG.LIST,
    ),
)

working_hours_editor_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Рабочие дни: {{ work_days }}"),
            Jinja("Рабочее время: {{ work_time }}"),
            Jinja("Перерыв: {{ break_time }}"),
            sep="\n",
        ),
        state=WorkingHoursEditorSG.VIEW,
    ),
)
