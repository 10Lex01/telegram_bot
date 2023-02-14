from aiogram import types, Dispatcher
from keyboards import create_users_keyboard
from create_bot import bot

debtors = ['Василий', 'Акакий', 'Валера', 'Виталик']



# @dp.message_handler(text='Список пользователей')
async def echo_slam(message: types.Message):
    await message.answer('Список должников:', reply_markup=create_users_keyboard(debtors))


def register_handlers_debtors(dp: Dispatcher):
    dp.register_message_handler(echo_slam, text='Список должников')
