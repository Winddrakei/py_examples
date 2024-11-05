import os
from dotenv import load_dotenv, find_dotenv

if not find_dotenv():
    exit('Переменные окружения не загружены, так как отсутствует файл .env')
else:
    load_dotenv()


BOT_TOKEN = os.getenv('BOT_TOKEN')
DB_PATH = os.path.join('database', 'database.db')
API_KEY = os.getenv('API_KEY')
X_RAPID_API_KEY = os.getenv('X_RAPID_API_KEY')
X_RAPID_API_HOST = os.getenv('X_RAPID_API_HOST')

LIMIT_ITEMS = 30

""" поддерживаемые команды Peewee """
DEFAULT_COMMANDS = (
    ("history", "Последние 10 запросов")
)
