from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton


kb_users_list = ReplyKeyboardMarkup(resize_keyboard=True)
b5 = KeyboardButton('Список пользователей')
b6 = KeyboardButton('Список должников')
kb_users_list.add(b5).insert(b6)

kb_cancel = ReplyKeyboardMarkup(resize_keyboard=True)
b7 = KeyboardButton('Отмена')
kb_cancel.add(b7)

def create_users_keyboard(users):
    kb_users = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in users:
        button = InlineKeyboardButton(text=name, callback_data=f'user_{name}')
        buttons.append(button)
    return kb_users.add(*buttons)




