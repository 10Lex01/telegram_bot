from datetime import datetime

from aiogram import types, Dispatcher

from database.services import add_to_database
from handlers.service import check_date
from keyboards import kb_users_list, create_users_list_keyboard, create_debtors_keyboard,\
     create_user_keyboard, balance_keyboard, transfer_date_keyboard
from create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup
from aiogram.dispatcher.filters import Text


users = ['Санек', 'Кирилл', 'Кристина', 'Леха']
debtors = ['Василий', 'Акакий', 'Вазген', 'Сэргей']


async def start_bot(message: types.Message):
    """Запуск бота"""
    await bot.send_message(message.from_user.id, 'Сейчас узнаем кто нам задолжал!', reply_markup=kb_users_list)


async def get_user_list(message: types.Message):
    """Открывает клавиатуру списка пользователей"""
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


async def get_debtors_list(message: types.Message):
    """Открывает клавиатуру списка должноков"""
    await message.answer('Список должников:', reply_markup=create_debtors_keyboard(debtors))


async def get_user_menu(callback: types.CallbackQuery):
    """Открывает меню пользователя"""
    user = callback.data.split('*')[1]
    await bot.send_message(chat_id=callback.message.chat.id, text=user, reply_markup=create_user_keyboard(user))


async def get_user_balance(callback: types.CallbackQuery):
    """Inline клавиатура "Баланс" для пользователя"""
    user = callback.data.split('*')[1]
    await bot.send_message(chat_id=callback.message.chat.id, text=f'Баланс {user} = 1000')


class FSMUsers(StatesGroup):
    balance = State()
    transfer_date = State()


async def add_user_name(callback: types.CallbackQuery, state=None):
    """Начало FSM. Добавление имени пользователя в БД. Вывод Inline клавиатуры для пополнения баланса"""
    user = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['user_name'] = user
        await FSMUsers.balance.set()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f'Введите сумму пополнения для {user}:',
                               reply_markup=balance_keyboard)


async def add_user_deposit_button(callback: types.CallbackQuery, state: FSMContext):
    """Ввод данных о поплнении баланса через Inline клавиатуру"""
    cash = callback.data.split('*')[1]
    async with state.proxy() as data:
        user = data['user_name']
        data['balance'] = cash
        await FSMUsers.next()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f'Баланс {user} пополнен на {cash}\nВведите дату пополнения',
                               reply_markup=transfer_date_keyboard)


async def balance_user_message(message: types.Message, state: FSMContext):
    """Ввод данных о пополнении баланса через сообщение"""
    async with state.proxy() as data:
        user = data['user_name']
        data['balance'] = message.text
        await FSMUsers.next()
        await message.answer(f'Баланс {user} пополнен на {message.text}\nВведите дату пополнения',
                             reply_markup=transfer_date_keyboard)


async def transfer_date_user_button(callback: types.CallbackQuery, state: FSMContext):
    """Ввод даты перевода за использование VPN через Inline клавиатуру, выход из FSM"""
    user_transfer_date = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['transfer_date'] = user_transfer_date
    async with state.proxy() as data:
        await bot.send_message(chat_id=callback.message.chat.id, text=f'{str(data)}')
    await state.finish()


async def transfer_date_user_message(message: types.Message, state: FSMContext):
    """Ввод даты перевода за использование VPN через сообщение, выход из FSM"""
    if check_date(message):
        async with state.proxy() as data:
            data['transfer_date'] = message.text
            await message.answer('Данные успешно добавлены', reply_markup=kb_users_list)
            await message.answer(str(data))

        await state.finish()
    else:
        await message.answer('Не верный формат')


async def cancel_fsm(message: types.Message, state: FSMContext):
    """Выход из FSM при отправке сообщения 'отмена'"""
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await message.answer('OK', reply_markup=kb_users_list)
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


class FSMAddUser(StatesGroup):
    user_name = State()
    balance = State()
    date_expiration = State()
    description = State()


async def start_FSM_add_user(message: types.Message):
    """Добавление нового пользователя"""
    await FSMAddUser.user_name.set()
    await message.answer('Введите имя пользователя')


async def add_new_user_name(message: types.Message, state: FSMContext):
    """Отлавливаем имя пользователя, запрашиваем баланс"""
    async with state.proxy() as data:
        data['user_name'] = message.text
    await FSMAddUser.balance.set()
    await message.answer('Введите стартовый баланс', reply_markup=balance_keyboard)


