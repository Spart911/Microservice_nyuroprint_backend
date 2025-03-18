import os
import shutil
import asyncio
from aiogram import Bot, Dispatcher, types, F
from aiogram.types import FSInputFile, InlineKeyboardMarkup, InlineKeyboardButton
from aiogram.filters import Command
from aiogram.utils.keyboard import InlineKeyboardBuilder
from dotenv import load_dotenv

# Загружаем переменные из .env
load_dotenv()
TOKEN = os.getenv("TOKEN")
DIR_DETECT = os.getenv("DIR_DETECT", "dir_detect")
DIR_MARKUP = os.getenv("DIR_MARKUP", "dir_markup")

# Убеждаемся, что папки существуют
os.makedirs(DIR_DETECT, exist_ok=True)
os.makedirs(DIR_MARKUP, exist_ok=True)

# Инициализация бота и диспетчера
bot = Bot(token=TOKEN)
dp = Dispatcher()


async def get_next_photo():
    """Возвращает первый файл из папки DIR_DETECT или None, если файлов нет"""
    files = sorted(os.listdir(DIR_DETECT))  # Получаем список файлов
    for file in files:
        if file.lower().endswith(('.jpg', '.jpeg', '.png', '.bmp')):  # Проверяем расширение
            return file
    return None


@dp.message(Command("start"))
@dp.message(Command("validate"))
async def start_validation(message: types.Message):
    """Начинает процесс валидации"""
    filename = await get_next_photo()

    if not filename:
        await message.answer("Нет новых фото для проверки.")
        return

    filepath = os.path.join(DIR_DETECT, filename)

    keyboard = InlineKeyboardMarkup(inline_keyboard=[
        [InlineKeyboardButton(text="✅ Оставить", callback_data=f"approve|{filename}")],
        [InlineKeyboardButton(text="❌ Удалить", callback_data=f"reject|{filename}")]
    ])

    photo = FSInputFile(filepath)
    await message.answer_photo(photo, caption=f"Файл: {filename}", reply_markup=keyboard)


@dp.callback_query(F.data.startswith("approve|"))
async def approve_photo(callback: types.CallbackQuery):
    """Перемещает фото в папку DIR_MARKUP"""
    filename = callback.data.split("|")[1]
    src_path = os.path.join(DIR_DETECT, filename)
    dst_path = os.path.join(DIR_MARKUP, filename)

    if os.path.exists(src_path):
        shutil.move(src_path, dst_path)
        await callback.message.answer(f"✅ Файл {filename} сохранён.")
    else:
        await callback.message.answer("⚠ Файл уже обработан.")

    await callback.message.delete()
    await start_validation(callback.message)


@dp.callback_query(F.data.startswith("reject|"))
async def reject_photo(callback: types.CallbackQuery):
    """Удаляет фото"""
    filename = callback.data.split("|")[1]
    file_path = os.path.join(DIR_DETECT, filename)

    if os.path.exists(file_path):
        os.remove(file_path)
        await callback.message.answer(f"❌ Файл {filename} удалён.")
    else:
        await callback.message.answer("⚠ Файл уже обработан.")

    await callback.message.delete()
    await start_validation(callback.message)


async def main():
    """Запуск бота"""
    print("🔹 Бот запущен!")
    await dp.start_polling(bot)


if __name__ == "__main__":
    asyncio.run(main())
