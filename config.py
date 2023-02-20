import os
from dotenv import load_dotenv

load_dotenv()
TOKEN = os.getenv('TOKEN')
SQLITE_URL = os.getenv('SQLITE_URL')

