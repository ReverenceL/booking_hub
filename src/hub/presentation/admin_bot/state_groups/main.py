from aiogram.fsm.state import State, StatesGroup


class AddBotSG(StatesGroup):
    GET_TOKEN = State()
    ALREADY_EXISTS = State()
    INVALID_TOKEN = State()
    SUCCESS = State()


class BotsListSG(StatesGroup):
    LIST = State()
