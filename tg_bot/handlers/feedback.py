import aiohttp
from aiogram import types, Router
from aiogram.fsm.context import FSMContext
from aiogram.types import InlineKeyboardMarkup, InlineKeyboardButton, CallbackQuery, FSInputFile
from utils.utils_privacy_policy_status import check_privacy_policy_status, update_privacy_policy_status
from utils.utils_sing_up import  is_valid_email
from class_states import FeedbackStates
from config import CHAT_ID, URL, PDF_PATH_1


router = Router()


@router.message(lambda message: message.text == "📩 Обратная связь")
async def start_feedback(message: types.Message, state: FSMContext):
    """Запуск процесса обратной связи"""
    user_id = message.from_user.id
    privacy_status = await check_privacy_policy_status(user_id)

    if privacy_status == 0:
        keyboard = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Согласиться", callback_data="accept_privacy_policy")],
            [InlineKeyboardButton(text="Ознакомиться с политикой конфиденциальности",
                                  callback_data="view_privacy_policy")]
        ])
        await message.answer("Вы должны согласиться с политикой конфиденциальности перед отправкой сообщения.",
                             reply_markup=keyboard)
        return
    elif privacy_status == 2:
        await message.answer("Для использования этой функции необходимо зарегистрироваться.")
        return

    await message.answer("Пожалуйста, введите ваше ФИО:")
    await state.set_state(FeedbackStates.name)

@router.message(FeedbackStates.name)
async def process_name(message: types.Message, state: FSMContext):
    """Обработка ввода ФИО"""
    await state.update_data(name=message.text)
    await message.answer("Теперь введите ваш email:")
    await state.set_state(FeedbackStates.email)

@router.message(FeedbackStates.email)
async def process_email(message: types.Message, state: FSMContext):
    """Обработка ввода email"""
    if not is_valid_email(message.text):
        await message.answer("❌ Неверный формат email. Пожалуйста, введите корректный email:")
        return

    await state.update_data(email=message.text)
    await message.answer("Напишите ваше сообщение:")
    await state.set_state(FeedbackStates.message)

@router.message(FeedbackStates.message)
async def process_message(message: types.Message, state: FSMContext):
    """Обработка ввода сообщения"""
    data = await state.get_data()
    name = data.get("name")
    email = data.get("email")
    text = f"ФИО: {name}\nПочта: {email}\nСообщение: {message.text}"

    async with aiohttp.ClientSession() as session:
        async with session.post(URL, json={"chat_id": CHAT_ID, "text": text}) as response:
            if response.status == 200:
                await message.answer("✅ Ваше сообщение успешно отправлено!")
            else:
                await message.answer("❌ Ошибка при отправке сообщения.")

    await state.clear()

# Обработчик согласия с политикой конфиденциальности
@router.callback_query(lambda c: c.data == "accept_privacy_policy")
async def accept_privacy_policy(callback: CallbackQuery):
    user_id = callback.from_user.id
    if await update_privacy_policy_status(user_id):
        await callback.message.answer("Вы согласились с политикой конфиденциальности. Теперь можете продолжить.")
    else:
        await callback.message.answer("Ошибка при обновлении согласия. Попробуйте ещё раз.")


# Обработчик нажатия на кнопку "Ознакомиться с политикой конфиденциальности"
@router.callback_query(lambda c: c.data == "view_privacy_policy")
async def view_privacy_policy(callback: CallbackQuery):
    # Передаем путь к файлу
    file = FSInputFile(PDF_PATH_1)  # Путь к файлу должен быть правильным
    await callback.message.answer_document(file)
    await callback.message.answer("Вы можете ознакомиться с политикой конфиденциальности.")
