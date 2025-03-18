from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from Models.Feedback import Feedback
from fastapi import HTTPException

class FeedbackController:
    @staticmethod
    async def add_feedback(rating: int, session: AsyncSession):
        try:
            new_feedback = Feedback(rating=rating)
            session.add(new_feedback)
            await session.commit()
            return {"message": "Feedback submitted successfully"}
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_feedbacks(session: AsyncSession):
        try:
            result = await session.execute(select(Feedback))
            return result.scalars().all()
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))
