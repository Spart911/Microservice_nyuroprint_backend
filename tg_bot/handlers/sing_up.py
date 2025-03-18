import logging
import aiohttp
from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from aiogram.types import ReplyKeyboardMarkup, KeyboardButton
from config import API_USER
from class_states import Registration
from utils.utils_sing_up import is_valid_email, is_valid_password
from keyboards import menu_keyboard

router = Router()

# Create a registration keyboard that includes the cancel option
registration_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="Продолжить регистрацию"), KeyboardButton(text="Отменить регистрацию")]
    ],
    resize_keyboard=True
)


@router.message(lambda message: message.text == "📝 Регистрация")
async def registration_start(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    logging.debug(f"User {user_id} selected registration")

    # Проверка, зарегистрирован ли пользователь
    async with aiohttp.ClientSession() as session:
        async with session.get(f"{API_USER}/users/telegram/{user_id}") as response:
            if response.status == 200:
                await message.answer("Вы уже зарегистрированы! Используйте меню.")
                return

    # Запрос на ввод email
    await message.answer("Введите ваш email:", reply_markup=registration_keyboard)
    await state.set_state(Registration.email)



@router.message(Registration.email, lambda message: message.text not in ["Продолжить регистрацию", "Отменить регистрацию"])
async def process_email(message: types.Message, state: FSMContext):
    email = message.text
    if not is_valid_email(email):
        await message.answer("Пожалуйста, введите корректный email.", reply_markup=registration_keyboard)
        return

    await state.update_data(email=email)
    await message.answer("Теперь введите пароль:", reply_markup=registration_keyboard)
    await state.set_state(Registration.password)


@router.message(Registration.password, lambda message: message.text not in ["Продолжить регистрацию", "Отменить регистрацию"])
async def process_password(message: types.Message, state: FSMContext):
    password = message.text
    if not is_valid_password(password):
        await message.answer("Пароль должен содержать минимум 6 символов, включая хотя бы одну букву и одну цифру.",
                           reply_markup=registration_keyboard)
        return

    data = await state.get_data()
    email = data["email"]
    user_id = str(message.from_user.id)
    amount_bonuses = 0  # Начальное количество бонусов

    async with aiohttp.ClientSession() as session:
        async with session.post(
                f"{API_USER}/users/",
                json={
                    "id_telegram": user_id,
                    "amount_bonuses": amount_bonuses,
                    "email": email,
                    "password": password
                }
        ) as response:
            if response.status == 200:
                await message.answer("Регистрация успешна!", reply_markup=menu_keyboard)
            elif response.status == 400:
                await message.answer("Пользователь с таким email уже зарегистрирован.", reply_markup=menu_keyboard)
            else:
                error_text = await response.text()
                await message.answer(f"Ошибка при регистрации: {error_text}", reply_markup=menu_keyboard)

    await state.clear()


@router.message(lambda message: message.text == "Продолжить регистрацию")
async def complete_registration(message: types.Message, state: FSMContext):
    current_state = await state.get_state()

    if current_state == Registration.email:
        # If at email state, remind user they need to enter email first
        await message.answer("Пожалуйста, сначала введите ваш email.", reply_markup=registration_keyboard)
        return
    elif current_state == Registration.password:
        # We should NOT call process_password directly
        # Instead, remind user to enter their password
        await message.answer("Пожалуйста, введите пароль для завершения регистрации.", reply_markup=registration_keyboard)
        return
    else:
        await message.answer("Неопределенный этап регистрации. Начните регистрацию заново.")
        await state.clear()
        await message.answer("Введите ваш email:", reply_markup=registration_keyboard)
        await state.set_state(Registration.email)


@router.message(lambda message: message.text == "Отменить регистрацию")
async def cancel_registration(message: types.Message, state: FSMContext):
    # This should work regardless of the current registration state
    await state.clear()  # Clear registration state
    await message.answer("Регистрация отменена. Вы можете начать заново, если хотите.",
                         reply_markup=menu_keyboard)  # Return to the main menu