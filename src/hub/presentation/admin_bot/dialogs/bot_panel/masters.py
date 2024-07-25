from collections.abc import Awaitable, Callable
from typing import Any

from aiogram import F
from aiogram.fsm.state import State
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, ShowMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Group, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from dishka import FromDishka

from hub.application.bot.get_branches import GetBotBranches, GetBotBranchesDTO
from hub.application.bot.get_cities import GetBotCities, GetBotCitiesDTO
from hub.application.bot.get_masters import GetBotMasters, GetBotMastersDTO
from hub.application.bot.get_services import GetBotServices, GetBotServicesDTO
from hub.application.branch.get import GetBranch, GetBranchDTO
from hub.application.master.create import CreateMaster, CreateMasterDTO
from hub.application.master.delete import DeleteMaster, DeleteMasterDTO
from hub.application.master.get import GetMaster, GetMasterDTO
from hub.application.master.get_master_available_branches import (
    GetMasterAvailableBranches,
    GetMasterAvailableBranchesDTO,
)
from hub.application.master.get_master_available_services import (
    GetMasterAvailableServices,
    GetMasterAvailableServicesDTO,
)
from hub.application.master.update import UpdateMaster, UpdateMasterDTO, UpdateServiceTimeDTO
from hub.application.service.get import GetService, GetServiceDTO
from hub.domain.models.bot import BotId
from hub.domain.models.branch import BranchId
from hub.domain.models.city import CityId
from hub.domain.models.master import MasterId, MasterName
from hub.domain.models.service import ServiceId
from hub.infrastructure.di.injectors import inject_getter, inject_handler, inject_trigger
from hub.presentation.admin_bot.state_groups.bot_panel import (
    AddMasterSG,
    BotPanelSG,
    BranchSG,
    MasterEditBreakTimeSG,
    MasterEditWorkTimeSG,
    MasterSG,
)
from ..common import (
    open_with_bot_id,
    put_start_data_to_dialog_data,
)


@inject_getter
async def master_list_getter(
    dialog_manager: DialogManager,
    get_bot_masters: FromDishka[GetBotMasters],
    **_: Any,
) -> dict[str, Any]:
    masters = await get_bot_masters(
        GetBotMastersDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {"masters": masters}


@inject_getter
async def master_editor_getter(
    dialog_manager: DialogManager,
    get_master: FromDishka[GetMaster],
    **_: Any,
) -> dict[str, Any]:
    master = await get_master(
        GetMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    return {
        "master": master,
    }


@inject_trigger
async def process_start_masters_dialog(
    start_data: BotId,
    dialog_manager: DialogManager,
    get_branches: FromDishka[GetBotBranches],
) -> None:
    branches = await get_branches(
        GetBotBranchesDTO(
            bot_id=start_data,
        ),
    )
    if len(branches) == 0:
        await dialog_manager.switch_to(state=MasterSG.NO_BRANCHES)


async def process_open_editor(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    master_id: MasterId,
) -> None:
    dialog_manager.dialog_data["master_id"] = master_id
    await dialog_manager.switch_to(state=MasterSG.EDITOR)


@inject_handler
async def process_update_master_name(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    name: MasterName,
    update_master: FromDishka[UpdateMaster],
) -> None:
    await update_master(
        UpdateMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
            name=name,
        ),
    )
    await dialog_manager.switch_to(state=MasterSG.EDITOR, show_mode=ShowMode.EDIT)
    await message.delete()


@inject_handler
async def process_delete_master(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    delete_master: FromDishka[DeleteMaster],
) -> None:
    await delete_master(
        DeleteMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    await dialog_manager.switch_to(state=MasterSG.LIST)


@inject_handler
async def process_select_branch(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    branch_id: BranchId,
    get_branch: FromDishka[GetBranch],
    update_master: FromDishka[UpdateMaster],
) -> None:
    branch = await get_branch(
        GetBranchDTO(
            branch_id=branch_id,
        ),
    )
    await update_master(
        UpdateMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
            branch=branch,
        ),
    )


@inject_handler
async def process_select_service(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    service_id: ServiceId,
    get_service: FromDishka[GetService],
    update_master: FromDishka[UpdateMaster],
) -> None:
    service = await get_service(GetServiceDTO(service_id=service_id))
    await update_master(
        UpdateMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
            service=service,
        ),
    )


