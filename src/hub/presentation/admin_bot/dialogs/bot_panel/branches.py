from typing import Any

from aiogram import F
from aiogram.types import Message
from aiogram_dialog import Dialog, DialogManager, LaunchMode, ShowMode, Window
from aiogram_dialog.widgets.input import TextInput
from aiogram_dialog.widgets.kbd import Back, Button, Cancel, Column, Select, SwitchTo
from aiogram_dialog.widgets.media import StaticMedia
from aiogram_dialog.widgets.text import Const, Format, Jinja, Multi
from dishka import FromDishka

from hub.application.bot.get_branches import GetBotBranches, GetBotBranchesDTO
from hub.application.bot.get_cities import GetBotCities, GetBotCitiesDTO
from hub.application.branch.create import CreateBranch, CreateBranchDTO
from hub.application.branch.delete import DeleteBranch, DeleteBranchDTO
from hub.application.branch.get import GetBranch, GetBranchDTO
from hub.application.branch.update import UpdateBranch, UpdateBranchDTO
from hub.application.city.get import GetCity, GetCityDTO
from hub.domain.models.bot import BotId
from hub.domain.models.branch import BranchId, BranchName
from hub.domain.models.city import CityId
from hub.infrastructure.di.injectors import inject_getter, inject_handler, inject_trigger
from hub.presentation.admin_bot.dialogs.common import open_with_bot_id
from hub.presentation.admin_bot.state_groups.bot_panel import AddBranchSG, BotPanelSG, BranchSG, CitySG


@inject_getter
async def bot_branches_getter(
    dialog_manager: DialogManager,
    get_branches: FromDishka[GetBotBranches],
    **_: Any,
) -> dict[str, Any]:
    branches = await get_branches(
        GetBotBranchesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "branches": branches,
    }


@inject_getter
async def branch_editor_getter(
    dialog_manager: DialogManager,
    get_branch: FromDishka[GetBranch],
    **_: Any,
) -> dict[str, Any]:
    branch = await get_branch(GetBranchDTO(branch_id=dialog_manager.dialog_data["branch_id"]))
    return {"branch": branch}


@inject_trigger
async def process_start_branches_dialog(
    start_data: BotId,
    dialog_manager: DialogManager,
    get_cities: FromDishka[GetBotCities],
) -> None:
    cities = await get_cities(
        GetBotCitiesDTO(
            bot_id=start_data,
        ),
    )
    if len(cities) == 0:
        await dialog_manager.switch_to(state=BranchSG.NO_CITIES)


@inject_handler
async def process_open_branch_editor(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    branch_id: BranchId,
) -> None:
    dialog_manager.dialog_data["branch_id"] = branch_id
    await dialog_manager.switch_to(BranchSG.EDITOR)


@inject_handler
async def process_delete_branch(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    delete_branch: FromDishka[DeleteBranch],
) -> None:
    await delete_branch(
        DeleteBranchDTO(
            branch_id=dialog_manager.dialog_data["branch_id"],
        ),
    )
    await dialog_manager.switch_to(state=BranchSG.LIST)


@inject_handler
async def process_new_name(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    name: BranchName,
    update_branch: FromDishka[UpdateBranch],
) -> None:
    await update_branch(
        UpdateBranchDTO(
            branch_id=dialog_manager.dialog_data["branch_id"],
            name=name,
        ),
    )
    await dialog_manager.switch_to(state=BranchSG.EDITOR)


@inject_handler
async def process_new_address(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    address: str,
    update_branch: FromDishka[UpdateBranch],
) -> None:
    await update_branch(
        UpdateBranchDTO(
            branch_id=dialog_manager.dialog_data["branch_id"],
            address=address,
        ),
    )
    await dialog_manager.switch_to(state=BranchSG.EDITOR)


