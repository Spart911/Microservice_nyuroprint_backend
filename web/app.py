from contextlib import asynccontextmanager
from fastapi import FastAPI, UploadFile, File, Depends, Form, HTTPException
from fastapi.middleware.cors import CORSMiddleware
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
import uvicorn
from Controllers.PrinterController import PrinterController
from Controllers.PrintController import PrintController
from Models.Printer import Printer
from Models.Print import Print
from database import DataBase, AsyncSessionLocal, engine, get_db  # Импорт необходимых объектов для работы с БД
from fastapi.responses import JSONResponse
from pydantic import BaseModel
from contextlib import asynccontextmanager
from Controllers.FeedbackController import FeedbackController

# Определяем папку для загрузки файлов
UPLOAD_FOLDER = '/uploads'

# Функция жизненного цикла приложения
@asynccontextmanager
async def lifespan(app: FastAPI):
    async with engine.begin() as conn:
        # Создание всех таблиц в БД, если их нет
        await conn.run_sync(DataBase.metadata.create_all)

    async with AsyncSessionLocal() as session:
        # Проверяем, есть ли принтеры в БД, если нет — создаем стандартные
        result = await session.execute(select(Printer))
        if not result.scalars().first():
            await PrinterController.create_default_printers(session)
        await session.commit()

    yield  # Пауза в контексте жизненного цикла (ожидание завершения работы приложения)

    await engine.dispose()  # Закрываем соединение с БД при завершении работы

# Создаем экземпляр FastAPI с указанным жизненным циклом
app = FastAPI(lifespan=lifespan)

# Настройка CORS для разрешения запросов с указанных доменов
app.add_middleware(
    CORSMiddleware,
    # Подправить !
    allow_origins=["https://nyuroprint.vercel.app", "https://nyuroprint.ru"],  # Разрешенные источники
    allow_credentials=True,
    allow_methods=["*"],  # Разрешаем все методы (GET, POST, PUT, DELETE и др.)
    allow_headers=["*"],  # Разрешаем все заголовки
)

# Middleware для Content Security Policy (CSP), обеспечивающий безопасность запросов
@app.middleware("http")
async def add_csp_header(request, call_next):
    response = await call_next(request)  # Обрабатываем запрос и получаем ответ
    csp = (
        "upgrade-insecure-requests; default-src 'self'; script-src 'self' 'unsafe-inline' "
        "'unsafe-eval'; style-src 'self' 'unsafe-inline'; img-src 'self' data:; "
        "connect-src 'self' http: https:;"
    )
    response.headers['Content-Security-Policy'] = csp  # Добавляем заголовок CSP
    return response

# =================== Роуты для работы с принтерами ===================

# Получение списка всех принтеров
@app.get("/api/printers/")
async def get_printers(session: AsyncSession = Depends(get_db)):
    return await PrinterController.get_printers(session)

# Добавление нового принтера
@app.post("/api/printers/")
async def add_printer(printer_data: dict, session: AsyncSession = Depends(get_db)):
    return await PrinterController.add_printer(session, printer_data)

# Получение информации о конкретном принтере по его ID
@app.get("/api/printers/{item_id}")
async def get_printer(item_id: int, session: AsyncSession = Depends(get_db)):
    return await PrinterController.get_printer(session, item_id)

# =================== Роуты для работы с печатями ===================

# Получение списка всех печатей
@app.get("/api/prints/")
async def get_prints(session: AsyncSession = Depends(get_db)):
    return await PrintController.get_prints(session)

# Добавление новой печати
@app.post("/api/prints/")
async def add_print(
    session: AsyncSession = Depends(get_db),
    img: UploadFile = File(...),  # Ожидаем, что файл будет передан через форму
    printer_id: int = Form(...),  # Ожидаем, что ID принтера будет передан через форму
    quality: int = Form(...)  # Ожидаем, что качество будет передано через форму
):
    return await PrintController.add_print(
        img=img,  # Передаем файл
        printer_id=printer_id,  # Передаем ID принтера
        quality=quality,  # Передаем качество
        session=session,  # Передаем сессию базы данных
        upload_folder = UPLOAD_FOLDER
    )


# Получение информации о конкретной печати по её ID
@app.get("/api/prints/{item_id}")
async def get_print(item_id: int, session: AsyncSession = Depends(get_db)):
    return await PrintController.get_print(session, item_id)

# =================== Роуты для работы с отзывами ===================

# Модель запроса для отправки отзыва
class FeedbackRequest(BaseModel):
    rating: int  # Оценка от пользователя

# Модель ответа с информацией об отзыве
class FeedbackResponse(BaseModel):
    id: int  # ID отзыва
    rating: int  # Оценка

    class Config:
        orm_mode = True  # Разрешаем работу с ORM-моделями

# Добавление нового отзыва
@app.post("/api/feedback/", response_model=dict)
async def add_feedback(feedback: FeedbackRequest, session: AsyncSession = Depends(get_db)):
    return await FeedbackController.add_feedback(feedback.rating, session)

# Получение списка всех отзывов
@app.get("/api/feedback/", response_model=list[FeedbackResponse])
async def get_feedbacks(session: AsyncSession = Depends(get_db)):
    return await FeedbackController.get_feedbacks(session)
