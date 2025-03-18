from aiogram import Router, types
from aiogram.types import FSInputFile
from config import TEAM_PNG_PATH

router = Router()

@router.message(lambda message: message.text == "📖 О нас")
async def about_us(message: types.Message):
    # Загружаем изображение
    photo = FSInputFile(f"{TEAM_PNG_PATH}")
    await message.answer_photo(photo=photo)

    # Отправляем описание
    description = (
        "Мы компания NyuroPrint, которая разрабатывает интеллектуальную систему "
        "для автоматического обнаружения и устранения дефектов в 3D-печати. Наша "
        "альфа-версия уже успешно распознает ключевые дефекты, возникающие в процессе "
        "FDM-печати, и мы активно работаем над созданием механизма их автоматического исправления."
        " Работа выполнена при поддержке гранта Фонда содействия инновациям, предоставленного в рамках программы «Студенческий стартап» федерального проекта «Платформа университетского технологического предпринимательства»."
    )
    await message.answer(description)
