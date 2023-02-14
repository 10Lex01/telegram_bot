from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, ReplyKeyboardMarkup, KeyboardButton

kb_debtors_list = ReplyKeyboardMarkup(resize_keyboard=True, one_time_keyboard=True)
b6 = KeyboardButton('Список должников')
kb_debtors_list.insert(b6)

def create_debtors_keyboard(debtors):
    kb_debtors = InlineKeyboardMarkup(row_width=2)
    buttons = []
    for name in debtors:
        button = InlineKeyboardButton(text=name, callback_data=name)
        buttons.append(button)
    return kb_debtors.add(*buttons)