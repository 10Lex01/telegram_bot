from aiogram.utils import executor
from create_bot import dp

async def on_startup(_):
    print('Здорово заебал')

from handlers import users_list

users_list.register_handlers_users(dp)

executor.start_polling(dp, skip_updates=True, on_startup=on_startup)
