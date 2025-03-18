from aiogram import Router, types
from aiogram.fsm.context import FSMContext
from utils.utils_team import send_team

router = Router()


@router.message(lambda message: message.text == "👥 Команда")
async def team(message: types.Message, state: FSMContext):
    # Сбрасываем состояние инструкции при новом запуске
    await state.update_data(photo_team_index=1, max_team_index=2, team_message=None)

    await send_team(message, state)


@router.callback_query(lambda c: c.data in ["next_team", "previous_team"])
async def team_navigation(callback_query: types.CallbackQuery, state: FSMContext):
    data = await state.get_data()
    photo_team_index = data.get("photo_team_index")
    max_team_index = data.get("max_team_index")

    if callback_query.data == "previous_team" and photo_team_index > 1:
        photo_team_index -= 1
    elif callback_query.data == "next_team" and photo_team_index < max_team_index:
        photo_team_index += 1

    await state.update_data(photo_team_index=photo_team_index)

    await send_team(callback_query.message, state)  # Вызов функции отправки инструкции
    await callback_query.answer()  # Подтверждаем обработку callback
