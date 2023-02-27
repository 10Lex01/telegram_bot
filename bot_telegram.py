from aiogram.utils import executor
from create_bot import dp
from database.database import create_db
from handlers import users_list


async def on_startup(_):
    print('Добы день!')


create_db()
users_list.register_handlers_users(dp)
executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
