import logging
from aiogram import types
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import BufferedInputFile
from aiogram.fsm.context import FSMContext
from config import bot


# Функция отправки инструкции с фото
async def send_team(message: types.Message, state: FSMContext):
    # Получаем состояние из FSM
    data = await state.get_data()
    team_message = data.get("team_message")
    photo_team_index = data.get("photo_team_index")
    max_team_index = data.get("max_team_index")

    # Функция для получения клавиатуры для переключения слайдов
    def get_team_keyboard(current_index):
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="previous_team"),
             InlineKeyboardButton(text="Вперёд ➡️", callback_data="next_team")]
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def send_team_photo(message):
        nonlocal team_message, photo_team_index
        photo_path = f"public/cards_team/{photo_team_index}.png"

        with open(photo_path, "rb") as photo_file:
            photo = BufferedInputFile(photo_file.read(), filename=f"{photo_team_index}.png")

            if team_message is None:
                # Первая отправка фото
                team_message = await message.answer_photo(
                    photo=photo,
                    reply_markup=get_team_keyboard(photo_team_index)
                )
                await state.update_data(team_message=team_message)
            else:
                # Обновляем фото и клавиатуру
                try:
                    await bot.edit_message_media(
                        chat_id=message.chat.id,
                        message_id=team_message.message_id,
                        media=types.InputMediaPhoto(
                            media=photo
                        )
                    )
                    # Обновляем клавиатуру
                    await bot.edit_message_reply_markup(
                        chat_id=message.chat.id,
                        message_id=team_message.message_id,
                        reply_markup=get_team_keyboard(photo_team_index)
                    )
                except Exception as e:
                    logging.error(f"Error editing message: {e}")
                    # Если не удалось отредактировать, отправляем новое
                    team_message = await message.answer_photo(
                        photo=photo,
                        reply_markup=get_team_keyboard(photo_team_index)
                    )
                    await state.update_data(team_message=team_message)

    # Отправка фото
    await send_team_photo(message)
