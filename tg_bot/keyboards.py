from aiogram.types import ReplyKeyboardMarkup, KeyboardButton, InlineKeyboardMarkup, InlineKeyboardButton


# Главное меню
menu_keyboard = ReplyKeyboardMarkup(
    keyboard=[
        [KeyboardButton(text="🔍 Распознать дефекты"), KeyboardButton(text="🕹 Мини-игра")],
        [KeyboardButton(text="📖 О нас"), KeyboardButton(text="💼 Партнёры")],
        [KeyboardButton(text="📩 Обратная связь"), KeyboardButton(text="📝 Регистрация")],
        [KeyboardButton(text="📜 Пользовательское соглашение"), KeyboardButton(text="🔒 Политика конфиденциальности")],
        [KeyboardButton(text="🎁 Бонусная система"), KeyboardButton(text="💵 Баланс бонусов")],
        [KeyboardButton(text="📞 Контакты"), KeyboardButton(text="👥 Команда")]
    ],
    resize_keyboard=True
)

keyboard_policy = InlineKeyboardMarkup(inline_keyboard=[
            [InlineKeyboardButton(text="Согласиться", callback_data="accept_privacy_policy")],
            [InlineKeyboardButton(text="Ознакомиться с политикой конфиденциальности",
                                  callback_data="view_privacy_policy")]])

keyboard_start_test = [
                [InlineKeyboardButton(text="▶️ Приступить к тесту", callback_data="start_test")]
            ]

keyboard_go_back = [
                [InlineKeyboardButton(text="⬅️ Назад", callback_data="previous"),
                 InlineKeyboardButton(text="Вперёд ➡️", callback_data="next")]
            ]