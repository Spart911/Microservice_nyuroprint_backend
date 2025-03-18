from fastapi import APIRouter, HTTPException, Depends
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from src.Config.db import get_session
from src.Schemas.UserSchemas import UserInput, UserOutput, UpdatePrivacyPolicyStatus
from src.Models.User import User
from sqlalchemy.exc import IntegrityError
import logging

router = APIRouter()


@router.post("/users/", response_model=UserOutput)
async def create_user(user: UserInput, db: AsyncSession = Depends(get_session)):
    logging.debug(f"Attempting to create user with id_telegram: {user.id_telegram}, email: {user.email}")

    # Проверка, существует ли уже пользователь с таким email
    async with db.begin():
        result = await db.execute(select(User).filter(User.email == user.email))
        existing_user = result.scalars().first()

    if existing_user:
        raise HTTPException(status_code=400, detail="Email already registered")

    # Создание нового пользователя
    new_user = User(
        id_telegram=user.id_telegram,
        amount_bonuses=user.amount_bonuses,
        email=user.email,
        password=user.password,
    )

    async with db.begin():
        db.add(new_user)
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=401, detail="Failed to create user")

    return new_user


@router.get("/users/{user_id}", response_model=UserOutput)
async def get_user(user_id: int, db: AsyncSession = Depends(get_session)):
    # Поиск пользователя по id
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.get("/users/telegram/{id_telegram}", response_model=UserOutput)
async def get_user_by_telegram(id_telegram: str, db: AsyncSession = Depends(get_session)):
    # Поиск пользователя по id_telegram
    async with db.begin():
        result = await db.execute(select(User).filter(User.id_telegram == id_telegram))
        user = result.scalars().first()

    if user is None:
        raise HTTPException(status_code=404, detail="User not found")

    return user

@router.put("/users/{user_id}", response_model=UserOutput)
async def update_user(user_id: int, user: UserInput, db: AsyncSession = Depends(get_session)):
    # Поиск пользователя по id
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == user_id))
        existing_user = result.scalars().first()

    if not existing_user:
        raise HTTPException(status_code=404, detail="User not found")

    # Обновление данных пользователя
    existing_user.id_telegram = user.id_telegram
    existing_user.amount_bonuses = user.amount_bonuses
    existing_user.email = user.email
    existing_user.password = user.password

    async with db.begin():
        try:
            await db.commit()
        except IntegrityError:
            await db.rollback()
            raise HTTPException(status_code=400, detail="Failed to update user")

    return existing_user


@router.delete("/users/{user_id}", response_model=UserOutput)
async def delete_user(user_id: int, db: AsyncSession = Depends(get_session)):
    # Поиск пользователя по id
    async with db.begin():
        result = await db.execute(select(User).filter(User.id == user_id))
        user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Удаление пользователя
    async with db.begin():
        await db.delete(user)
        await db.commit()

    return user

@router.put("/users/telegram/{id_telegram}/set-bonuses", response_model=UserOutput)
async def set_user_bonuses(id_telegram: str, amount: int, db: AsyncSession = Depends(get_session)):
    """
    Устанавливает указанное количество бонусов для пользователя по id_telegram.
    """
    # Ищем пользователя по id_telegram
    result = await db.execute(select(User).filter(User.id_telegram == id_telegram))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Устанавливаем новое количество бонусов
    user.amount_bonuses = amount

    try:
        await db.commit()
        await db.refresh(user)  # Обновляем объект пользователя
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось обновить бонусы пользователя")

    return user

@router.put("/users/telegram/{id_telegram}/increment-bonus", response_model=UserOutput)
async def increment_user_bonus(id_telegram: str, db: AsyncSession = Depends(get_session)):
    """
    Увеличивает количество бонусов пользователя на 1 по id_telegram.
    """
    # Ищем пользователя по id_telegram без начала транзакции
    result = await db.execute(select(User).filter(User.id_telegram == id_telegram))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Увеличиваем количество бонусов на 1
    user.amount_bonuses += 1

    # Теперь начинаем транзакцию для сохранения изменений
    try:
        await db.commit()
    except IntegrityError:
        await db.rollback()
        raise HTTPException(status_code=400, detail="Не удалось обновить бонусы пользователя")

    return user


@router.get("/users/telegram/{id_telegram}/bonuses", response_model=int)
async def get_user_bonuses(id_telegram: str, db: AsyncSession = Depends(get_session)):
    """
    Получает количество бонусов пользователя по id_telegram.
    """
    # Ищем пользователя по id_telegram
    result = await db.execute(
        select(User).filter(User.id_telegram == id_telegram)
    )
    user = result.scalars().first()

    # Проверяем, найден ли пользователь
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Возвращаем количество бонусов
    return user.amount_bonuses

@router.put("/update-privacy-policy-status/{id_telegram}", response_model=UserOutput)
async def update_privacy_policy_status(id_telegram: str, db: AsyncSession = Depends(get_session)):
    """
    Обновляет статус согласия с политикой конфиденциальности по id_telegram и устанавливает его в True.
    """
    # Ищем пользователя по id_telegram
    result = await db.execute(select(User).where(User.id_telegram == id_telegram))
    user = result.scalars().first()

    # Если пользователь не найден, возвращаем ошибку 404
    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    # Устанавливаем значение privacy_policy_accepted в True
    user.privacy_policy_accepted = True
    await db.commit()  # Применяем изменения в базе данных
    await db.refresh(user)  # Обновляем объект пользователя с новыми данными

    return user  # Возвращаем обновленные данные пользователя


@router.get("/get-privacy-policy-status/{id_telegram}", response_model=UpdatePrivacyPolicyStatus)
async def get_privacy_policy_status(id_telegram: str, db: AsyncSession = Depends(get_session)):
    """
    Получает статус согласия с политикой конфиденциальности по id_telegram.
    """
    # Ищем пользователя по id_telegram
    result = await db.execute(select(User).where(User.id_telegram == id_telegram))
    user = result.scalars().first()

    if not user:
        raise HTTPException(status_code=404, detail="Пользователь не найден")

    return {"id_telegram": user.id_telegram, "privacy_policy_accepted": user.privacy_policy_accepted}