async def add_start_user_balance_button(callback: types.CallbackQuery, state: FSMContext):
    """Отлавливаем баланс, запрашиваем дату истечения срока оплаты"""
    balance = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['balance'] = int(balance)
    await FSMAddUser.date_expiration.set()
    await bot.send_message(chat_id=callback.message.chat.id, text='Введите дату истечения срока оплаты',
                           reply_markup=transfer_date_keyboard)


async def add_start_user_balance_message(message: types.Message, state: FSMContext):
    """Отлавливаем баланс, запрашиваем дату истечения срока оплаты"""
    async with state.proxy() as data:
        try:
            data['balance'] = int(message.text)
        except ValueError:
            await message.reply('Введите число')
            return
    await FSMAddUser.date_expiration.set()
    await message.answer('Введите дату истечения срока оплаты')


async def add_date_expiration_button(callback: types.CallbackQuery, state: FSMContext):
    """Отлавливаем дату истечения срока оплаты"""
    date_expiration = callback.data.split('*')[1]
    async with state.proxy() as data:
        formated_date = datetime.strptime(date_expiration, "%d.%m.%Y").date()
        data['date_expiration'] = formated_date
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='Введите примечание для пользователя', reply_markup=kb_users_list)
    await FSMAddUser.description.set()


async def add_date_expiration_message(message: types.Message, state: FSMContext):
    """Отлавливаем дату истечения срока оплаты"""
    if check_date(message):
        async with state.proxy() as data:
            try:
                formated_date = datetime.strptime(message.text, "%d.%m.%Y").date()
                data['date_expiration'] = formated_date
            except ValueError:
                await message.reply('Введите дату в формате: ДД.ММ.ГГГГ')
            await message.answer('Введите примечание для пользователя', reply_markup=kb_users_list)
        await FSMAddUser.description.set()
    else:
        await message.reply('Не верный формат\nВведите дату в формате: ДД.ММ.ГГГГ')


async def add_description(message: types.Message, state: FSMContext):
    """Отлавливаем примечание"""
    async with state.proxy() as data:
        data['description'] = message.text
        add_to_database(data)
        await message.answer('Данные успешно добавлены', reply_markup=kb_users_list)
    await state.finish()

def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_bot, commands=['start'])
    dp.register_message_handler(get_user_list, text='Список пользователей')
    dp.register_message_handler(get_debtors_list, text='Список должнков')
    dp.register_message_handler(cancel_fsm, Text(equals='отмена', ignore_case=True), state="*")
    dp.register_callback_query_handler(get_user_menu, lambda callback: callback.data.split('*')[0] == 'user')
    dp.register_callback_query_handler(get_user_balance, lambda callback: callback.data.split('*')[0] == 'balance')
    dp.register_callback_query_handler(add_new_user_name, lambda callback: callback.data.split('*')[0] == 'deposit',
                                       state=None)
    dp.register_callback_query_handler(add_user_deposit_button,
                                       lambda callback: callback.data.split('*')[0] == 'money',
                                       state=FSMUsers.balance)
    dp.register_message_handler(balance_user_message, state=FSMUsers.balance)
    dp.register_callback_query_handler(transfer_date_user_button,
                                       lambda callback: callback.data.split('*')[0] == 'date_expiration',
                                       state=FSMUsers.transfer_date)
    dp.register_message_handler(transfer_date_user_message, state=FSMUsers.transfer_date)

    dp.register_message_handler(start_FSM_add_user, text='Добавить пользователя')
    dp.register_message_handler(add_new_user_name, state=FSMAddUser.user_name)
    dp.register_callback_query_handler(add_start_user_balance_button,
                                       lambda callback: callback.data.split('*')[0] == 'money',
                                       state=FSMAddUser.balance)
    dp.register_message_handler(add_start_user_balance_message, state=FSMAddUser.balance)
    dp.register_callback_query_handler(add_date_expiration_button,
                                       lambda callback: callback.data.split('*')[0] == 'date_expiration',
                                       state=FSMAddUser.date_expiration)
    dp.register_message_handler(add_date_expiration_message, state=FSMAddUser.date_expiration)
    dp.register_message_handler(add_description, state=FSMAddUser.description)
