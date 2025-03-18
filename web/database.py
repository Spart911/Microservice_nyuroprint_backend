from sqlalchemy.ext.asyncio import AsyncSession, create_async_engine
from sqlalchemy.orm import sessionmaker, declarative_base

# Определение базового класса
DataBase = declarative_base()

DATABASE_URL = "postgresql+asyncpg://root:root@db:5432/PrintersProject"

# Создаем асинхронный движок и сессию
engine = create_async_engine(DATABASE_URL, echo=True)
AsyncSessionLocal = sessionmaker(engine, class_=AsyncSession, expire_on_commit=False)

# Функция для получения сессии
async def get_db() -> AsyncSession:
    async with AsyncSessionLocal() as session:
        yield session
