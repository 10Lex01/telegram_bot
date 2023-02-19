from aiogram import types, Dispatcher

from handlers.service import check_date
from keyboards import kb_users_list, create_users_list_keyboard, create_debtors_keyboard,\
     create_user_keyboard, balance_keyboard
from create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text

users = ['Санек', 'Кирилл', 'Кристина', 'Леха']
debtors = ['Василий', 'Акакий', 'Вазген', 'Сэргей']


async def start_bot(message: types.Message):
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
    user_name = State()
    balance = State()
    date_expiration = State()


async def add_user_name(callback: types.CallbackQuery, state=None):
    print(callback)
    user = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['user_name'] = user
        await FSMUsers.user_name.set()


async def add_user_deposit_message(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    await FSMUsers.next()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f'Введите сумму пополнения для {user}:',
                           reply_markup=balance_keyboard)


async def add_user_deposit_button(callback: types.CallbackQuery, state: FSMContext):
    cash = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['balance'] = cash
        await FSMUsers.next()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f'Баланс пополнен на {cash}\nВведите дату окончания использования VPN')


async def balance_user_message(message: types.Message, state: FSMContext):
    async with state.proxy() as data:
        data['balance'] = message.text
        await FSMUsers.next()
        await message.answer(f'Баланс пополнен на {message.text}\nВведите дату окончания использования VPN')


async def date_expiration_users(message: types.Message, state: FSMContext):
    if check_date(message):
        async with state.proxy() as data:
            data['date_expiration'] = message.text
            await message.answer('Данные успешно добавлены', reply_markup=kb_users_list)
        async with state.proxy() as data:
            await message.answer(str(data))

        await state.finish()
    else:
        await message.answer('Не верный формат')


async def cancel_fsm(message: types.Message, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('OK', reply_markup=kb_users_list)
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


def register_handlers_users(dp: Dispatcher):
    # Запуск бота
    dp.register_message_handler(start_bot, commands=['start'])
    # Открывает клавиатуру списка пользователей
    dp.register_message_handler(get_user_list, text='Список пользователей')
    # Открывает клавиатуру списка должноков
    dp.register_message_handler(get_debtors_list, text='Список должнков')
    # Выход из FSM при отправке сообщения "отмена"
    dp.register_message_handler(cancel_fsm, Text(equals='отмена', ignore_case=True), state="*")
    # Открывает меню пользователя
    dp.register_callback_query_handler(get_user_menu, lambda callback: callback.data.split('*')[0] == 'user')
    # Inline клавиатура "Баланс" для пользователя
    dp.register_callback_query_handler(get_user_balance, lambda callback: callback.data.split('*')[0] == 'balance')
    # !!!!!!НЕ РАБОТАЕТ!!!!!! Добавление имени пользователя в БД, начало FSM
    dp.register_callback_query_handler(add_user_name, lambda callback: callback.data.split('*')[0] == 'user')
    # Inline клавиатура 'Пополнить' для пользователя
    dp.register_callback_query_handler(add_user_deposit_message,
                                       lambda callback: callback.data.split('*')[0] == 'deposit')
    # Ввод данный о поплнении баланса через Inline клавиатуру
    dp.register_callback_query_handler(add_user_deposit_button,
                                       lambda callback: callback.data.split('*')[0] == 'money',
                                       state=FSMUsers.user_name)
    # Ввод данных о пополнении баланса через сообщение
    dp.register_message_handler(balance_user_message, state=FSMUsers.user_name)
    # Ввод даты окончания использования VPN, выход из FSM
    dp.register_message_handler(date_expiration_users, state=FSMUsers.balance)