@inject_getter
async def available_branches_getter(
    dialog_manager: DialogManager,
    get_branches: FromDishka[GetMasterAvailableBranches],
    **_: Any,
) -> dict[str, Any]:
    branches = await get_branches(
        GetMasterAvailableBranchesDTO(
            bot_id=dialog_manager.start_data,
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    return {
        "branches": branches,
    }


@inject_getter
async def get_available_services(
    dialog_manager: DialogManager,
    get_services: FromDishka[GetMasterAvailableServices],
    **_: Any,
) -> dict[str, Any]:
    services = await get_services(
        GetMasterAvailableServicesDTO(
            bot_id=dialog_manager.start_data,
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    return {
        "services": services,
    }


def open_with_master_id(state: State) -> Callable[[Any, Any, DialogManager], Awaitable[None]]:
    async def on_click(_: Any, __: Any, dialog_manager: DialogManager) -> None:
        await dialog_manager.start(
            state=state,
            data={"master_id": dialog_manager.dialog_data["master_id"], "bot_id": dialog_manager.start_data},
        )

    return on_click


masters_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Список мастеров:", when=F["masters"]),
        Multi(
            Const("У вас не создано ни одного мастера!"),
            Const("Добавим нового?"),
            sep="\n\n",
            when=~F["masters"],
        ),
        Group(
            Select(
                Format("{item.name}"),
                id="select.master",
                item_id_getter=lambda master: master.id,
                items="masters",
                on_click=process_open_editor,
                type_factory=MasterId,
            ),
            width=2,
        ),
        Button(Const("➕ Добавить"), id="add.master", on_click=open_with_bot_id(AddMasterSG.GET_NAME)),
        Cancel(Const("⬅️ Назад")),
        state=MasterSG.LIST,
        getter=master_list_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("У Вас нет мастеров и мы не можем их добавить!"),
            Const("Для работы с мастерами нужны отделения, а у Вас не создано ни одного отделения."),
            Const("Перейти к отделениям?"),
            sep="\n\n",
        ),
        Button(Const("↗️ К городам"), id="open.cities", on_click=open_with_bot_id(BranchSG.LIST)),
        Button(Const("↩️ Назад"), id="open.bot.panel", on_click=open_with_bot_id(BotPanelSG.MENU)),
        state=MasterSG.NO_BRANCHES,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Настройки мастера: {{ master.name }}"),
        SwitchTo(Const("Сменить имя"), id="open.edit.name", state=MasterSG.EDIT_NAME),
        SwitchTo(Const("Отделения работы"), id="open.edit.branch", state=MasterSG.EDIT_BRANCH),
        SwitchTo(Const("Оказываемые услуги"), id="open.edit.services", state=MasterSG.EDIT_SERVICES),
        Button(
            Const("Время оказания услуг"),
            id="open.edit.work.time",
            on_click=open_with_master_id(MasterEditWorkTimeSG.GET_SERVICE),
        ),
        Button(
            Const("Перерывы"),
            id="open.edit.break.time",
            on_click=open_with_master_id(MasterEditBreakTimeSG.GET_SERVICE),
        ),
        SwitchTo(Const("❌ Удалить"), id="open.delete.master", state=MasterSG.DELETE),
        SwitchTo(Const("↩️ Назад"), id="open.masters.list", state=MasterSG.LIST),
        state=MasterSG.EDITOR,
        getter=master_editor_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Отправьте новое имя мастера:"),
        TextInput(
            id="get.new.name",
            on_success=process_update_master_name,
            type_factory=MasterName,
        ),
        SwitchTo(Const("↩️ Назад"), id="back.to.editor", state=MasterSG.EDITOR),
        state=MasterSG.EDIT_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Выберите отделения в котором работает мастер:"),
        Column(
            Select(
                Multi(
                    Const("✔️", when=F["item"].is_associated),
                    Jinja("{{ item.name }}"),
                    sep=" ",
                ),
                id="select.branch",
                item_id_getter=lambda branch: branch.id,
                items="branches",
                type_factory=BranchId,
                on_click=process_select_branch,
            ),
        ),
        SwitchTo(Const("↩️ Назад"), id="back.to.editor", state=MasterSG.EDITOR),
        state=MasterSG.EDIT_BRANCH,
        getter=available_branches_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Выберите услуги, которые оказывает мастер:"),
        Column(
            Select(
                Multi(
                    Const("✔️", when=F["item"].is_associated),
                    Jinja("{{ item.name }}"),
                    sep=" ",
                ),
                id="select.service",
                item_id_getter=lambda service: service.id,
                items="services",
                type_factory=ServiceId,
                on_click=process_select_service,
            ),
        ),
        SwitchTo(Const("↩️ Назад"), id="back.to.editor", state=MasterSG.EDITOR),
        state=MasterSG.EDIT_SERVICES,
        getter=get_available_services,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Вы уверены, что хотите удалить мастера?"),
        Button(Const("Да"), id="delete.master", on_click=process_delete_master),
        SwitchTo(Const("↩️ Я передумал"), id="back.to.editor", state=MasterSG.EDITOR),
        state=MasterSG.DELETE,
    ),
    on_start=process_start_masters_dialog,
)


async def process_edit_service_time(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    service_id: ServiceId,
) -> None:
    dialog_manager.dialog_data["service_id"] = service_id
    await dialog_manager.next()


@inject_handler
async def process_work_time(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    work_time: int,
    update_master: FromDishka[UpdateMaster],
    get_service: FromDishka[GetService],
) -> None:
    service = await get_service(GetServiceDTO(service_id=dialog_manager.dialog_data["service_id"]))
    await update_master(
        UpdateMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
            service_time=UpdateServiceTimeDTO(
                service=service,
                work_time=work_time,
            ),
        ),
    )
    await dialog_manager.done()


