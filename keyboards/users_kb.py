from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


kb_users_list = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('Список пользователей')
b2 = KeyboardButton('Список должников')
kb_users_list.add(b1).insert(b2)

kb_debtors_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b3 = KeyboardButton('Список должников')
kb_debtors_list.insert(b3)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
b4 = KeyboardButton('Отмена')
kb_cancel.add(b4)

kb_inline_user_menu = InlineKeyboardMarkup()
b5 = InlineKeyboardButton(text='Баланс', callback_data='balance')
b6 = InlineKeyboardButton(text='Пополнить', callback_data='deposit')
kb_inline_user_menu.add(b5).insert(b6)

# Клавиатура для пополнения баланса
balance_keyboard = InlineKeyboardMarkup(row_width=3)
b7 = InlineKeyboardButton(text='100', callback_data='money*100')
b8 = InlineKeyboardButton(text='300', callback_data='money*300')
b9 = InlineKeyboardButton(text='500', callback_data='money*500')
balance_keyboard.add(b7).insert(b8).insert(b9)


def create_user_keyboard(user):
    keyboard = InlineKeyboardMarkup(row_width=2)
    b1 = InlineKeyboardButton(text='Баланс', callback_data=f'balance*{user}')
    b2 = InlineKeyboardButton(text='Пополнить', callback_data=f'deposit*{user}')
    return keyboard.add(b1).insert(b2)


def create_users_list_keyboard(users):
    kb_users = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in users:
        button = InlineKeyboardButton(text=name, callback_data=f'user*{name}')
        buttons.append(button)
    return kb_users.add(*buttons)


def create_debtors_keyboard(debtors):
    kb_debtors = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in debtors:
        button = InlineKeyboardButton(text=name, callback_data=name)
        buttons.append(button)
    return kb_debtors.add(*buttons)



