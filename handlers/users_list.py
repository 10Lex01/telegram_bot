from aiogram import types, Dispatcher

from handlers.service import check_date
from keyboards import kb_users_list, create_users_list_keyboard, kb_cancel, create_debtors_keyboard,\
    kb_inline_user_menu, create_user_keyboard, balance_keyboard
from create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

users = ['Санек', 'Кирилл', 'Кристина', 'Леха']
debtors = ['Василий', 'Акакий', 'Вазген', 'Сэргей']


async def echo_send(message: types.Message):
    await bot.send_message(message.from_user.id, 'Сейчас узнаем кто нам задолжал!', reply_markup=kb_users_list)


async def get_user_list(message: types.Message):
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


async def get_debtors_list(message: types.Message):
    await message.answer('Список должников:', reply_markup=create_debtors_keyboard(debtors))


async def get_user_menu(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    await bot.send_message(chat_id=callback.message.chat.id, text=user, reply_markup=create_user_keyboard(user))


async def get_user_balance(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    await bot.send_message(chat_id=callback.message.chat.id, text=f'Баланс {user} = 1000')


class FSMUsers(StatesGroup):
    #user_name = State()
    balance = State()
    date_expiration = State()


# Начало
async def add_user_deposit(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    await FSMUsers.balance.set()
    await bot.send_message(chat_id=callback.message.chat.id,
                            text=f'Введите сумму пополнения для {user}:',
                            reply_markup=balance_keyboard)


async def balance_user_bottom(callback: types.CallbackQuery, state: FSMContext):
    cash = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['balance'] = cash
        await bot.send_message(chat_id=callback.message.chat.id, text=f'Баланс пополнен на {cash}')
    async with state.proxy() as data:
        await bot.send_message(text=str(data))
    await state.finish()


# Ловим данныые о балансе
async def balance_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['balance'] = message.text
        await message.answer('Баланс пополнен')
    async with state.proxy() as data:
        await message.answer(str(data))
    await state.finish()


#Ловим данные о начале использования VPN и используем полученные данные
async def date_activated_users(message: types.Message, state: FSMContext):
    if check_date(message):
        async with state.proxy() as data:
            data['date_expiration'] = message.text

        async with state.proxy() as data:
            await message.answer(str(data))

        await state.finish()
    else:
        await message.answer('Не верный формат')


#Выход из состояний
async def cancel_FSM(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('OK', reply_markup=kb_users_list)
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(echo_send, commands=['start'])
    dp.register_message_handler(get_user_list, text='Список пользователей')
    dp.register_message_handler(get_debtors_list, text='Список должнков')
    dp.register_message_handler(cancel_FSM, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(get_user_menu, lambda callback: callback.data.split('*')[0] == 'user')
    dp.register_callback_query_handler(get_user_balance, lambda callback: callback.data.split('*')[0] == 'balance')
    dp.register_callback_query_handler(add_user_deposit, lambda callback: callback.data.split('*')[0] == 'deposit')
    dp.register_message_handler(balance_user_bottom, lambda callback: callback.data.split('*')[0] == 'money')
    dp.register_message_handler(balance_user_message, state=FSMUsers.balance)
    dp.register_message_handler(date_activated_users, state=FSMUsers.date_expiration)






