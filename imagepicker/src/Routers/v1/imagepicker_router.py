from fastapi import APIRouter, HTTPException, Depends, Form, Query
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.Config.db import get_session
from src.Models.Imagepicker import Imagepicker
from sqlalchemy.exc import IntegrityError
from starlette.responses import FileResponse, StreamingResponse
from pathlib import Path
import logging
import random
import os
import csv
import pandas as pd
from io import StringIO
from src.Schemas.ImagepickerSchemas import ProcessTestInput, ProcessTestOutput, DefectCountOutput
from sqlalchemy import func
from dotenv import load_dotenv

# Configure logging
logging.basicConfig(level=logging.INFO)
logger = logging.getLogger(__name__)

load_dotenv()

router = APIRouter()

MAIN_FOLDER = Path(os.getenv('PATH_DATA'))
READY_DATA_FOLDER = Path(os.getenv('PATH_READY_DATA_DATA'))
VALIDATION_MARKUP_FILE = Path(os.getenv('PATH_READY_DATA_MARKUP'))

os.makedirs(MAIN_FOLDER, exist_ok=True)

# Загрузка файла с разметкой для валидации
try:
    validation_data = pd.read_csv(VALIDATION_MARKUP_FILE)
    validation_images = list(validation_data['uid'].unique()) if 'uid' in validation_data.columns else []
    logger.info(f"Loaded {len(validation_images)} validation images from markup.csv")
except Exception as e:
    logger.error(f"Error loading validation data: {e}")
    validation_images = []

defect_types = [5, 0, 6, 2, 7, 3, 1, 4]


@router.get("/get-test")
async def get_random_image():
    logger.info("Received request for a random image.")

    # С вероятностью 20% предлагаем валидационное изображение
    use_validation = random.random() < 0.2 and validation_images

    if use_validation:
        # Выбираем случайное валидационное изображение
        random_validation_image = random.choice(validation_images)
        logger.info(f"Selected validation image: {random_validation_image}")
        return {"uid": random_validation_image}
    else:
        # Стандартная логика выбора обычного изображения
        files = list(MAIN_FOLDER.glob("*.*"))
        if not files:
            logger.error("No images found in the main folder.")
            raise HTTPException(status_code=404, detail="No images found in the main folder.")

        random_photo = random.choice(files)
        logger.info(f"Selected random image: {random_photo.name}")
        return {"uid": random_photo.name}


@router.get("/photo/{uid}")
async def serve_photo(uid: str):
    logger.info(f"Received request to serve photo with uid: {uid}")

    # Проверяем, является ли это валидационным изображением
    is_validation = uid in validation_images

    if is_validation:
        file_path = READY_DATA_FOLDER / uid
    else:
        file_path = MAIN_FOLDER / uid

    if not file_path.exists():
        logger.error(f"Photo not found: {uid}")
        raise HTTPException(status_code=404, detail="Photo not found.")

    logger.info(f"Serving photo: {uid}")
    return FileResponse(file_path)


