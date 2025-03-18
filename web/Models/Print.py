from sqlalchemy import Column, Integer, String, ForeignKey, ARRAY
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.future import select
from sqlalchemy.orm import declarative_base, relationship
from marshmallow import Schema, fields, validate
from database import DataBase

class Print(DataBase):
    __tablename__ = 'print'

    id = Column(Integer, primary_key=True, index=True)
    printer_id = Column(Integer, ForeignKey('printer.id'), nullable=False)
    defect = Column(ARRAY(Integer), nullable=False)  # Изменили на массив целых чисел
    img_path = Column(String(127), nullable=False)
    quality = Column(Integer, nullable=False)

    def __init__(self, printer_id, defect, img_path, quality):
        self.printer_id = printer_id
        self.defect = defect
        self.img_path = img_path
        self.quality = quality

    def __repr__(self):
        return f'<Print {self.id}>'

class PrintSchema(Schema):
    id = fields.Integer(dump_only=True)
    printer_id = fields.Integer(required=True, validate=validate.Range(min=1))
    defect = fields.List(fields.Integer(), allow_none=True)  # Теперь это список целых чисел
    img_path = fields.String(dump_only=True)
    quality = fields.Integer(required=True, validate=validate.Range(min=1))