branches_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Список отделений", when=F["branches"]),
        Multi(
            Const("У Вас нет отделений!"),
            Const("Добавим?"),
            sep="\n\n",
            when=~F["branches"],
        ),
        Column(
            Select(
                Format("{item.address}"),
                items="branches",
                item_id_getter=lambda branch: branch.id,
                id="select.branch",
                type_factory=BranchId,
                on_click=process_open_branch_editor,
            ),
        ),
        Button(Const("➕ Добавить отделение"), id="add.branch", on_click=open_with_bot_id(AddBranchSG.GET_NAME)),
        Button(Const("↩️ Назад"), id="open.bot.panel", on_click=open_with_bot_id(BotPanelSG.MENU)),
        state=BranchSG.LIST,
        getter=bot_branches_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("У Вас нет отделений, но мы не можем их добавить!"),
            Const("Чтобы добавить отделение, нужно выбрать город, а Вы еще не добавили ни одного города."),
            Const("Перейти к городам?"),
            sep="\n\n",
        ),
        Button(Const("↗️ К городам"), id="open.cities", on_click=open_with_bot_id(CitySG.LIST)),
        Button(Const("↩️ Назад"), id="open.bot.panel", on_click=open_with_bot_id(BotPanelSG.MENU)),
        state=BranchSG.NO_CITIES,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Jinja("Настройки отделения\n{{ branch.name }}"),
        SwitchTo(Const("Сменить название"), id="open.edit.name", state=BranchSG.EDIT_NAME),
        SwitchTo(Const("Сменить адрес"), id="open.edit.address", state=BranchSG.EDIT_ADDRESS),
        SwitchTo(Const("❌ Удалить"), id="open.delete.branch", state=BranchSG.DELETE),
        SwitchTo(Const("↩️ Назад"), id="open.branches.list", state=BranchSG.LIST),
        state=BranchSG.EDITOR,
        getter=branch_editor_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Меняем название отделения\n{{ branch_name }}"),
            Const("Отправьте новое название:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.new.name",
            on_success=process_new_name,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.branch.editor", state=BranchSG.EDITOR),
        state=BranchSG.EDIT_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Jinja("Меняем адрес отделения\n{{ branch_name }}"),
            Const("Отправьте новый адрес:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.new.address",
            on_success=process_new_address,
        ),
        SwitchTo(Const("↩️ Назад"), id="open.branch.editor", state=BranchSG.EDITOR),
        state=BranchSG.EDIT_ADDRESS,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Const("Удалить отделение?"),
        Button(Const("✅ Да!"), id="delete.branch", on_click=process_delete_branch),
        SwitchTo(Const("↩️ Я передумал"), id="open.branch.editor", state=BranchSG.EDITOR),
        state=BranchSG.DELETE,
    ),
    on_start=process_start_branches_dialog,
    launch_mode=LaunchMode.ROOT,
)


async def process_new_branch_name(message: Message, _: Any, dialog_manager: DialogManager, name: BranchName) -> None:
    dialog_manager.dialog_data["branch_name"] = name
    dialog_manager.show_mode = ShowMode.EDIT
    await dialog_manager.next()
    await message.delete()


@inject_getter
async def add_branch_get_city_getter(
    dialog_manager: DialogManager,
    get_bot_cities: FromDishka[GetBotCities],
    **_: Any,
) -> dict[str, Any]:
    cities = await get_bot_cities(
        GetBotCitiesDTO(
            bot_id=dialog_manager.start_data,
        ),
    )
    return {
        "cities": cities,
    }


@inject_handler
async def process_select_city(
    _: Any,
    __: Any,
    dialog_manager: DialogManager,
    city_id: CityId,
    get_city: FromDishka[GetCity],
) -> None:
    city = await get_city(
        GetCityDTO(
            city_id=city_id,
        ),
    )
    dialog_manager.dialog_data["city_id"] = city.id
    dialog_manager.dialog_data["city_name"] = city.name

    await dialog_manager.next()


@inject_handler
async def process_new_branch_address(
    message: Message,
    _: Any,
    dialog_manager: DialogManager,
    address: str,
    create_branch: FromDishka[CreateBranch],
) -> None:
    await create_branch(
        CreateBranchDTO(
            city_id=dialog_manager.dialog_data["city_id"],
            name=dialog_manager.dialog_data["branch_name"],
            address=address,
        ),
    )
    await dialog_manager.done(show_mode=ShowMode.EDIT)
    await message.delete()


add_branch_dialog = Dialog(
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем отделение!"),
            Const("Отправьте название:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.name",
            on_success=process_new_branch_name,
            type_factory=BranchName,
        ),
        Cancel(Const("⬅️ Назад")),
        state=AddBranchSG.GET_NAME,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем отделение!"),
            Jinja("Название: {{ dialog_data.branch_name }}"),
            Const("Нам нужно знать, в каком городе находится Ваше отделение."),
            Const("Выберите город из списка 👇"),
            sep="\n\n",
        ),
        Column(
            Select(
                Jinja("{{ item.name }}"),
                id="get.city",
                items=F["cities"],
                item_id_getter=lambda city: city.id,
                type_factory=CityId,
                on_click=process_select_city,
            ),
        ),
        Back(Const("↩️ Назад")),
        state=AddBranchSG.GET_CITY,
        getter=add_branch_get_city_getter,
    ),
    Window(
        StaticMedia(path="./resources/media/main_bot/stub.png"),
        Multi(
            Const("Добавляем отделение!"),
            Multi(
                Jinja("Название: {{ dialog_data.branch_name }}"),
                Jinja("Город: {{ dialog_data.city_name }}"),
                sep="\n",
            ),
            Const("Чтобы клиенты могли найти Ваше отделение, нам нужен адрес."),
            Const("Отправьте адрес отделения текстом:"),
            sep="\n\n",
        ),
        TextInput(
            id="get.address",
            on_success=process_new_branch_address,
        ),
        Back(Const("↩️ Назад")),
        Const("💡 Отправьте адрес нового отделения:"),
        state=AddBranchSG.GET_ADDRESS,
    ),
)
