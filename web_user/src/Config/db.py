from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base
from dotenv import load_dotenv
import os

load_dotenv()

DATABASE_URL = (f"{os.getenv('DB_DRIVER')}://{os.getenv('DB_USER')}:{os.getenv('DB_PASSWORD')}@"
                f"{os.getenv('DB_HOST')}:{os.getenv('DB_PORT')}/{os.getenv('DB_NAME')}")

# Создаем асинхронный движок для подключения к базе данных
engine = create_async_engine(DATABASE_URL, echo=True)

# Создаем асинхронную фабрику сессий для работы с базой данных
AsyncSessionLocal = sessionmaker(
    class_=AsyncSession,
    expire_on_commit=False
)

# Базовый класс для моделей
Base = declarative_base()


# Получение сессии
async def get_session():
    async with AsyncSessionLocal(bind=engine) as session:
        yield session