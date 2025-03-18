from sqlalchemy import Column, Integer, String, Boolean
from src.Config.db import Base


class Imagepicker(Base):
    __tablename__ = 'imagepicker'
    id = Column(Integer, primary_key=True)
    uid = Column(String, nullable=False)
    userUid = Column(String, nullable=False)
    defect_0 = Column(Boolean, nullable=False)
    defect_1 = Column(Boolean, nullable=False)
    defect_2 = Column(Boolean, nullable=False)
    defect_3 = Column(Boolean, nullable=False)
    defect_4 = Column(Boolean, nullable=False)
    defect_5 = Column(Boolean, nullable=False)
    defect_6 = Column(Boolean, nullable=False)
    defect_7 = Column(Boolean, nullable=False)
