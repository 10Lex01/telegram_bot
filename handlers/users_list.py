from aiogram import types, Dispatcher
from database.services import add_to_db_users, get_all_users_from_db, get_user_balance_from_db, \
    update_balance_and_date_for_user, delete_user_from_db, create_operation, get_user_operations_from_db
from handlers.service import check_date, calculate_expiration_date, is_debtor
from create_bot import bot
from aiogram.dispatcher import FSMContext, filters
from aiogram.dispatcher.filters.state import State, StatesGroup
from keyboards.users_kb import create_main_keyboard, create_balance_keyboard, create_transfer_date_keyboard, \
    create_users_list_keyboard, create_user_keyboard, confirm_delete_user_keyboards
from config import ID_ADMIN_1, ID_ADMIN_2, ID_ADMIN_3
from typing import Union


async def start_bot(message: types.Message):
    """Запуск бота"""
    await bot.send_message(message.from_user.id, 'Сейчас узнаем кто нам задолжал!', reply_markup=create_main_keyboard())


async def get_user_list(request: Union[types.Message, types.InlineKeyboardMarkup]):
    """Открывает клавиатуру списка пользователей"""
    users = get_all_users_from_db()
    await request.answer('Список пользователей:', reply_markup=create_users_list_keyboard(users))


async def get_debtors_list(message: types.Message):
    """Открывает клавиатуру списка должников"""
    users = get_all_users_from_db()
    debtors_list = []
    for user in users:
        if is_debtor(user):
            debtors_list.append(user)
    if len(debtors_list) == 0:
        await message.answer('Должников нет')
    else:
        await message.answer('Список должников:', reply_markup=create_users_list_keyboard(debtors_list))


async def get_user_menu(callback: types.CallbackQuery):
    """Открывает меню пользователя"""
    user_name = callback.data.split('*')[1]
    user = get_user_balance_from_db(user_name)
    message_text = f'{user.user_name}'
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=message_text, reply_markup=create_user_keyboard(user.user_name))


async def get_user_balance(callback: types.CallbackQuery):
    """Inline клавиатура "Информация" для пользователя"""
    user_name = callback.data.split('*')[1]
    user = get_user_balance_from_db(user_name)
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f'Пользователь: {user.user_name}\n'
                                f'Баланс: {user.balance} ₽\n'
                                f'Дата истечения срока: {user.date_expiration.strftime("%d.%m.%Y")}\n'
                                f'*{user.description}',
                           reply_markup=create_user_keyboard(user.user_name))


async def get_user_last_operations(callback: types.CallbackQuery):
    """Inline клавиатура "Последние операции" для пользователя"""
    user_name = callback.data.split('*')[1]
    user = get_user_balance_from_db(user_name)
    user_operations = get_user_operations_from_db(user.id)
    string = ''
    for operation in enumerate(user_operations):
        string = string + f'{operation[0] + 1}. Дата операции {operation[1].date_operation.strftime("%d.%m.%Y")}\n' \
                          f'Сумма {operation[1].summ}\n'
    await bot.send_message(chat_id=callback.message.chat.id, text=string)


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
                               text=f'Введите сумму пополнения для <b>{user}</b>:',
                               reply_markup=create_balance_keyboard(),
                               parse_mode='html')


async def add_user_deposit(request: Union[types.CallbackQuery, types.Message], state: FSMContext):
    """Ввод данных о пополнении баланса через Inline клавиатуру"""
    if type(request) == types.CallbackQuery:
        cash = request.data.split('*')[1]
        async with state.proxy() as data:
            user = data['user_name']
            data['balance'] = cash
            await FSMUsers.next()
            await bot.send_message(chat_id=request.message.chat.id,
                                   text=f'Баланс <b>{user}</b> пополнен на <b>{cash}</b>'
                                        f'\nВведите дату пополнения счета',
                                   reply_markup=create_transfer_date_keyboard(),
                                   parse_mode='html')
    else:
        async with state.proxy() as data:
            user = data['user_name']
            data['balance'] = request.text
            await request.delete()
            await FSMUsers.next()
            await request.answer(f'Баланс <b>{user}</b> пополнен на <b>{request.text}</b>'
                                 f'\nВведите дату пополнения счета',
                                 reply_markup=create_transfer_date_keyboard(),
                                 parse_mode='html')


async def transfer_date_user(request: Union[types.CallbackQuery, types.Message], state: FSMContext):
    """Ввод даты перевода за использование VPN через Inline клавиатуру, выход из FSM"""
    if type(request) == types.CallbackQuery:
        user_transfer_date = request.data.split('*')[1]
        async with state.proxy() as data:
            update_balance_and_date_for_user(data['user_name'], data['balance'])
            create_operation(user_name=data['user_name'], summ=data['balance'], transfer_date=user_transfer_date)
            await bot.send_message(chat_id=request.message.chat.id,
                                   text=f'Баланс успешно пополнен',
                                   reply_markup=create_main_keyboard())
            await state.finish()
    else:
        if check_date(request):
            async with state.proxy() as data:
                update_balance_and_date_for_user(data['user_name'], data['balance'])
                create_operation(user_name=data['user_name'], summ=data['balance'], transfer_date=request.text)
                await request.answer('Данные успешно добавлены', reply_markup=create_main_keyboard())
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
    await message.answer('Введите стартовый баланс', reply_markup=create_balance_keyboard())