@router.post("/process-test", response_model=ProcessTestOutput)
async def process_test(
        input_data: ProcessTestInput,
        session: AsyncSession = Depends(get_session)
):
    logger.info(f"Processing test for userUid: {input_data.userUid}, uid: {input_data.uid}")

    # Проверяем, является ли это валидационным изображением
    is_validation = input_data.uid in validation_images

    # Если это валидационное изображение, модифицируем userUid для сохранения
    modified_user_uid = f"{input_data.userUid}_val" if is_validation else input_data.userUid

    # Задаём дефолтные значения для всех дефектов (от 0 до 7)
    defect_data = {f"defect_{i}": False for i in range(8)}

    # Проверяем, есть ли переданные дефекты
    target_defects = []
    if input_data.target:
        try:
            target_defects = [int(t) for t in input_data.target.split(",")]
            logger.debug(f"Parsed target defects: {target_defects}")
        except ValueError:
            logger.error("Invalid target format. Should be a comma-separated list of integers.")
            raise HTTPException(status_code=400, detail="Target should be a comma-separated list of integers.")

        # Проверяем, что дефекты в допустимом диапазоне (от 0 до 7)
        if any(t < 0 or t > 7 for t in target_defects):
            logger.error(f"Invalid defect type in target: {target_defects}")
            raise HTTPException(status_code=400, detail="Defect numbers must be in range 0-7.")

        # Если это валидационное изображение, сравниваем с эталоном
        if is_validation:
            # Получаем эталонную разметку для этого изображения
            validation_row = validation_data[validation_data['uid'] == input_data.uid]
            if not validation_row.empty:
                # Для каждого дефекта проверяем совпадение с эталоном
                for i in range(8):
                    defect_col = f"defect_{i}"
                    if defect_col in validation_row.columns:
                        # Проверяем совпадение: был ли выбран дефект пользователем и есть ли он в эталоне
                        user_selected = i in target_defects
                        validation_has_defect = validation_row[defect_col].iloc[0]

                        # True если совпадает (оба True или оба False), иначе False
                        defect_data[defect_col] = user_selected == validation_has_defect
                        logger.debug(
                            f"Validation for {defect_col}: user={user_selected}, validation={validation_has_defect}, match={defect_data[defect_col]}")
                    else:
                        logger.warning(f"Column {defect_col} not found in validation data for image {input_data.uid}")
            else:
                logger.warning(f"Validation image {input_data.uid} not found in validation data")
        else:
            # Если не валидационное изображение, сохраняем выбранные пользователем дефекты
            for t in target_defects:
                defect_data[f"defect_{t}"] = True

    logger.debug(f"Final defect data for DB: {defect_data}")

    # Создаём запись с полными данными
    new_record = Imagepicker(
        uid=input_data.uid,  # Используем оригинальный uid
        userUid=modified_user_uid,  # Используем модифицированный userUid для валидационных изображений
        **defect_data  # Передаём все дефекты (по результатам сравнения для валидационных изображений)
    )
    session.add(new_record)
    logger.info(f"Added new record for uid: {modified_user_uid}")

    try:
        await session.commit()
        logger.info(f"Successfully committed new record for uid: {modified_user_uid}")
    except IntegrityError:
        await session.rollback()
        logger.error("Database error occurred while processing the request.")
        raise HTTPException(status_code=500, detail="Database error occurred while processing the request.")

    return {"status": "success", "uid": input_data.uid, "created": target_defects}


@router.get("/export-csv")
async def export_csv(session: AsyncSession = Depends(get_session)):
    logger.info("Exporting data to CSV.")
    query = select(Imagepicker)
    result = await session.execute(query)
    records = result.scalars().all()

    output = StringIO()
    writer = csv.writer(output)
    writer.writerow(
        ["id", "uid", "userUid", "defect_0", "defect_1", "defect_2", "defect_3", "defect_4", "defect_5", "defect_6",
         "defect_7"])

    for record in records:
        writer.writerow([
            record.id, record.uid, record.userUid,
            record.defect_0, record.defect_1, record.defect_2, record.defect_3,
            record.defect_4, record.defect_5, record.defect_6, record.defect_7
        ])
    logger.info("CSV data prepared.")

    output.seek(0)
    logger.info("Returning CSV file as response.")
    return StreamingResponse(output, media_type="text/csv",
                             headers={"Content-Disposition": "attachment; filename=imagepicker_data.csv"})


@router.get("/defect-count", response_model=DefectCountOutput)
async def get_defect_count(userUid: str = Query(...), session: AsyncSession = Depends(get_session)):
    logger.info(f"Counting records for userUid: {userUid}")

    query = select(func.count()).select_from(Imagepicker).where(Imagepicker.userUid == userUid)
    result = await session.execute(query)
    count = result.scalar()

    logger.info(f"Record count for userUid {userUid}: {count}")

    return {"count": count}