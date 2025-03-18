import logging
import aiohttp
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup, BufferedInputFile, InputMediaPhoto
from aiogram.utils.keyboard import InlineKeyboardBuilder
from aiogram.fsm.context import FSMContext
from config import GAME_API_URL, user_defects, defect_options
from keyboards import menu_keyboard, keyboard_start_test, keyboard_go_back


# Функция отправки инструкции с фото
async def send_instruction(message: types.Message, state: FSMContext):
    data = await state.get_data()
    photo_index = data.get("photo_index", 1)
    max_index = 8  # Фиксированное значение
    instruction_message_id = data.get("instruction_message_id")

    def get_instruction_keyboard(current_index):
        return InlineKeyboardMarkup(
            inline_keyboard=keyboard_start_test if current_index == max_index else keyboard_go_back)

    async def send_instruction_photo():
        photo_path = f"public/cards_instruction/{photo_index}.png"
        try:
            with open(photo_path, "rb") as photo_file:
                photo = BufferedInputFile(photo_file.read(), filename=f"{photo_index}.png")
                caption = f"Инструкция: шаг {photo_index}/8"

                if instruction_message_id is None:
                    msg = await message.answer_photo(
                        photo=photo, caption=caption, reply_markup=get_instruction_keyboard(photo_index)
                    )
                    await state.update_data(instruction_message_id=msg.message_id)
                else:
                    try:
                        await message.bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=instruction_message_id,
                            media=InputMediaPhoto(media=photo, caption=caption)
                        )
                        await message.bot.edit_message_reply_markup(
                            chat_id=message.chat.id,
                            message_id=instruction_message_id,
                            reply_markup=get_instruction_keyboard(photo_index)
                        )
                    except Exception:
                        msg = await message.answer_photo(
                            photo=photo, caption=caption, reply_markup=get_instruction_keyboard(photo_index)
                        )
                        await state.update_data(instruction_message_id=msg.message_id)
        except Exception as e:
            logging.error(f"Ошибка загрузки фото: {e}")
            await message.answer("Не удалось загрузить фото инструкции.")

    await send_instruction_photo()


def get_defect_keyboard(user_id):
    keyboard = InlineKeyboardBuilder()
    selected = user_defects.get(user_id, set())

    for i in range(0, len(defect_options), 2):
        row = [
            InlineKeyboardButton(
                text=("✅ " if defect in selected else "❌ ") + defect, callback_data=f"toggle_{defect}"
            ) for defect in defect_options[i:i + 2]
        ]
        keyboard.row(*row)

    keyboard.row(
        InlineKeyboardButton(text="⏭ Пропустить", callback_data="skip"),
        InlineKeyboardButton(text="📤 Отправить", callback_data="submit")
    )

    return keyboard.as_markup()


async def get_game_uid() -> str:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GAME_API_URL}/get-test", ssl=False) as response:
            if response.status == 200:
                data = await response.json()
                return data.get("uid")
            return None


async def get_photo(uid: str) -> bytes:
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{GAME_API_URL}/photo/{uid}", ssl=False) as response:
            if response.status == 200:
                return await response.read()
            return None


async def send_photo_with_defects(user_id: int, photo_data: bytes, uid: str, message: types.Message):
    photo = BufferedInputFile(photo_data, filename=f"{uid}.jpg")
    user_defects[user_id] = set()
    await message.answer_photo(
        photo=photo,
        caption="Выберите дефекты:",
        reply_markup=get_defect_keyboard(user_id)
    )


async def start_test(message: types.Message, state: FSMContext = None):  # Добавлен параметр state со значением по умолчанию
    user_id = message.from_user.id
    await message.answer("Начинаем тест! Запрашиваю фото...", reply_markup=menu_keyboard)

    uid = await get_game_uid()
    if uid:
        photo_data = await get_photo(uid)
        if photo_data:
            # Сохраняем UID фото в состоянии
            if state:
                await state.update_data(photo_uid=uid)
            await send_photo_with_defects(user_id, photo_data, uid, message)
        else:
            await message.answer("Не удалось получить фото.")
    else:
        await message.answer("Ошибка при запросе UID фото.")