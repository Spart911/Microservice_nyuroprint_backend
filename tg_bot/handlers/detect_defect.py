from aiogram import Router, types, F
from aiogram.fsm.context import FSMContext
from aiogram.utils.keyboard import InlineKeyboardBuilder
import aiohttp
from aiohttp import FormData

from class_states import DefectRecognition
from config import bot, DETECT_API, quality_options, default_printers
from utils.utils_privacy_policy_status import check_privacy_policy_status

router = Router()

# Словарь дефектов с их названиями и рекомендациями по устранению
defect_names_and_fixes = {
    0: ("*Недоэкструзия*\n",
        "➜ **Увеличьте температуру сопла** \n"
        "➜ **Проверьте, нет ли засора в экструдере** \n"
        "➜ **Убедитесь, что филамент подается без затруднений** \n"
        "➜ **Проверьте калибровку подачи филамента** "),
    1: ("*Переэкструзия*\n",
        "➜ **Уменьшите температуру сопла** \n"
        "➜ **Снизьте скорость печати** \n"
        "➜ **Проверьте калибровку подачи филамента** "),
    2: ("*Сопли*\n",
        "➜ **Включите ретракт (откат) филамента** \n"
        "➜ **Увеличьте скорость перемещения без экструзии** \n"
        "➜ **Проверьте температуру сопла** "),
    3: ("*Отлипание*\n",
        "➜ **Улучшите адгезию к столу (используйте клей, лак, подогрев)** \n"
        "➜ **Проверьте калибровку стола** \n"
        "➜ **Уменьшите начальную скорость печати** "),
    4: ("*Пузыри*\n",
        "➜ **Просушите филамент** \n"
        "➜ **Уменьшите температуру сопла** \n"
        "➜ **Проверьте качество филамента** "),
    5: ("*Расслоение*\n",
        "➜ **Увеличьте температуру сопла** \n"
        "➜ **Уменьшите скорость печати** \n"
        "➜ **Убедитесь, что охлаждение не слишком сильное** "),
    6: ("*Волнистость*\n",
        "➜ **Проверьте натяжение ремней** \n"
        "➜ **Снизьте скорость печати** \n"
        "➜ **Уменьшите вибрации принтера** ")
}


@router.message(F.text == "🔍 Распознать дефекты")
async def recognize_defects(message: types.Message, state: FSMContext):
    user_id = message.from_user.id
    privacy_status = await check_privacy_policy_status(user_id)

    if privacy_status == 0:
        keyboard = types.InlineKeyboardMarkup(inline_keyboard=[
            [types.InlineKeyboardButton(text="Согласиться", callback_data="accept_privacy_policy")],
            [types.InlineKeyboardButton(text="Ознакомиться с политикой конфиденциальности",
                                        callback_data="view_privacy_policy")]
        ])
        await message.answer("Вы должны согласиться с политикой конфиденциальности перед отправкой сообщения.",
                             reply_markup=keyboard)
        return
    elif privacy_status == 2:
        await message.answer("Для использования этой функции необходимо зарегистрироваться.")
        return

    printer_kb = InlineKeyboardBuilder()
    for printer in default_printers[1:]:
        printer_kb.row(types.InlineKeyboardButton(text=printer["name"], callback_data=f"printer_{printer['id']}"))

    await message.answer("Выберите ваш 3D-принтер:", reply_markup=printer_kb.as_markup())
    await state.set_state(DefectRecognition.printer)


@router.callback_query(F.data.startswith("printer_"))
async def process_printer_selection(callback: types.CallbackQuery, state: FSMContext):
    printer_id = callback.data.split("_")[1]
    await state.update_data(printer_id=printer_id)

    quality_kb = InlineKeyboardBuilder()
    for quality in quality_options:
        quality_kb.row(types.InlineKeyboardButton(text=quality, callback_data=f"quality_{quality}"))

    await callback.message.edit_text("Выберите качество печати:", reply_markup=quality_kb.as_markup())
    await state.set_state(DefectRecognition.quality)
    await callback.answer()


@router.callback_query(F.data.startswith("quality_"))
async def process_quality_selection(callback: types.CallbackQuery, state: FSMContext):
    quality = callback.data.split("quality_")[1]
    await state.update_data(quality=quality_options.get(quality, 1))

    await callback.message.edit_text("Загрузите фото напечатанной на 3D принтере детали.")
    await state.set_state(DefectRecognition.photo)
    await callback.answer()


@router.message(DefectRecognition.photo, F.photo)
async def process_photo_upload(message: types.Message, state: FSMContext):
    loading_message = await message.answer("⏳ *Обрабатываю фото...*", parse_mode="Markdown")
    try:
        photo = message.photo[-1]
        file_info = await bot.get_file(photo.file_id)
        file = await bot.download_file(file_info.file_path)

        data = await state.get_data()
        printer_id = data.get("printer_id")
        quality = data.get("quality", 1)

        form_data = FormData()
        form_data.add_field('printer_id', str(printer_id))
        form_data.add_field('quality', str(quality))
        form_data.add_field('img', file, filename='photo.jpg')

        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(f"{DETECT_API}/api/prints/", data=form_data) as response:
                if response.status == 200:
                    result = await response.json()
                    detected_defects = result.get("defect", [])
                    if detected_defects:
                        await message.answer("🔴 *Обнаружены дефекты:*", parse_mode="Markdown")
                        for defect_code in detected_defects:
                            defect_name, fix = defect_names_and_fixes.get(defect_code,
                                                                          ("Неизвестный дефект", "Нет решения"))
                            await message.answer(f"**{defect_name}**\n{fix}", parse_mode="Markdown")

                        # Восстановленная клавиатура для оценки
                        feedback_kb = InlineKeyboardBuilder()
                        feedback_kb.row(
                            types.InlineKeyboardButton(text="👍", callback_data="rate_5"),
                            types.InlineKeyboardButton(text="🙂", callback_data="rate_4"),
                            types.InlineKeyboardButton(text="😐", callback_data="rate_3"),
                            types.InlineKeyboardButton(text="🙁", callback_data="rate_2"),
                            types.InlineKeyboardButton(text="👎", callback_data="rate_1")
                        )
                        await message.answer("Пожалуйста, оцените работу бота:", reply_markup=feedback_kb.as_markup())
                    else:
                        await message.answer("✅ *Дефектов не обнаружено!*", parse_mode="Markdown")
                else:
                    await message.answer("❌ *Ошибка при обработке фото.*", parse_mode="Markdown")
    except Exception as e:
        await message.answer(f"⚠ *Ошибка:* {e}", parse_mode="Markdown")
    finally:
        await bot.delete_message(chat_id=loading_message.chat.id, message_id=loading_message.message_id)
        await state.clear()


@router.callback_query(F.data.startswith("rate_"))
async def process_rating(callback: types.CallbackQuery):
    rating = int(callback.data.split("_")[1])
    try:
        async with aiohttp.ClientSession(connector=aiohttp.TCPConnector(ssl=False)) as session:
            async with session.post(f"{DETECT_API}/api/feedback/", json={"rating": rating}) as response:
                if response.status == 200:
                    await callback.answer("Спасибо за вашу оценку!")
                else:
                    await callback.answer("Не удалось отправить оценку. Попробуйте еще раз.")
    except Exception as e:
        await callback.answer(f"Ошибка: {e}")
