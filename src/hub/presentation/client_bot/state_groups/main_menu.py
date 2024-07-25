from aiogram.fsm.state import State, StatesGroup


class RegistrationSG(StatesGroup):
    GET_CITY = State()


class MainMenuSG(StatesGroup):
    MENU = State()
