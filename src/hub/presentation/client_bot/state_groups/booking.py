from aiogram.fsm.state import State, StatesGroup


class BookingSG(StatesGroup):
    GET_SERVICE = State()
    GET_DATE = State()
    SERVICE_DESCRIPTION = State()
    GET_TIME = State()
    SUCCESS_BOOKING = State()
