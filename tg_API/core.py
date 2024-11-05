import telebot
from config import BOT_TOKEN, LIMIT_ITEMS
from typing import Dict, List, Optional
from telebot import types, custom_filters
from telebot.storage import StateMemoryStorage
from site_API.core import APIResponse
from database.core import User, Record, pw
from tg_API.states import MyStates

state_storage = StateMemoryStorage()

bot = telebot.TeleBot(BOT_TOKEN, state_storage=state_storage)


def create_start_buttons() -> types:
    """ Создание кнопок для ввода команд """
    markup = types.ReplyKeyboardMarkup(resize_keyboard=True, row_width=3)
    markup.add(types.KeyboardButton('/low'),
               types.KeyboardButton('/high'),
               types.KeyboardButton('/custom'),
               types.KeyboardButton('/history'),
               types.KeyboardButton('/help'))
    return markup


def check_register(message: types) -> Optional[User]:
    """ Проверка регистрации пользователя """
    user = User.get_or_none(User.user_id == message.from_user.id)
    if user is None:
        bot.send_message(message.chat.id, 'Вы не зарегистрированы. Напишите /start')
        return None
    return user


def api_search(req: Dict, limit: int, message: types) -> None:
    """
    Функция для работы с API сайта и вывода результатов

    Args:
         req (Dict): url сайта
         limit (int): предельное количество товаров для выдачи
         message (types): объект, содержащий в себе информацию о сообщении

    Attributes:
         message.chat.id (int): идентификатор чата
         message.from.id (int): идентификатор пользователя
         message.text (str): текст сообщения
    """
    api = APIResponse(querystring=req)
    items = api.get_items()
    if not items['status']:
        bot.send_message(message.chat.id, '<b>Ошибка сервера:</b> {0}'.format(items['error']),
                         parse_mode="html", reply_markup=create_start_buttons())
    elif len(items['item_list']) > 0:
        for number, item in enumerate(items['item_list']):
            if number < limit:
                bot.send_photo(message.chat.id, item['image'],
                               caption="{title}.\nЦена: <b>{price}</b>\n<a href=\"{url}\">Перейти на сайт</a>".
                               format(title=item['title'], url=item['url'], price=item['price']), parse_mode="html")
            else:
                break
        bot.send_message(message.chat.id, '<b>Поиск завершен.</b> Начнём заново?', parse_mode="html",
                         reply_markup=create_start_buttons())
    else:
        bot.send_message(message.chat.id,
                         "<b>К сожалению по вашему запросу ничего найти не удалось.</b>\nНачнём новый поиск?",
                         parse_mode="html", reply_markup=create_start_buttons())


@bot.message_handler(state="*", commands=['start'])
def start_command(message: types) -> None:
    """ Стартовое меню с кнопками команд """
    try:
        User.create(user_id=message.from_user.id)
        bot.send_message(message.chat.id, 'Я - бот по поиску товаров в Google Покупки. '
                                          'Чтобы начать поиск, введите одну из предложенных команд. '
                                          'Нажмите /help для получения справочной информации',
                         reply_markup=create_start_buttons())
    except pw.IntegrityError:
        bot.send_message(message.chat.id, f"Рад вас снова видеть! Начнём поиск?",
                         reply_markup=create_start_buttons())
    bot.set_state(message.from_user.id, MyStates.start, message.chat.id)


@bot.message_handler(state="*", commands=['hello', 'hello-world'])
def hi_command(message) -> None:
    bot.send_message(message.chat.id, 'Привет! Я - бот по поиску товаров в Google Покупки')


@bot.message_handler(state="*", commands=['help'])
def help_command(message: types) -> None:
    """ Реализация команды /help """
    bot.send_message(message.chat.id, "Я - бот по поиску товаров в Google Покупки.\n\n"
                                      "<b>Список команд</b>, которые я понимаю:"
                                      "\n<b>/low</b> - поиск товаров с самой низкой ценой"
                                      "\n<b>/high</b> - поиск товаров с самой высокой ценой"
                                      "\n<b>/custom</b> - поиск товаров в заданном ценовом диапазоне"
                                      "\n<b>/history</b> - вывод истории запросов"
                                      "\n<b>/help</b> - вывод информации о работе бота"
                                      "\n<b>/start</b> - запуск / перезапуск телеграм-бота"
                                      "\n<b>/hello-world</b> - приветствие", parse_mode="html")


