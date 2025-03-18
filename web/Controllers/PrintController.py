import os
import uuid
import aiofiles
import aiohttp
import numpy as np
from fastapi import HTTPException, UploadFile, Form, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from Models.Print import Print, PrintSchema
from database import get_db
from torchvision import transforms
from PIL import Image
import asyncio
import io

TRITON_URL = "http://triton_inference_server:8000/v2/models/defect_detection_model/infer"
THRESHOLDS = np.array([0.00765891, 0.08482563, 0.04003922, 0.12988287, 0.01532748, 0.07293494, 0.01747844])

class PrintController:
    # Разрешённые расширения файлов изображений
    ALLOWED_EXTENSIONS = {'png', 'jpg', 'jpeg'}

    @staticmethod
    def allowed_file(filename: str) -> bool:
        """
        Проверяет, является ли файл изображением с допустимым расширением
        """
        return '.' in filename and filename.rsplit('.', 1)[1].lower() in PrintController.ALLOWED_EXTENSIONS

    @staticmethod
    async def get_prints(session: AsyncSession):
        """
        Получает список всех записей о печати из базы данных
        """
        try:
            result = await session.execute(select(Print))
            prints = result.scalars().all()
            print_schema = PrintSchema(many=True)
            return {"message": "OK", "data": print_schema.dump(prints)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_print(session: AsyncSession, item_id: int):
        """
        Получает конкретную запись о печати по её ID
        """
        try:
            result = await session.execute(select(Print).filter(Print.id == item_id))
            selected_print = result.scalar_one_or_none()
            if not selected_print:
                raise HTTPException(status_code=404, detail="Print not found")
            print_schema = PrintSchema()
            return {"message": "OK", "data": print_schema.dump(selected_print)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def add_print(
            img: UploadFile,
            printer_id: int = Form(...),
            quality: int = Form(...),
            session: AsyncSession = Depends(get_db),
            upload_folder: str = "/uploads"  # Папка для загрузки изображений
    ):
        """
        Добавляет новую запись о печати:
        - Сохраняет изображение в файловой системе
        - Отправляет его на обработку в сервис определения дефектов
        - Создаёт запись в базе данных
        """
        # Проверяем, что файл загружен и имеет допустимый формат
        if not img or img.filename == "":
            raise HTTPException(status_code=400, detail="No selected image")

        if not PrintController.allowed_file(img.filename):
            raise HTTPException(status_code=400, detail="Invalid img type")

        # Безопасное имя файла
        filename = PrintController.secure_filename(img.filename)
        filepath = os.path.join(upload_folder, filename)

        try:
            # Генерация уникального имени файла, если такое уже существует
            while os.path.exists(filepath):
                name, ext = filename.rsplit('.', 1)
                unique_id = str(uuid.uuid4())
                filename = f"{name}_{unique_id}.{ext}"
                filepath = os.path.join(upload_folder, filename)

            # Асинхронное сохранение файла на диск
            async with aiofiles.open(filepath, 'wb') as f:
                content = await img.read()
                await f.write(content)

            # Преобразование изображения
            transform = transforms.Compose([
                transforms.Resize((500, 500)),
                transforms.ToTensor(),
                transforms.Normalize(mean=[0.485, 0.456, 0.406], std=[0.229, 0.224, 0.225])
            ])

            image_bytes = io.BytesIO(content)
            image = Image.open(image_bytes).convert("RGB")
            image = transform(image).unsqueeze(0)  # Преобразование изображения
            image_data = image.numpy().flatten().tolist()

            data = {
                "inputs": [{
                    "name": "input__0",
                    "shape": [1, 3, 500, 500],
                    "datatype": "FP32",
                    "data": image_data
                }]
            }

            # Асинхронный запрос к Triton
            async with aiohttp.ClientSession() as session_aiohttp:
                async with session_aiohttp.post(TRITON_URL, json=data) as response:
                    if response.status == 200:
                        result = await response.json()
                        output_data = result['outputs'][0]['data']
                        probabilities = 1 / (1 + np.exp(-np.array(output_data)))
                        detected_classes = [i for i, prob in enumerate(probabilities) if prob > THRESHOLDS[i]]
                        is_defected_image = np.array(detected_classes)
                    else:
                        is_defected_image = np.array([])

            print(f"Ответ от triton_inference_server : {is_defected_image}")

            # Создание записи в базе данных
            new_print = Print(
                printer_id=printer_id,
                defect=is_defected_image.tolist(),
                img_path=filepath,
                quality=quality
            )
            session.add(new_print)
            await session.commit()

            return {
                "message": "Print added successfully",
                "print_id": new_print.id,
                "defect": is_defected_image.tolist()
            }


        except Exception as e:
            print(f"Ошибка при обработке изображения: {str(e)}")

            # Откат транзакции для базы данных
            if session:
                await session.rollback()

            # Удаление файла в случае ошибки
            if os.path.exists(filepath):
                os.remove(filepath)

            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    def secure_filename(filename: str) -> str:
        """
        Преобразует имя файла в безопасный формат:
        - Заменяет пробелы на подчёркивания
        - Удаляет все символы, кроме букв, цифр и ._-
        """
        filename = filename.replace(" ", "_")
        filename = "".join(c for c in filename if c.isalnum() or c in "._-")
        return filename