@inject_handler
async def process_break_time(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    break_time: int,
    update_master: FromDishka[UpdateMaster],
    get_service: FromDishka[GetService],
) -> None:
    service = await get_service(GetServiceDTO(service_id=dialog_manager.dialog_data["service_id"]))
    await update_master(
        UpdateMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
            service_time=UpdateServiceTimeDTO(
                service=service,
                break_time=break_time,
            ),
        ),
    )
    await dialog_manager.done()


@inject_getter
async def get_services(
    dialog_manager: DialogManager,
    get_master_services: FromDishka[GetMasterAvailableServices],
    **_: Any,
) -> dict[str, Any]:
    services = await get_master_services(
        GetMasterAvailableServicesDTO(
            bot_id=dialog_manager.dialog_data["bot_id"],
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    return {"services": [service for service in services if service.is_associated]}


@inject_getter
async def master_edit_work_time_get_service_getter(
    dialog_manager: DialogManager,
    get_master: FromDishka[GetMaster],
    get_bot_services: FromDishka[GetBotServices],
    **_: Any,
) -> dict[str, Any]:
    master = await get_master(
        GetMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    services = await get_bot_services(
        GetBotServicesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "master": master,
        "services": services,
    }


@inject_getter
async def master_edit_break_work_get_work_time_getter(
    dialog_manager: DialogManager,
    get_master: FromDishka[GetMaster],
    get_service: FromDishka[GetService],
    **_: Any,
) -> dict[str, Any]:
    master = await get_master(
        GetMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    service = await get_service(
        GetServiceDTO(
            service_id=dialog_manager.dialog_data["service_id"],
        ),
    )
    return {
        "master": master,
        "service": service,
    }


edit_master_work_time_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Выберите услугу, для которой нужно изменить время оказания мастером {{ master.name }}"),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="select.service",
                item_id_getter=lambda service: service.id,
                type_factory=ServiceId,
                items="services",
                on_click=process_edit_service_time,
            ),
        ),
        Cancel(Const("↩️ Назад")),
        state=MasterEditWorkTimeSG.GET_SERVICE,
        getter=master_edit_work_time_get_service_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Время оказания услуги {{ service.name }} мастером {{ master.name }}"),
            Const("Отправьте время оказания в минутах, например «120», т.е. 2 часа."),
        ),
        TextInput(
            id="get_work_time",
            on_success=process_work_time,
            type_factory=int,
        ),
        Back(Const("⬅️ Назад")),
        state=MasterEditWorkTimeSG.GET_WORK_TIME,
        getter=master_edit_break_work_get_work_time_getter,
    ),
    on_start=put_start_data_to_dialog_data,
)


