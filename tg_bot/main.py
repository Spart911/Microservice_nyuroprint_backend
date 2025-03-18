import asyncio
import logging
from aiogram import Dispatcher, Router
from aiogram.fsm.storage.memory import MemoryStorage
from aiogram.types import BotCommand
from aiogram.filters import Command

from config import bot

# Импорт всех обработчиков из директории handlers
from handlers.start import router as start_router
from handlers.detect_defect import router as detect_router
from handlers.markup import router as markup_router
from handlers.about_us import router as about_us_router
from handlers.partners import router as partners_router
from handlers.feedback import router as feedback_router
from handlers.sing_up import router as sing_up_router
from handlers.privacy_policy import router as privacy_policy_router
from handlers.user_agreement import router as user_agreement_router
from handlers.contacts import router as contacts_router
from handlers.team import router as team_router
from handlers.info_bonus import router as info_bonus_router
from handlers.balance import router as balance_router


# Настройка логирования
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

# Создание диспетчера
dp = Dispatcher(storage=MemoryStorage())

# Регистрация роутеров
dp.include_router(start_router)
dp.include_router(detect_router)
dp.include_router(markup_router)
dp.include_router(about_us_router)
dp.include_router(partners_router)
dp.include_router(feedback_router)
dp.include_router(sing_up_router)
dp.include_router(privacy_policy_router)
dp.include_router(user_agreement_router)
dp.include_router(contacts_router)
dp.include_router(team_router)
dp.include_router(info_bonus_router)
dp.include_router(balance_router)

# Основной роутер для необработанных сообщений
main_router = Router()
dp.include_router(main_router)


# Установка команд бота
async def set_commands():
    commands = [
        BotCommand(command="start", description="Начать работу с ботом"),
        BotCommand(command="help", description="Получить помощь"),
    ]
    await bot.set_my_commands(commands)


# Обработчик по умолчанию для необработанных сообщений
@main_router.message()
async def default_handler(message):
    await message.answer("Не понимаю эту команду. Используйте меню или /help для получения списка команд.")


# Команда помощи
@main_router.message(Command("help"))
async def help_command(message):
    help_text = """
*Доступные команды*:
/start - Начать работу с ботом
/detect - Распознать дефекты
/markup - Разметка дефектов
/about - О нас
/feedback - Обратная связь

Для удобства вы можете использовать меню внизу экрана.
"""
    await message.answer(help_text)


# Событие при запуске
async def on_startup():
    try:
        # Установка команд бота
        await set_commands()
        logger.info("Команды бота успешно установлены")

        # Уведомление о перезапуске бота
        logger.info("Бот запущен")
    except Exception as e:
        logger.error(f"Ошибка при запуске: {e}")


# Событие при выключении
async def on_shutdown():
    logger.info("Выключение бота...")
    await bot.session.close()
    logger.info("Сессия бота закрыта")


# Запуск бота
async def main():
    try:
        logger.info("Запуск бота...")
        await on_startup()
        await dp.start_polling(bot, skip_updates=True)
    except Exception as e:
        logger.error(f"Ошибка при запуске бота: {e}")
    finally:
        await on_shutdown()


# Запуск программы
if __name__ == "__main__":
    asyncio.run(main())