async def add_start_user_balance(request: Union[types.CallbackQuery, types.Message], state: FSMContext):
    """Отлавливаем баланс, запрашиваем дату истечения срока оплаты"""
    if type(request) == types.CallbackQuery:
        balance = request.data.split('*')[1]
        async with state.proxy() as data:
            data['balance'] = int(balance)
        await FSMAddUser.date_expiration.set()
        await bot.send_message(chat_id=request.message.chat.id, text=f'Введите дату пополнения счета на {int(balance)}',
                               reply_markup=create_transfer_date_keyboard())
    else:
        async with state.proxy() as data:
            try:
                data['balance'] = int(request.text)
            except ValueError:
                await request.reply('Введите число')
                return
        await FSMAddUser.date_expiration.set()
        await request.answer(f'Введите дату пополнения счета на {int(request.text)}',
                             reply_markup=create_transfer_date_keyboard())


async def add_date_expiration(request: Union[types.CallbackQuery, types.Message], state: FSMContext) -> None:
    """Отлавливаем дату истечения срока оплаты"""
    if type(request) == types.CallbackQuery:
        transfer_date = request.data.split('*')[1]
        async with state.proxy() as data:
            data['transfer_date'] = transfer_date
            data['date_expiration'] = calculate_expiration_date(transfer_date, data['balance'])
            await bot.send_message(chat_id=request.message.chat.id,
                                   text='Введите примечание для пользователя', reply_markup=create_main_keyboard())
        await FSMAddUser.description.set()
    else:
        if check_date(request):
            async with state.proxy() as data:
                try:
                    data['transfer_date'] = request.text
                    data['date_expiration'] = calculate_expiration_date(request.text, data['balance'])
                except ValueError:
                    await request.reply('Введите дату в формате: <b>ДД.ММ.ГГГГ</b>', parse_mode='html')
                    return
                await request.answer('Введите примечание для пользователя', reply_markup=create_main_keyboard())
            await FSMAddUser.description.set()
        else:
            await request.reply('Не верный формат\nВведите дату в формате: <b>ДД.ММ.ГГГГ</b>', parse_mode='html')


async def add_description(message: types.Message, state: FSMContext):
    """Отлавливаем примечание"""
    async with state.proxy() as data:
        data['description'] = message.text
        transfer_date = data['transfer_date']
        del data['transfer_date']
        add_to_db_users(data, transfer_date)
        await message.answer('Данные успешно добавлены', reply_markup=create_main_keyboard())
    await state.finish()


async def back_function_for_user(callback: types.CallbackQuery):
    """Выход из FSM при отправке сообщения 'отмена'"""
    users = get_all_users_from_db()
    await bot.send_message(chat_id=callback.message.chat.id,
                           text='Список пользователей:',
                           reply_markup=create_users_list_keyboard(users))


async def confirm_delete_user(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    await bot.send_message(chat_id=callback.message.chat.id,
                           text=f'Удалить пользователя <b>{user}</b>?',
                           reply_markup=confirm_delete_user_keyboards(user),
                           parse_mode='html')


async def delete_user(callback: types.CallbackQuery):
    user = callback.data.split('*')[1]
    users = get_all_users_from_db()
    if callback.data.split('*')[0] == 'yes':
        delete_user_from_db(user)
        users = get_all_users_from_db()
        await bot.send_message(chat_id=callback.message.chat.id,
                               text=f'Пользователь <b>{user}</b> успешно удален',
                               parse_mode='html')
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='Список пользователей:',
                               reply_markup=create_users_list_keyboard(users))
    else:
        await bot.send_message(chat_id=callback.message.chat.id,
                               text='Список пользователей:',
                               reply_markup=create_users_list_keyboard(users))


async def cancel_handler(callback: types.CallbackQuery, state: FSMContext):
    current_state = await state.get_state()
    if current_state is None:
        return
    await state.finish()
    await callback.message.answer('OK', reply_markup=create_main_keyboard())


def register_handlers_users(dp: Dispatcher):
    dp.register_message_handler(start_bot, filters.IDFilter(user_id=ID_ADMIN_1), commands=['start'])
    dp.register_message_handler(start_bot, filters.IDFilter(user_id=ID_ADMIN_2), commands=['start'])
    dp.register_message_handler(start_bot, filters.IDFilter(user_id=ID_ADMIN_3), commands=['start'])
    dp.register_message_handler(get_user_list, text='Список пользователей')
    dp.register_callback_query_handler(back_function_for_user, lambda callback: callback.data == 'back')
    dp.register_callback_query_handler(cancel_handler, lambda callback: callback.data == 'cancel', state="*")
    dp.register_callback_query_handler(confirm_delete_user,
                                       lambda callback: callback.data.split('*')[0] == 'delete_this_user')
    dp.register_callback_query_handler(delete_user, lambda callback: callback.data.split('*')[0] == 'yes')
    dp.register_callback_query_handler(delete_user, lambda callback: callback.data.split('*')[0] == 'no')
    dp.register_message_handler(get_debtors_list, text='Список должников')
    dp.register_callback_query_handler(get_user_menu, lambda callback: callback.data.split('*')[0] == 'user')
    dp.register_callback_query_handler(get_user_balance, lambda callback: callback.data.split('*')[0] == 'balance')
    dp.register_callback_query_handler(get_user_last_operations,
                                       lambda callback: callback.data.split('*')[0] == 'last_operations')
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
