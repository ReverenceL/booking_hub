from typing import Any

from aiogram import F
from aiogram.types import CallbackQuery, Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Button, Cancel, Column, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from dishka import FromDishka

from hub.application.bot.get_services import GetBotServices, GetBotServicesDTO
from hub.application.service.create import CreateService, CreateServiceDTO
from hub.application.service.delete import DeleteService, DeleteServiceDTO
from hub.application.service.get import GetService, GetServiceDTO
from hub.application.service.update import ServiceUpdate, ServiceUpdateDTO
from hub.domain.models.service import ServiceId, ServiceName
from hub.infrastructure.di.injectors import inject_getter, inject_handler
from hub.presentation.admin_bot.dialogs.common import open_with_bot_id
from hub.presentation.admin_bot.state_groups.bot_panel import AddServiceSG, ServiceSG


@inject_getter
async def service_list_getter(
    dialog_manager: DialogManager,
    get_bot_services: FromDishka[GetBotServices],
    **_: Any,
) -> dict[str, Any]:
    services = await get_bot_services(
        GetBotServicesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "services": services,
    }


@inject_getter
async def service_editor_getter(
    dialog_manager: DialogManager,
    get_service: FromDishka[GetService],
    **_: Any,
) -> dict[str, Any]:
    service = await get_service(
        GetServiceDTO(
            service_id=dialog_manager.dialog_data["service_id"],
        ),
    )
    return {
        "service": service,
    }


@inject_handler
async def process_select_service(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    service_id: ServiceId,
) -> None:
    dialog_manager.dialog_data["service_id"] = service_id
    await dialog_manager.switch_to(state=ServiceSG.EDITOR)


@inject_handler
async def process_delete_service(
    callback_query: CallbackQuery,
    _: Any,
    dialog_manager: DialogManager,
    service_deleter: FromDishka[DeleteService],
) -> None:
    key = f"delete.service.{dialog_manager.dialog_data['service_id']}"
    if dialog_manager.dialog_data.get(key, False):
        await service_deleter(
            DeleteServiceDTO(
                service_id=dialog_manager.dialog_data["service_id"],
            ),
        )
        await callback_query.answer("Услуга удалена.", show_alert=True)
        await dialog_manager.switch_to(state=ServiceSG.LIST)
        return
    dialog_manager.dialog_data[key] = True
    await callback_query.answer(
        text="Вы уверены, что хотите удалить услугу?\nЕсли да, то нажмите на кнопку удаления еще раз.",
        show_alert=True,
    )


@inject_handler
async def process_update_service_name(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    new_name: str,
    service_update: FromDishka[ServiceUpdate],
) -> None:
    await service_update(
        ServiceUpdateDTO(
            service_id=dialog_manager.dialog_data["service_id"],
            name=new_name,
        ),
    )
    await dialog_manager.switch_to(state=ServiceSG.EDITOR, show_mode=ShowMode.EDIT)
    await message.delete()


@inject_handler
async def process_update_service_description(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    new_description: str,
    service_update: FromDishka[ServiceUpdate],
) -> None:
    await service_update(
        ServiceUpdateDTO(
            service_id=dialog_manager.dialog_data["service_id"],
            description=new_description,
        ),
    )
    await dialog_manager.switch_to(state=ServiceSG.EDITOR, show_mode=ShowMode.EDIT)
    await message.delete()


services_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Список услуг", when=F["services"]),
        Multi(
            Const("У вас не добавлено ни одной услуги!"),
            Const("Давайте покажем клиентам, что мы умеем! Добавить услугу?"),
            sep="\n\n",
            when=~F["services"],
        ),
        Column(
            Select(
                Format("{item.name}"),
                id="select.service",
                item_id_getter=lambda service: service.id,
                items="services",
                type_factory=ServiceId,
                on_click=process_select_service,
            ),
        ),
        Button(
            Const("➕ Добавить"),
            id="add.service",
            on_click=open_with_bot_id(AddServiceSG.GET_NAME),
        ),
        Cancel(Const("↩️ Назад")),
        state=ServiceSG.LIST,
        getter=service_list_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Управление услугой"),
        Jinja("{{ service.name }}"),
        SwitchTo(Const("Сменить название"), id="edit.name", state=ServiceSG.EDIT_NAME),
        SwitchTo(Const("Сменить описание"), id="edit.description", state=ServiceSG.EDIT_DESCRIPTION),
        Button(Const("❌ Удалить"), id="delete.service", on_click=process_delete_service),
        SwitchTo(Const("↩️ Назад"), id="open.list", state=ServiceSG.LIST),
        state=ServiceSG.EDITOR,
        getter=service_editor_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Отправьте новое название услуги:"),
        TextInput(
            id="get.new.name",
            on_success=process_update_service_name,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.editor", state=ServiceSG.EDITOR),
        state=ServiceSG.EDIT_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Отправьте новое описание услуги:"),
        TextInput(
            id="get.new.name",
            on_success=process_update_service_description,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.editor", state=ServiceSG.EDITOR),
        state=ServiceSG.EDIT_DESCRIPTION,
    ),
)


@inject_handler
async def process_new_service_name(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    name: ServiceName,
    create_service: FromDishka[CreateService],
) -> None:
    await create_service(
        CreateServiceDTO(
            bot_id=dialog_manager.start_data,
            name=name,
            description=None,
        ),
    )
    await dialog_manager.done(show_mode=ShowMode.EDIT)
    await message.delete()


add_service_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Отправьте название новой услуги:"),
        TextInput(
            id="get.service.name",
            on_success=process_new_service_name,
        ),
        Cancel(Const("↩️ Назад")),
        state=AddServiceSG.GET_NAME,
    ),
)
