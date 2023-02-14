from aiogram import Bot
from aiogram.dispatcher import Dispatcher
from aiogram.contrib.fsm_storage.memory import MemoryStorage

TOKEN = '5945096956:AAE4ce2vMtFqwHnq-pmJVDLi8A8hw1ILPWk'

storage=MemoryStorage()

bot = Bot(token=TOKEN)
dp = Dispatcher(bot, storage=storage)