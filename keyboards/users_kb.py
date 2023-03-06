from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta

# Клавиатура - Список пользователей и Список должников
kb_main = ReplyKeyboardMarkup(resize_keyboard=True)
b1 = KeyboardButton('Список пользователей')
b2 = KeyboardButton('Список должников')
b3 = KeyboardButton('Добавить пользователя')
kb_main.add(b1).insert(b2).add(b3)

# Клавиатура - Список должников
kb_debtors_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b4 = KeyboardButton('Список должников')
kb_debtors_list.insert(b4)

# Клавиатура для пополнения баланса пользователя
balance_keyboard = InlineKeyboardMarkup(row_width=3)
b5 = InlineKeyboardButton(text='100', callback_data='money*100')
b6 = InlineKeyboardButton(text='200', callback_data='money*200')
b7 = InlineKeyboardButton(text='300', callback_data='money*300')
b_cancel_inline = InlineKeyboardButton(text='Отмена', callback_data='cancel')
balance_keyboard.add(b5).insert(b6).insert(b7).add(b_cancel_inline)

# Клавиатура для ввода даты активации пользователя
yesterday = datetime.now() - timedelta(days=1)
today = datetime.now()
tomorrow = datetime.now() - timedelta(days=-1)
transfer_date_keyboard = InlineKeyboardMarkup(row_width=3)
b9 = InlineKeyboardButton(text=f'{yesterday.strftime("%d.%m.%Y")}',
                          callback_data=f'date_expiration*{yesterday.strftime("%d.%m.%Y")}')
b10 = InlineKeyboardButton(text=f'{today.strftime("%d.%m.%Y")}',
                           callback_data=f'date_expiration*{today.strftime("%d.%m.%Y")}')
b11 = InlineKeyboardButton(text=f'{tomorrow.strftime("%d.%m.%Y")}',
                           callback_data=f'date_expiration*{tomorrow.strftime("%d.%m.%Y")}')
transfer_date_keyboard.add(b9).insert(b10).insert(b11).add(b_cancel_inline)


def create_user_keyboard(username):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Информация', callback_data=f'balance*{username}')
    button2 = InlineKeyboardButton(text='Пополнить', callback_data=f'deposit*{username}')
    button3 = InlineKeyboardButton(text='Удалить', callback_data=f'delete_this_user*{username}')
    button4 = InlineKeyboardButton(text='Назад', callback_data='back')
    button5 = InlineKeyboardButton(text='Последние операции', callback_data='last_operations')
    return keyboard.add(button1).insert(button2).insert(button5).insert(button3).add(button4)


def create_users_list_keyboard(users):
    kb_users = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for user in users:
        button = InlineKeyboardButton(text=f'{user.user_name}', callback_data=f'user*{user.user_name}')
        buttons.append(button)
    return kb_users.add(*buttons)
