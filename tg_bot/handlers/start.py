import logging
from aiogram import Router, types
from aiogram.filters import Command
from keyboards import menu_keyboard

router = Router()

@router.message(Command("start"))
async def start_command(message: types.Message):
    logging.debug(f"Received /start command from user {message.from_user.id}")
    await message.answer("Привет! Я бот. Выбери действие в меню:", reply_markup=menu_keyboard)