@bot.message_handler(state="*", commands=['low'])
def low_command(message: types) -> None:
    """ Запуск команды /low, ожидаем ввода названия товара для поиска """
    if check_register(message):
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Напишите название товара для поиска',
                         reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.low_item, message.chat.id)


@bot.message_handler(state="*", commands=['high'])
def high_command(message: types) -> None:
    """ Запуск команды /high, ожидаем ввода названия товара для поиска """
    if check_register(message):
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Напишите название товара для поиска',
                         reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.high_item, message.chat.id)


@bot.message_handler(state="*", commands=['custom'])
def custom_command(message: types) -> None:
    """ Запуск команды /custom, ожидаем ввода названия товара для поиска """
    if check_register(message):
        markup = types.ReplyKeyboardRemove()
        bot.send_message(message.chat.id, 'Напишите название товара для поиска',
                         reply_markup=markup)
        bot.set_state(message.from_user.id, MyStates.custom_item, message.chat.id)


@bot.message_handler(state="*", commands=['history'])
def history_command(message: types) -> None:
    """ Реализация команды /history """
    user = check_register(message)
    if user:
        history: List[Record] = user.history.order_by(-Record.record_id).limit(10)
        result = []
        result.extend(map(str, reversed(history)))

        if not result:
            bot.send_message(message.chat.id, 'Вы еще ничего не искали')
            return
        bot.send_message(message.chat.id, "История Вашего поиска (не более 10 последних команд):\n" + "\n".join(result))


@bot.message_handler(state=MyStates.low_item)
def low_item_state(message: types) -> None:
    """
        Статус low_item команды /low:
        на вход получаем название товара для поиска и переходим в статус low_count
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        bot.send_message(message.chat.id,
                         f"Можем найти от 1 до {LIMIT_ITEMS} дешевых товаров: <b>{message.text}</b>.\n"
                         f"Напишите количество для вывода", parse_mode="html")
        data['search_item'] = message.text
        bot.set_state(message.from_user.id, MyStates.low_count, message.chat.id)


@bot.message_handler(state=MyStates.low_count)
def low_count_state(message: types) -> None:
    """
        Статус low_count команды /low:
        на вход получаем количество товаров для выдачи, реализуем выдачу и переходим в стартовое меню
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            if 0 < int(message.text) <= LIMIT_ITEMS:
                new_record = Record(user_id=message.from_user.id, command='/low', item=data['search_item'],
                                    count=message.text)
                new_record.save()
                api_search({'q': data['search_item'], 'language': 'ru', 'sort_by': 'LOWEST_PRICE'},
                           int(message.text), message)
            else:
                bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите число от 1 до {LIMIT_ITEMS}',
                                 parse_mode="html")
        except (TypeError, ValueError):
            bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите целое число',
                             parse_mode="html")
        bot.set_state(message.from_user.id, MyStates.start, message.chat.id)


@bot.message_handler(state=MyStates.high_item)
def high_item_state(message: types) -> None:
    """
        Статус high_item команды /high:
        на вход получаем название товара для поиска и переходим в статус high_count
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        bot.send_message(message.chat.id,
                         f"Можем найти от 1 до {LIMIT_ITEMS} дорогих товаров: <b>{message.text}</b>.\n"
                         f"Напишите количество для вывода", parse_mode="html")
        data['search_item'] = message.text
        bot.set_state(message.from_user.id, MyStates.high_count, message.chat.id)


@bot.message_handler(state=MyStates.high_count)
def high_count_state(message: types) -> None:
    """
        Статус high_count команды /high:
        на вход получаем количество товаров для выдачи, реализуем выдачу и переходим в стартовое меню
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            if 0 < int(message.text) <= LIMIT_ITEMS:
                new_record = Record(user_id=message.from_user.id, command='/high', item=data['search_item'],
                                    count=message.text)
                new_record.save()
                api_search({'q': data['search_item'], 'language': 'ru', 'sort_by': 'HIGHEST_PRICE'},
                           int(message.text), message)
            else:
                bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите число от 1 до {LIMIT_ITEMS}',
                                 parse_mode="html")
        except TypeError:
            bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите целое число',
                             parse_mode="html")
        bot.set_state(message.from_user.id, MyStates.start, message.chat.id)


