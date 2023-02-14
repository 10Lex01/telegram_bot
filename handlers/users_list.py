from aiogram import types, Dispatcher

from handlers.service import check_date
from keyboards import kb_users_list, create_users_keyboard, kb_cancel
from create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

users = ['Санек', 'Кирилл', 'Кристина', 'Леха']



#@dp.message_handler(commands=['start'])
async def echo_send(message: types.Message):
    await bot.send_message(message.from_user.id, 'Сейчас узнаем кто нам задолжал!', reply_markup=kb_users_list)

#@dp.message_handler(text='Список пользователей')
async def echo_slam(message: types.Message):
    await message.answer('Список пользователей:', reply_markup=create_users_keyboard(users))

class FSMUsers(StatesGroup):
    user_name = State()
    balance = State()
    date_acticated = State()



#Начало
async def start_FSM(callback : types.CallbackQuery, state=None):
    user = callback.data.split('_')[1]
    async with state.proxy() as data:
        data['user_name'] = user
        await FSMUsers.balance.set()
        await bot.send_message(chat_id=callback.message.chat.id, text=f'Укажите баланс {user}:', reply_markup=kb_cancel)


#Ловим данныые о балансе
async def balance_users(message : types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['balance'] = message.text
        await FSMUsers.next()
        await message.answer('Отлично! \nУкажите дату начала использования VPN (в формате ДД.ММ.ГГГГ):')

#Ловим данные о начале использования VPN и используем полученные данные
async def date_activated_users(message : types.Message, state: FSMContext):
    if check_date(message):
        async with state.proxy() as data:
            data['date_activated'] = message.text

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
    await message.answer('OK',reply_markup=kb_users_list)
    await message.delete()

def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(echo_send, commands=['start'])
    dp.register_message_handler(echo_slam, text='Список пользователей')
    dp.register_message_handler(cancel_FSM, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(start_FSM, lambda callback: callback.data.split('_')[0] == 'user')
    dp.register_message_handler(balance_users, state=FSMUsers.balance)
    dp.register_message_handler(date_activated_users, state=FSMUsers.date_acticated)






