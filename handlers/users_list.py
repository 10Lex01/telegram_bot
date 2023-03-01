from datetime import datetime
from aiogram import types, Dispatcher
from database.services import add_to_database, get_all_users_from_db, get_user_balance_from_db, \
    update_balance_and_date_for_user, delete_user_from_db
from handlers.service import check_date, calculate_expiration_date
from keyboards import kb_users_list, create_users_list_keyboard, create_debtors_keyboard,\
     create_user_keyboard, balance_keyboard, transfer_date_keyboard
from create_bot import bot
from aiogram.dispatcher import FSMContext
from aiogram.dispatcher.filters.state import State, StatesGroup



async def start_bot(message: types.Message):
    """Запуск бота"""
    await bot.send_message(message.from_user.id, 'Сейчас узнаем кто нам задолжал!', reply_markup=kb_users_list)


async def get_user_list(message: types.Message):
    """Открывает клавиатуру списка пользователей"""
    users = get_all_users_from_db()
    await message.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


async def get_debtors_list(message: types.Message):
    """Открывает клавиатуру списка должников"""
    users = get_all_users_from_db()
    await message.answer('Список должников:', reply_markup=create_debtors_keyboard(users))


async def get_user_menu(callback: types.CallbackQuery):
    """Открывает меню пользователя"""
    user_name = callback.data.split('*')[1]
    user = get_user_balance_from_db(user_name)
    message_text = f'{user.user_name}'
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=message_text, reply_markup=create_user_keyboard(user.user_name))


async def get_user_balance(callback: types.CallbackQuery):
    """Inline клавиатура "Баланс" для пользователя"""
    user_name = callback.data.split('*')[1]
    user = get_user_balance_from_db(user_name)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f'Пользователь: {user.user_name}\n'
                                f'Баланс: {user.balance} ₽\n'
                                f'Дата истечения срока: {user.date_expiration.strftime("%d.%m.%Y")}\n'
                                f'*{user.description}',
                           reply_markup=create_user_keyboard(user.user_name))


class FSMUsers(StatesGroup):
    balance = State()
    transfer_date = State()


async def update_user_balance(callback: types.CallbackQuery, state=None):
    """Начало FSM. Вывод Inline клавиатуры для пополнения баланса"""
    user = callback.data.split('*')[1]
    async with state.proxy() as data:
        data['user_name'] = user
        await FSMUsers.balance.set()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f'Введите сумму пополнения для {user}:',
                               reply_markup=balance_keyboard)


async def add_user_deposit(request: types.CallbackQuery | types.Message, state: FSMContext):
    """Ввод данных о пополнении баланса через Inline клавиатуру"""
    if type(request) == types.CallbackQuery:
        cash = request.data.split('*')[1]
        async with state.proxy() as data:
            user = data['user_name']
            data['balance'] = cash
            await FSMUsers.next()
            await bot.send_message(chat_id=request.message.chat.id,
                                   text=f'Баланс {user} пополнен на {cash}\nВведите дату пополнения счета',
                                   reply_markup=transfer_date_keyboard)
    else:
        async with state.proxy() as data:
            user = data['user_name']
            data['balance'] = request.text
            await FSMUsers.next()
            await request.answer(f'Баланс {user} пополнен на {request.text}\nВведите дату пополнения счета',
                                 reply_markup=transfer_date_keyboard)


async def transfer_date_user(request: types.CallbackQuery | types.Message, state: FSMContext):
    """Ввод даты перевода за использование VPN через Inline клавиатуру, выход из FSM"""
    if type(request) == types.CallbackQuery:
        user_transfer_date = request.data.split('*')[1]
        async with state.proxy() as data:
            data['transfer_date'] = user_transfer_date
            update_balance_and_date_for_user(data['user_name'], data['balance'])
            await bot.send_message(chat_id=request.message.chat.id,
                                   text=f'Баланс успешно пополнен',
                                   reply_markup=kb_users_list)
            await state.finish()
    else:
        if check_date(request):
            async with state.proxy() as data:
                data['transfer_date'] = request.text
                update_balance_and_date_for_user(data['user_name'], data['balance'])
                await request.answer('Данные успешно добавлены', reply_markup=kb_users_list)
            await state.finish()
        else:
            await request.answer('Не верный формат')


class FSMAddUser(StatesGroup):
    user_name = State()
    balance = State()
    date_expiration = State()
    description = State()


async def start_fsm_add_user(message: types.Message):
    """Добавление нового пользователя"""
    await FSMAddUser.user_name.set()
    await message.answer('Введите имя пользователя')


async def add_new_user_name(message: types.Message, state: FSMContext):
    """Отлавливаем имя пользователя, запрашиваем баланс"""
    async with state.proxy() as data:
        data['user_name'] = message.text
    await FSMAddUser.balance.set()
    await message.answer('Введите стартовый баланс', reply_markup=balance_keyboard)


