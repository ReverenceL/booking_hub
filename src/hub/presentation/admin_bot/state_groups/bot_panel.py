from aiogram.fsm.state import State, StatesGroup


class BotPanelSG(StatesGroup):
    MENU = State()


class CitySG(StatesGroup):
    LIST = State()
    EDITOR = State()
    EDIT_NAME = State()
    EDIT_TIMEZONE = State()
    DELETE = State()


class AddCitySG(StatesGroup):
    GET_NAME = State()
    GET_TIMEZONE = State()


class BranchSG(StatesGroup):
    LIST = State()
    NO_CITIES = State()
    EDITOR = State()
    EDIT_NAME = State()
    EDIT_ADDRESS = State()
    DELETE = State()


class AddBranchSG(StatesGroup):
    GET_CITY = State()
    GET_NAME = State()
    GET_ADDRESS = State()


class MasterSG(StatesGroup):
    LIST = State()
    NO_BRANCHES = State()
    EDITOR = State()
    EDIT_NAME = State()
    EDIT_BRANCH = State()
    EDIT_SERVICES = State()
    DELETE = State()


class MasterEditBreakTimeSG(StatesGroup):
    GET_SERVICE = State()
    GET_BREAK_TIME = State()


class MasterEditWorkTimeSG(StatesGroup):
    GET_SERVICE = State()
    GET_WORK_TIME = State()


class AddMasterSG(StatesGroup):
    GET_NAME = State()
    GET_CITY = State()


class ServiceSG(StatesGroup):
    LIST = State()
    EDITOR = State()
    EDIT_NAME = State()
    EDIT_DESCRIPTION = State()


class AddServiceSG(StatesGroup):
    GET_NAME = State()


class GeneralSettingsSG(StatesGroup):
    LIST = State()


class WorkingHoursEditorSG(StatesGroup):
    VIEW = State()
