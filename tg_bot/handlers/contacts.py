from aiogram import Router, types

router = Router()

@router.message(lambda message: message.text == "📞 Контакты")
async def send_contact(message: types.Message):
    await message.answer(
        "*📞 Контакты*\n\n"
        "📱 *Номер:* +79930811885\n"
        "📧 *Почта:* nyuroprint@yandex.ru\n"
        "📍 *Адрес:* г. Ростов-на-Дону, Ростовская обл.\n"
        "🏢 *Почтовый индекс:* 344000",
        parse_mode="Markdown"
    )