async def add_start_user_balance(request: types.CallbackQuery | types.Message, state: FSMContext):
    """Отлавливаем баланс, запрашиваем дату истечения срока оплаты"""
    if type(request) == types.CallbackQuery:
        balance = request.data.split('*')[1]
        async with state.proxy() as data:
            data['balance'] = int(balance)
        await FSMAddUser.date_expiration.set()
        await bot.send_message(chat_id=request.message.chat.id, text='Введите дату пополнения счета',
                               reply_markup=transfer_date_keyboard)
    else:
        async with state.proxy() as data:
            try:
                data['balance'] = int(request.text)
            except ValueError:
                await request.reply('Введите число')
                return
        await FSMAddUser.date_expiration.set()
        await request.answer('Введите дату пополнения счета', reply_markup=transfer_date_keyboard)


async def add_date_expiration(request: types.CallbackQuery | types.Message, state: FSMContext) -> None:
    """Отлавливаем дату истечения срока оплаты"""
    if type(request) == types.CallbackQuery:
        date_expiration = request.data.split('*')[1]
        async with state.proxy() as data:
            # formated_date = datetime.strptime(date_expiration, "%d.%m.%Y").date()
            data['date_expiration'] = calculate_expiration_date(date_expiration, data['balance'])
            await bot.send_message(chat_id=request.message.chat.id,
                                   text='Введите примечание для пользователя', reply_markup=kb_users_list)
        await FSMAddUser.description.set()
    else:
        if check_date(request):
            async with state.proxy() as data:
                try:
                    # formated_date = datetime.strptime(request.text, "%d.%m.%Y").date()
                    data['date_expiration'] = calculate_expiration_date(request.text, data['balance'])
                except ValueError:
                    await request.reply('Введите дату в формате: ДД.ММ.ГГГГ')
                    return
                await request.answer('Введите примечание для пользователя', reply_markup=kb_users_list)
            await FSMAddUser.description.set()
        else:
            await request.reply('Не верный формат\nВведите дату в формате: ДД.ММ.ГГГГ')


async def add_description(message: types.Message, state: FSMContext):
    """Отлавливаем примечание"""
    async with state.proxy() as data:
        data['description'] = message.text
        add_to_database(data)
        await message.answer('Данные успешно добавлены', reply_markup=kb_users_list)
    await state.finish()


async def back_function_for_user(callback: types.CallbackQuery):
    """Выход из FSM при отправке сообщения 'отмена'"""
    users = get_all_users_from_db()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Список пользователей:',
                           reply_markup=create_users_list_keyboard(users))


async def delete_user(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    delete_user_from_db(user)
    users = get_all_users_from_db()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f'Пользователь {user} успешно удален',
                           reply_markup=create_users_list_keyboard(users))


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_bot, commands=['start'])
    dp.register_message_handler(get_user_list, text='Список пользователей')
    dp.register_callback_query_handler(back_function_for_user, lambda callback: callback.data == 'back')
    dp.register_callback_query_handler(delete_user, lambda callback: callback.data.split('*')[0] == 'delete_this_user')
    dp.register_message_handler(get_debtors_list, text='Список должников')
    dp.register_callback_query_handler(get_user_menu, lambda callback: callback.data.split('*')[0] == 'user')
    dp.register_callback_query_handler(get_user_balance, lambda callback: callback.data.split('*')[0] == 'balance')
    dp.register_callback_query_handler(update_user_balance, lambda callback: callback.data.split('*')[0] == 'deposit',
                                       state=None)
    dp.register_callback_query_handler(add_user_deposit,
                                       lambda callback: callback.data.split('*')[0] == 'money',
                                       state=FSMUsers.balance)
    dp.register_message_handler(add_user_deposit, state=FSMUsers.balance)
    dp.register_callback_query_handler(transfer_date_user,
                                       lambda callback: callback.data.split('*')[0] == 'date_expiration',
                                       state=FSMUsers.transfer_date)
    dp.register_message_handler(transfer_date_user, state=FSMUsers.transfer_date)

    dp.register_message_handler(start_fsm_add_user, text='Добавить пользователя')
    dp.register_message_handler(add_new_user_name, state=FSMAddUser.user_name)
    dp.register_callback_query_handler(add_start_user_balance,
                                       lambda callback: callback.data.split('*')[0] == 'money',
                                       state=FSMAddUser.balance)
    dp.register_message_handler(add_start_user_balance, state=FSMAddUser.balance)
    dp.register_callback_query_handler(add_date_expiration,
                                       lambda callback: callback.data.split('*')[0] == 'date_expiration',
                                       state=FSMAddUser.date_expiration)
    dp.register_message_handler(add_date_expiration, state=FSMAddUser.date_expiration)
    dp.register_message_handler(add_description, state=FSMAddUser.description)

