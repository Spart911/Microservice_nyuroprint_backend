from sqlalchemy import Column, Integer
from database import DataBase

class Feedback(DataBase):
    __tablename__ = "feedback"
    id = Column(Integer, primary_key=True, index=True)
    rating = Column(Integer, nullable=False)