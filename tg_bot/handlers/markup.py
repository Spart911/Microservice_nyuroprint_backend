import aiohttp
from aiogram import Router, types
from config import user_defects, GAME_API_URL, defect_options, API_USER
from utils.utils_privacy_policy_status import check_privacy_policy_status
from utils.utils_markup import get_defect_keyboard, start_test, send_instruction, get_game_uid, get_photo, send_photo_with_defects
from keyboards import keyboard_policy
from aiogram.fsm.context import FSMContext

router = Router()


@router.message(lambda message: message.text == "🕹 Мини-игра")
async def mini_game(message: types.Message, state: FSMContext):
    """Запуск мини-игры"""
    user_id = message.from_user.id
    privacy_status = await check_privacy_policy_status(user_id)

    if privacy_status == 0:
        await message.answer(
            "Вы должны согласиться с политикой конфиденциальности перед отправкой сообщения.",
            reply_markup=keyboard_policy,
        )
        return
    elif privacy_status == 2:
        await message.answer("Для использования этой функции необходимо зарегистрироваться.")
        return

    await state.update_data(instruction_message_id=None, photo_index=1)
    await send_instruction(message, state)


@router.callback_query(lambda c: c.data.startswith("toggle_"))
async def toggle_defect(callback: types.CallbackQuery):
    """Переключает чекбокс дефекта"""
    user_id = callback.from_user.id
    defect = callback.data.split("_")[1]

    if user_id not in user_defects:
        user_defects[user_id] = set()

    if defect in user_defects[user_id]:
        user_defects[user_id].remove(defect)
    else:
        user_defects[user_id].add(defect)

    await callback.message.edit_reply_markup(reply_markup=get_defect_keyboard(user_id))
    await callback.answer()


@router.callback_query(lambda c: c.data == "skip")
async def skip_defects(callback: types.CallbackQuery, state: FSMContext):
    """Пропуск выбора дефектов"""
    user_id = callback.from_user.id
    await callback.message.delete()
    await callback.answer()

    # Запрос нового фото
    uid = await get_game_uid()
    if uid:
        photo_data = await get_photo(uid)
        if photo_data:
            await state.update_data(photo_uid=uid)  # Сохраняем UID нового фото
            await send_photo_with_defects(user_id, photo_data, uid, callback.message)
        else:
            await callback.message.answer("Не удалось получить фото.")
    else:
        await callback.message.answer("Ошибка при запросе UID фото.")


@router.callback_query(lambda c: c.data == "submit")
async def submit_defects(callback: types.CallbackQuery, state: FSMContext):
    """Отправка выбранных дефектов и загрузка следующего фото"""
    user_id = callback.from_user.id
    selected_defects = user_defects.get(user_id, [])
    selected_defects_str = ",".join(str(defect_options.index(d)) for d in selected_defects if d in defect_options)
    await callback.message.delete()
    await callback.answer()

    # Получаем UID фото из состояния
    data = await state.get_data()
    uid = data.get("photo_uid")
    if not uid:
        await callback.message.answer("Ошибка: UID фото не найден.")
        return

    # Отправка разметки на API
    payload = {"userUid": str(user_id), "uid": uid, "target": selected_defects_str}
    async with aiohttp.ClientSession() as session:
        async with session.post(f"{GAME_API_URL}/process-test", json=payload, ssl=False) as response:
            if response.status != 200:
                await callback.message.answer("Ошибка при отправке данных на сервер.")
                return

            # Если разметка успешно отправлена, вызываем API для увеличения бонуса
            # Используем try-except для обработки возможных ошибок
            try:
                async with session.put(f"{API_USER}/users/telegram/{user_id}/increment-bonus") as bonus_response:
                    if bonus_response.status != 200:
                        error_text = await bonus_response.text()
                        await callback.message.answer(f"Ошибка при обновлении бонусов: {error_text}")
            except Exception as e:
                await callback.message.answer(f"Ошибка при обновлении бонусов: {str(e)}")

    # Запрос нового фото
    uid = await get_game_uid()
    if uid:
        photo_data = await get_photo(uid)
        if photo_data:
            await state.update_data(photo_uid=uid)  # Сохраняем UID нового фото
            await send_photo_with_defects(user_id, photo_data, uid, callback.message)
        else:
            await callback.message.answer("Не удалось получить фото.")
    else:
        await callback.message.answer("Ошибка при запросе UID фото.")



@router.callback_query(lambda c: c.data in ["next", "previous", "start_test"])
async def instruction_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo_index = data.get("photo_index", 1)
    max_index = 8

    if callback_query.data == "start_test":
        await start_test(callback_query.message, state)  # Передаем state в функцию start_test
        return

    if callback_query.data == "previous":
        photo_index = max(1, photo_index - 1)
    elif callback_query.data == "next":
        photo_index = min(max_index, photo_index + 1)

    await state.update_data(photo_index=photo_index)
    await send_instruction(callback_query.message, state)
    await callback_query.answer()