@inject_getter
async def master_edit_break_time_get_service_getter(
    dialog_manager: DialogManager,
    get_master: FromDishka[GetMaster],
    get_bot_services: FromDishka[GetBotServices],
    **_: Any,
) -> dict[str, Any]:
    master = await get_master(
        GetMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    services = await get_bot_services(
        GetBotServicesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "master": master,
        "services": services,
    }


@inject_getter
async def master_edit_break_time_get_break_time_getter(
    dialog_manager: DialogManager,
    get_master: FromDishka[GetMaster],
    get_service: FromDishka[GetService],
    **_: Any,
) -> dict[str, Any]:
    master = await get_master(
        GetMasterDTO(
            master_id=dialog_manager.dialog_data["master_id"],
        ),
    )
    service = await get_service(
        GetServiceDTO(
            service_id=dialog_manager.dialog_data["service_id"],
        ),
    )
    return {
        "master": master,
        "service": service,
    }


edit_master_break_time_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Выберите услугу, для которой нужно изменить перерыв после оказания работ мастером {{ master.name }}"),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="select.service",
                item_id_getter=lambda service: service.id,
                type_factory=ServiceId,
                items="services",
                on_click=process_edit_service_time,
            ),
        ),
        Cancel(Const("↩️ Назад")),
        state=MasterEditBreakTimeSG.GET_SERVICE,
        getter=master_edit_break_time_get_service_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Время перерыва после оказания услуги {{ service.name }} мастером {{ master.name }}."),
            Const("Отправьте время перерыва в минутах, например «15», т.е. 15 минут."),
        ),
        TextInput(
            id="get_break_time",
            on_success=process_break_time,
            type_factory=int,
        ),
        Back(Const("⬅️ Назад")),
        state=MasterEditBreakTimeSG.GET_BREAK_TIME,
        getter=master_edit_break_time_get_break_time_getter,
    ),
    on_start=put_start_data_to_dialog_data,
)


@inject_getter
async def add_master_get_city_getter(
    dialog_manager: DialogManager,
    get_bot_cities: FromDishka[GetBotCities],
    **_: Any,
) -> dict[str, Any]:
    cities = await get_bot_cities(
        GetBotCitiesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {"cities": cities}


async def get_new_master_name(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    name: MasterName,
) -> None:
    dialog_manager.dialog_data["master_name"] = name
    await dialog_manager.switch_to(
        state=AddMasterSG.GET_CITY,
        show_mode=ShowMode.EDIT,
    )
    await message.delete()


@inject_handler
async def process_select_city(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    city_id: CityId,
    create_master: FromDishka[CreateMaster],
) -> None:
    await create_master(
        CreateMasterDTO(
            name=dialog_manager.dialog_data["master_name"],
            city_id=city_id,
            bot_id=dialog_manager.start_data,
        ),
    )
    await dialog_manager.done()


add_master_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем мастера!"),
            Const("Как назовем мастера?"),
            Const("Отправьте имя:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.name",
            on_success=get_new_master_name,
        ),
        Cancel(Const("↩️ Назад")),
        state=AddMasterSG.GET_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем мастера!"),
            Jinja("Имя: {{ dialog_data.master_name }}"),
            Const("Теперь нужно выбрать город, в котором мастер работает 👇"),
            sep="\n\n",
        ),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="select.city",
                item_id_getter=lambda city: city.id,
                items="cities",
                type_factory=CityId,
                on_click=process_select_city,
            ),
        ),
        Back(Const("↩️ Назад")),
        state=AddMasterSG.GET_CITY,
        getter=add_master_get_city_getter,
    ),
)
