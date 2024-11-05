from telebot.handler_backends import State, StatesGroup


class MyStates(StatesGroup):
    start = State()         # основное состояние (стартовое меню)
    low_item = State()      # реализация команды /low - состояние ввода наименования товара
    low_count = State()     # реализация команды /low - состояние ввода количеств
    high_item = State()     # реализация команды /high - состояние ввода наименования товара
    high_count = State()    # реализация команды /high - состояние ввода количеств
    custom_item = State()   # реализация команды /custom - состояние ввода наименования товара
    custom_range = State()  # реализация команды /custom - состояние ввода диапазона цены
    custom_count = State()  # реализация команды /custom - состояние ввода количеств