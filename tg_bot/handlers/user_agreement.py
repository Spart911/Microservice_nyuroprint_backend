from aiogram import Router, types
from aiogram.types import FSInputFile
from config import PDF_PATH_2

router = Router()

@router.message(lambda message: message.text == "📜 Пользовательское соглашение")
async def send_user_agreement(message: types.Message):
    file_path = f"{PDF_PATH_2}"
    await message.answer_document(FSInputFile(file_path), caption="Пользовательское соглашение")
