import logging
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from utils.utils_partners import send_partners_slider
from utils.utils_markup import start_test


router = Router()


@router.message(lambda message: message.text == "💼 Партнёры")
async def partners_slider(message: types.Message, state: FSMContext):
    # Сбрасываем состояние перед отправкой слайдера
    await state.update_data(partner_photo_index=1, partner_message=None, max_partner_index=4)  # Пример max_partner_index
    # Отправляем слайдер с фото партнёров
    await send_partners_slider(message, state, is_initial=True)


# Обработчик callback_query для слайдера партнёров
@router.callback_query(lambda c: c.data in ["next_partner", "previous_partner", "start_test"])
async def partner_slider_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    partner_photo_index = data.get("partner_photo_index", 1)
    max_partner_index = data.get("max_partner_index", 10)

    logging.info(f"Partner slider navigation: {callback_query.data}, Current index: {partner_photo_index}")

    if callback_query.data == "start_test":
        # Запуск теста
        await start_test(callback_query.message)
        return

    if callback_query.data == "previous_partner" and partner_photo_index > 1:
        partner_photo_index -= 1
    elif callback_query.data == "next_partner" and partner_photo_index < max_partner_index:
        partner_photo_index += 1

    await state.update_data(partner_photo_index=partner_photo_index)

    await send_partners_slider(callback_query.message, state)  # Редактируем текущее сообщение с фото
    await callback_query.answer()  # Подтверждаем обработку callback