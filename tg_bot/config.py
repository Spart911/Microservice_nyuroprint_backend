import logging
from aiogram import Bot
from aiogram.client.session.aiohttp import AiohttpSession
from aiogram.client.default import DefaultBotProperties
from aiogram.enums import ParseMode
from dotenv import load_dotenv
import os

# Загружаем переменные из .env файла
load_dotenv()

# Токен бота
TOKEN = os.getenv("BOT_TOKEN")

# Путь к PDF-файлу с политикой конфиденциальности
PDF_PATH_1 = os.getenv("PDF_PATH_1")

# Путь к PDF-файлу с пользовательским соглашением
PDF_PATH_2 = os.getenv("PDF_PATH_2")

TEAM_PNG_PATH = os.getenv("TEAM_PNG_PATH")

API_USER = os.getenv("API_USER")
GAME_API_URL = os.getenv("GAME_API_URL")
DETECT_API = os.getenv("DETECT_API")

# Список дефектов для разметки
defect_options = os.getenv("DEFECT_OPTIONS").split(", ")

# Хранение выбора пользователя
user_defects = {}

quality_options = {q: i+1 for i, q in enumerate(os.getenv("QUALITY_OPTIONS").split(", "))}

default_printers = [
    {"id": i, "name": printer}
    for i, printer in enumerate(os.getenv("DEFAULT_PRINTERS").split(", "))
]

# Для работы с ботом обратной связи
BOT_TOKEN = os.getenv("BOT_FEEDBACK_TOKEN")
CHAT_ID = os.getenv("CHAT_ID")
URL = f"https://api.telegram.org/bot{BOT_TOKEN}/sendMessage"

# Конфигурация бота
logging.basicConfig(level=logging.INFO)
session = AiohttpSession()
bot = Bot(token=TOKEN, default=DefaultBotProperties(parse_mode=ParseMode.MARKDOWN), session=session)