@bot.message_handler(state=MyStates.custom_item)
def high_item_state(message: types) -> None:
    """
        Статус custom_item команды /custom:
        на вход получаем название товара для поиска и переходим в статус custom_range
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        bot.send_message(message.chat.id, 'Напишите ценовой диапазон поиска, например: 100-200. ')
        data['search_item'] = message.text
        data['record'] = {'user_id': message.from_user.id, 'command': '/custom', 'item': message.text}
        bot.set_state(message.from_user.id, MyStates.custom_range, message.chat.id)


@bot.message_handler(state=MyStates.custom_range)
def high_item_state(message: types) -> None:
    """
        Статус custom_range команды /custom:
        на вход получаем диапазон цен в формате X-Y и переходим в статус custom_count
    """
    try:
        price_range = message.text.split('-')
        if len(price_range) != 2:
            raise IndexError
        elif (int(price_range[0]) <= 0) or (int(price_range[0]) >= int(price_range[1])):
            raise ValueError

        with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
            bot.send_message(message.chat.id, "Можем найти от 1 до {limit} товаров: <b>{item}</b> "
                                              "в ценовом диапазоне {range}.\nНапишите количество для вывода"
                             .format(limit=LIMIT_ITEMS, item=data['search_item'], range=message.text),
                             parse_mode="html")
            data['price_range'] = {'min': int(price_range[0]), 'max': int(price_range[1])}
            data['record']['range'] = message.text
            bot.set_state(message.from_user.id, MyStates.custom_count, message.chat.id)

    except IndexError:
        bot.send_message(message.chat.id, '<b>Ошибка!</b> Ожидается ввод двух чисел, например: 100-200. ',
                         parse_mode="html")
    except ValueError:
        bot.send_message(message.chat.id, "<b>Ошибка!</b> Первое число должно быть больше нуля и меньше второго.\n"
                                          "Введите корректный диапазон цены! ",
                         parse_mode="html")


@bot.message_handler(state=MyStates.custom_count)
def high_count_state(message: types) -> None:
    """
        Статус custom_count команды /custom:
        на вход получаем количество товаров для выдачи, реализуем выдачу и переходим в стартовое меню
    """
    with bot.retrieve_data(message.from_user.id, message.chat.id) as data:
        try:
            if 0 < int(message.text) <= LIMIT_ITEMS:
                new_record = Record(user_id=message.from_user.id, command='/custom', item=data['search_item'],
                                    range='{0}-{1}'.format(data['price_range']['min'], data['price_range']['max']),
                                    count=message.text)
                new_record.save()
                api_search({'q': data['search_item'], 'language': 'ru', 'sort_by': 'LOWEST_PRICE',
                            'min_price': data['price_range']['min'], 'max_price': data['price_range']['max']},
                           int(message.text), message)
            else:
                bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите число от 1 до {LIMIT_ITEMS}',
                                 parse_mode="html")
        except TypeError:
            bot.send_message(message.chat.id, f'<b>Ошибка!</b> Напишите целое число',
                             parse_mode="html")
        bot.set_state(message.from_user.id, MyStates.start, message.chat.id)


@bot.message_handler(content_types=['text'])
def text_msg(message: types) -> None:
    """ Обработчик неизвестных сообщений и команд """
    if message.text.lower() == 'привет':
        bot.send_message(message.chat.id, 'Я - бот по поиску товаров в Google Покупки')
    else:
        bot.send_message(message.chat.id, 'Я вас не понял. Нажмите <b>/help</b> для получения справочной информации',
                         parse_mode="html")


bot.add_custom_filter(custom_filters.StateFilter(bot))
