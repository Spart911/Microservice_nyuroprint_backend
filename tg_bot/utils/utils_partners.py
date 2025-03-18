import logging
from aiogram import types
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardButton, InlineKeyboardMarkup
from aiogram.types import BufferedInputFile
from config import bot


# Функция для отправки слайдера с фото партнёров
async def send_partners_slider(message: types.Message, state: FSMContext, is_initial=False):
    # Получаем состояние из FSM
    data = await state.get_data()
    partner_photo_index = data.get("partner_photo_index", 1)  # Устанавливаем значение по умолчанию
    max_partner_index = data.get("max_partner_index", 4)  # Устанавливаем значение по умолчанию
    partner_message = data.get("partner_message", None)  # Устанавливаем значение по умолчанию

    logging.info(f"Sending partner slider: Current index {partner_photo_index}, Max index {max_partner_index}")

    def get_partner_slider_keyboard(current_index):
        # Используем прямое создание списка клавиатуры
        keyboard = [
            [InlineKeyboardButton(text="⬅️ Назад", callback_data="previous_partner"),
             InlineKeyboardButton(text="Вперёд ➡️", callback_data="next_partner")],
        ]
        return InlineKeyboardMarkup(inline_keyboard=keyboard)

    async def send_partner_photo(message):
        # Убираем глобальные переменные, теперь работаем с состоянием
        photo_path = f"public/partners/{partner_photo_index}.png"
        nonlocal partner_message  # Явно указываем, что переменная берётся из внешней области видимости

        try:
            with open(photo_path, "rb") as photo_file:
                photo = BufferedInputFile(photo_file.read(), filename=f"{partner_photo_index}.png")
                logging.info(f"Partner photo: {photo_path}")

                if partner_message is None:
                    # Первая отправка фото
                    partner_message = await message.answer_photo(
                        photo=photo,
                        reply_markup=get_partner_slider_keyboard(partner_photo_index)
                    )
                    # Обновляем состояние с partner_message
                    await state.update_data(partner_message=partner_message)
                else:
                    # Попробуем обновить фото и клавиатуру
                    try:
                        await bot.edit_message_media(
                            chat_id=message.chat.id,
                            message_id=partner_message.message_id,
                            media=types.InputMediaPhoto(
                                media=photo
                            )
                        )
                        # Обновляем клавиатуру
                        await bot.edit_message_reply_markup(
                            chat_id=message.chat.id,
                            message_id=partner_message.message_id,
                            reply_markup=get_partner_slider_keyboard(partner_photo_index)
                        )
                    except Exception as e:
                        logging.error(f"Error editing message: {e}")
                        # Если редактирование не удалось, отправляем новое сообщение
                        partner_message = await message.answer_photo(
                            photo=photo,
                            reply_markup=get_partner_slider_keyboard(partner_photo_index)
                        )
                        # Обновляем состояние с partner_message
                        await state.update_data(partner_message=partner_message)
        except Exception as e:
            logging.error(f"Error opening partner photo: {e}")
            await message.answer("Не удалось загрузить фото партнёра.")

    # Отправляем или редактируем фото
    await send_partner_photo(message)
