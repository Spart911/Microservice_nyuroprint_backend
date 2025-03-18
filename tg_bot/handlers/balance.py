from aiogram import Router, types
from aiohttp import ClientSession
from config import API_USER
from aiogram.types import Message

router = Router()


@router.message(lambda message: message.text == "💵 Баланс бонусов")
async def balance(message: Message):
    """
    Обрабатывает запрос пользователя на получение баланса бонусов через API.
    """
    user_id_telegram = str(message.from_user.id)  # Получаем ID Telegram пользователя

    # Формируем URL для запроса
    url = f"{API_USER}/users/telegram/{user_id_telegram}/bonuses"

    # Запрос к API для получения баланса бонусов
    async with ClientSession() as session:
        async with session.get(url) as response:
            if response.status == 200:
                # Получаем данные баланса
                balance = await response.json()
                await message.answer(f"Ваш баланс бонусов: {balance}")
            else:
                await message.answer("Не удалось получить баланс бонусов. Попробуйте позже.")
