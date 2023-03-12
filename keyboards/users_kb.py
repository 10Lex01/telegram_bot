from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton
from datetime import datetime, timedelta


# Клавиатура - Список пользователей и Список должников
def create_main_keyboard():
    kb_main = ReplyKeyboardMarkup(resize_keyboard=True)
    b1 = KeyboardButton('Список пользователей')
    b2 = KeyboardButton('Список должников')
    b3 = KeyboardButton('Добавить пользователя')
    kb_main.add(b1).insert(b2).add(b3)
    return kb_main


# Клавиатура для пополнения баланса пользователя
def create_balance_keyboard():
    balance_keyboard = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton(text='100', callback_data='money*100')
    b2 = InlineKeyboardButton(text='200', callback_data='money*200')
    b3 = InlineKeyboardButton(text='300', callback_data='money*300')
    b_cancel_balance_inline = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    balance_keyboard.add(b1).insert(b2).insert(b3).add(b_cancel_balance_inline)
    return balance_keyboard


# Клавиатура для ввода даты активации пользователя
def create_transfer_date_keyboard():
    yesterday = datetime.now() - timedelta(days=1)
    today = datetime.now()
    tomorrow = datetime.now() - timedelta(days=-1)
    transfer_date_keyboard = InlineKeyboardMarkup(row_width=3)
    b1 = InlineKeyboardButton(text=f'{yesterday.strftime("%d.%m.%Y")}',
                              callback_data=f'date_expiration*{yesterday.strftime("%d.%m.%Y")}')
    b2 = InlineKeyboardButton(text=f'{today.strftime("%d.%m.%Y")}',
                              callback_data=f'date_expiration*{today.strftime("%d.%m.%Y")}')
    b3 = InlineKeyboardButton(text=f'{tomorrow.strftime("%d.%m.%Y")}',
                              callback_data=f'date_expiration*{tomorrow.strftime("%d.%m.%Y")}')
    b_cancel_date_inline = InlineKeyboardButton(text='Отмена', callback_data='cancel')
    transfer_date_keyboard.add(b1).insert(b2).insert(b3).add(b_cancel_date_inline)
    return transfer_date_keyboard


def create_user_keyboard(username):
    keyboard = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Информация', callback_data=f'balance*{username}')
    button2 = InlineKeyboardButton(text='Пополнить', callback_data=f'deposit*{username}')
    button3 = InlineKeyboardButton(text='Удалить', callback_data=f'delete_this_user*{username}')
    button4 = InlineKeyboardButton(text='Назад', callback_data='back')
    button5 = InlineKeyboardButton(text='Последние операции', callback_data=f'last_operations*{username}')
    return keyboard.add(button1).insert(button2).insert(button5).insert(button3).add(button4)


def create_users_list_keyboard(users):
    kb_users = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for user in users:
        button = InlineKeyboardButton(text=f'{user.user_name}', callback_data=f'user*{user.user_name}')
        buttons.append(button)
    return kb_users.add(*buttons)


def confirm_delete_user_keyboards(username):
    confirm_delete_kb = InlineKeyboardMarkup(row_width=2)
    button1 = InlineKeyboardButton(text='Да', callback_data=f'yes*{username}')
    button2 = InlineKeyboardButton(text='Нет', callback_data=f'no*{username}')
    confirm_delete_kb.add(button1).insert(button2)
    return confirm_delete_kb
