from sqlalchemy import Column, Integer, String, Boolean
from src.Config.db import Base


class User(Base):
    __tablename__ = 'users'

    id = Column(Integer, primary_key=True)
    id_telegram = Column(String(50), unique=True, nullable=False)
    amount_bonuses = Column(Integer, nullable=False)
    email = Column(String(50), unique=True, nullable=False)
    password= Column(String(50), unique=False, nullable=False)
    privacy_policy_accepted = Column(Boolean, default=False, nullable=False)

