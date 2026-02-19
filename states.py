from aiogram.fsm.state import State, StatesGroup

class BuyFlow(StatesGroup):
    choosing_tariff = State()
    awaiting_payment = State()
