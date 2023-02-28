from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

# Клавиатура - Список пользователей и Список должников
kb_users_list = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('Список пользователей')
b2 = KeyboardButton('Список должников')
b8 = KeyboardButton('Добавить пользователя')
kb_users_list.add(b1).insert(b2).add(b8)

# Клавиатура - Список должников
kb_debtors_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b3 = KeyboardButton('Список должников')
kb_debtors_list.insert(b3)

# Клавиатура для пополнения баланса пользователя
balance_keyboard = InlineKeyboardMarkup(row_width=3)
b4 = InlineKeyboardButton(text='100', callback_data='money*100')
b5 = InlineKeyboardButton(text='200', callback_data='money*200')
b6 = InlineKeyboardButton(text='300', callback_data='money*300')
balance_keyboard.add(b4).insert(b5).insert(b6)

# Клавиатура для ввода даты активации пользователя
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()
tomorrow = datetime.now() - timedelta(days=-1)
transfer_date_keyboard = InlineKeyboardMarkup(row_width=3)
b5 = InlineKeyboardButton(text=f'{yesterday.strftime("%d.%m.%Y")}',
                          callback_data=f'date_expiration*{yesterday.strftime("%d.%m.%Y")}')
b6 = InlineKeyboardButton(text=f'{today.strftime("%d.%m.%Y")}',
                          callback_data=f'date_expiration*{today.strftime("%d.%m.%Y")}')
b7 = InlineKeyboardButton(text=f'{tomorrow.strftime("%d.%m.%Y")}',
                          callback_data=f'date_expiration*{tomorrow.strftime("%d.%m.%Y")}')
transfer_date_keyboard.add(b5).insert(b6).insert(b7)


def create_user_keyboard(username):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Информация', callback_data=f'balance*{username}')
    button2 = InlineKeyboardButton(text='Пополнить', callback_data=f'deposit*{username}')
    button3 = InlineKeyboardButton(text='Удалить', callback_data=f'delete_this_user*{username}')
    button4 = InlineKeyboardButton(text='Назад', callback_data='back')
    return keyboard.add(button1).insert(button2).insert(button3).insert(button4)


def create_users_list_keyboard(users):
    kb_users = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for user in users:
        button = InlineKeyboardButton(text=f'{user.user_name}', callback_data=f'user*{user.user_name}')
        buttons.append(button)
    return kb_users.add(*buttons)


def create_debtors_keyboard(debtors):
    kb_debtors = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in debtors:
        button = InlineKeyboardButton(text=name, callback_data=name)
        buttons.append(button)
    return kb_debtors.add(*buttons)
