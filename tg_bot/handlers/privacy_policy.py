from aiogram import Router, types
from aiogram.types import FSInputFile
from config import PDF_PATH_1

router = Router()

@router.message(lambda message: message.text == "🔒 Политика конфиденциальности")
async def send_privacy_policy(message: types.Message):
    file_path = f"{PDF_PATH_1}"
    await message.answer_document(FSInputFile(file_path), caption="Политика в отношении обработки персональных данных")