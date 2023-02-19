from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


# Клавиатура - Список пользователей и Список должников
kb_users_list = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('Список пользователей')
b2 = KeyboardButton('Список должников')
kb_users_list.add(b1).insert(b2)

# Клавиатура - Список должников
kb_debtors_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b3 = KeyboardButton('Список должников')
kb_debtors_list.insert(b3)

# Клавиатура для пополнения баланса пользователя
balance_keyboard = InlineKeyboardMarkup(row_width=3)
b4 = InlineKeyboardButton(text='100', callback_data='money*100')
b5 = InlineKeyboardButton(text='300', callback_data='money*300')
b6 = InlineKeyboardButton(text='500', callback_data='money*500')
balance_keyboard.add(b4).insert(b5).insert(b6)


def create_user_keyboard(user):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Баланс', callback_data=f'balance*{user}')
    button2 = InlineKeyboardButton(text='Пополнить', callback_data=f'deposit*{user}')
    return keyboard.add(button1).insert(button2)


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
