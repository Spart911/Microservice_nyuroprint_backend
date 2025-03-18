from fastapi import HTTPException
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy import select
from typing import List, Optional, Dict, Any
from Models.Printer import Printer, PrinterSchema
from pydantic import BaseModel
import logging


class PrinterCreate(BaseModel):
    name: str
    val_print_x: Optional[float] = None
    val_print_y: Optional[float] = None
    val_print_z: Optional[float] = None
    view_table: Optional[str] = None
    center_origin: Optional[bool] = None
    table_heating: Optional[bool] = None
    print_volume_heating: Optional[bool] = None
    type_g_code: Optional[str] = None
    min_x_head: Optional[float] = None
    min_y_head: Optional[float] = None
    max_x_head: Optional[float] = None
    max_y_head: Optional[float] = None
    height_portal: Optional[float] = None
    displace_extruder: Optional[bool] = None
    count_extruder: Optional[int] = None
    start_g_code: Optional[str] = None
    end_g_code: Optional[str] = None
    extr_1_nozzle_diameter: Optional[float] = None
    extr_1_filament_diameter: Optional[float] = None
    extr_1_nozzle_displacement_x: Optional[float] = None
    extr_1_nozzle_displacement_y: Optional[float] = None
    extr_1_fan_number: Optional[int] = None
    extr_1_start_g_code: Optional[str] = None
    extr_1_end_g_code: Optional[str] = None
    extr_2_nozzle_diameter: Optional[float] = None
    extr_2_filament_diameter: Optional[float] = None
    extr_2_nozzle_displacement_x: Optional[float] = None
    extr_2_nozzle_displacement_y: Optional[float] = None
    extr_2_fan_number: Optional[int] = None
    extr_2_start_g_code: Optional[str] = None
    extr_2_end_g_code: Optional[str] = None


class PrinterController:
    @staticmethod
    async def get_printers(session: AsyncSession):
        try:
            result = await session.execute(select(Printer))
            printers = result.scalars().all()
            printer_schema = PrinterSchema(many=True)
            return {"message": "OK", "data": printer_schema.dump(printers)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def get_printer(session: AsyncSession, item_id: int):
        try:
            result = await session.execute(
                select(Printer).filter(Printer.id == item_id)
            )
            printer = result.scalar_one_or_none()
            if not printer:
                raise HTTPException(status_code=404, detail="Printer not found")

            printer_schema = PrinterSchema()
            return {"message": "OK", "data": printer_schema.dump(printer)}
        except Exception as e:
            raise HTTPException(status_code=500, detail=str(e))

    @staticmethod
    async def add_printer(session: AsyncSession, printer_data: dict):
        try:
            # Преобразуем поля в нужные типы
            printer_dict = printer_data.copy()  # Создаём копию, чтобы не изменять оригинал
            if printer_dict.get("val_print_x") is not None:
                printer_dict["val_print_x"] = float(printer_dict["val_print_x"])

            if printer_dict.get("val_print_y") is not None:
                printer_dict["val_print_y"] = float(printer_dict["val_print_y"])

            if printer_dict.get("val_print_z") is not None:
                printer_dict["val_print_z"] = float(printer_dict["val_print_z"])

            if printer_dict.get("min_x_head") is not None:
                printer_dict["min_x_head"] = float(printer_dict["min_x_head"])

            if printer_dict.get("min_y_head") is not None:
                printer_dict["min_y_head"] = float(printer_dict["min_y_head"])

            if printer_dict.get("max_x_head") is not None:
                printer_dict["max_x_head"] = float(printer_dict["max_x_head"])

            if printer_dict.get("max_y_head") is not None:
                printer_dict["max_y_head"] = float(printer_dict["max_y_head"])

            if printer_dict.get("height_portal") is not None:
                printer_dict["height_portal"] = float(printer_dict["height_portal"])

            if printer_dict.get("extr_1_nozzle_diameter") is not None:
                printer_dict["extr_1_nozzle_diameter"] = float(printer_dict["extr_1_nozzle_diameter"])

            if printer_dict.get("extr_1_filament_diameter") is not None:
                printer_dict["extr_1_filament_diameter"] = float(printer_dict["extr_1_filament_diameter"])

            if printer_dict.get("extr_1_nozzle_displacement_x") is not None:
                printer_dict["extr_1_nozzle_displacement_x"] = float(printer_dict["extr_1_nozzle_displacement_x"])

            if printer_dict.get("extr_1_nozzle_displacement_y") is not None:
                printer_dict["extr_1_nozzle_displacement_y"] = float(printer_dict["extr_1_nozzle_displacement_y"])

            if printer_dict.get("extr_2_nozzle_diameter") is not None:
                printer_dict["extr_2_nozzle_diameter"] = float(printer_dict["extr_2_nozzle_diameter"])

            if printer_dict.get("extr_2_filament_diameter") is not None:
                printer_dict["extr_2_filament_diameter"] = float(printer_dict["extr_2_filament_diameter"])

            if printer_dict.get("extr_2_nozzle_displacement_x") is not None:
                printer_dict["extr_2_nozzle_displacement_x"] = float(printer_dict["extr_2_nozzle_displacement_x"])

            if printer_dict.get("extr_2_nozzle_displacement_y") is not None:
                printer_dict["extr_2_nozzle_displacement_y"] = float(printer_dict["extr_2_nozzle_displacement_y"])

            # Преобразуем булевы значения
            if printer_dict.get("center_origin") is not None:
                printer_dict["center_origin"] = bool(printer_dict["center_origin"])

            if printer_dict.get("table_heating") is not None:
                printer_dict["table_heating"] = bool(printer_dict["table_heating"])

            if printer_dict.get("print_volume_heating") is not None:
                printer_dict["print_volume_heating"] = bool(printer_dict["print_volume_heating"])

            if printer_dict.get("displace_extruder") is not None:
                printer_dict["displace_extruder"] = bool(printer_dict["displace_extruder"])

            # Преобразуем числовые значения
            if printer_dict.get("count_extruder") is not None:
                printer_dict["count_extruder"] = int(printer_dict["count_extruder"])

            # Создаём новый принтер из данных
            new_printer = Printer(**printer_dict)

            session.add(new_printer)
            await session.commit()
            await session.refresh(new_printer)

            return {
                "message": "Printer added successfully",
                "printer_id": new_printer.id
            }
        except InterruptedError as e:
            await session.rollback()
            logging.error(f"Database error: {str(e)}")
            raise HTTPException(status_code=409, detail="Printer already exists or violates constraints")
        except Exception as e:
            await session.rollback()
            logging.exception("Unexpected error while adding printer")
            raise HTTPException(status_code=500, detail="Internal server error")

    @staticmethod
    async def create_default_printers(session: AsyncSession):
        default_printers = [
            {
                "name": "Ender 3",
                "val_print_x": 200.0,
                "val_print_y": 200.0,
                "val_print_z": 200.0,
                "view_table": "Glass",
                "center_origin": True,
                "table_heating": False,
                "print_volume_heating": False,
                "type_g_code": "G-code",
                "min_x_head": 0.0,
                "min_y_head": 0.0,
                "max_x_head": 200.0,
                "max_y_head": 200.0,
                "height_portal": 100.0,
                "displace_extruder": False,
                "count_extruder": 1,
                "start_g_code": "Start G-code",
                "end_g_code": "End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 0.0,
                "extr_1_nozzle_displacement_y": 0.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Start G-code",
                "extr_1_end_g_code": "Extruder 1 End G-code",
                "extr_2_nozzle_diameter": None,
                "extr_2_filament_diameter": None,
                "extr_2_nozzle_displacement_x": None,
                "extr_2_nozzle_displacement_y": None,
                "extr_2_fan_number": None,
                "extr_2_start_g_code": None,
                "extr_2_end_g_code": None
            },
            {
                "name": "Creality Ender 5",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Anycubic i3 Mega",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Ultimaker S3",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Prusa SL1S",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Raise3D E2",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "MakerBot Replicator Z18",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Wanhao Duplicator 9",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Prusa MINI+",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "UlTi Steel 2",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "FlyingBear Ghost 5",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Creality CR-K1C",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Anycubic Kobra 2 Neo",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Creality K1",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "FlyingBear Ghost 6",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "ZAV-PRO V3",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
            ,
            {
                "name": "Biqu Hurakan",
                "val_print_x": 250.0,
                "val_print_y": 250.0,
                "val_print_z": 250.0,
                "view_table": "Aluminum",
                "center_origin": False,
                "table_heating": True,
                "print_volume_heating": True,
                "type_g_code": "Custom G-code",
                "min_x_head": 10.0,
                "min_y_head": 10.0,
                "max_x_head": 240.0,
                "max_y_head": 240.0,
                "height_portal": 120.0,
                "displace_extruder": True,
                "count_extruder": 2,
                "start_g_code": "Custom Start G-code",
                "end_g_code": "Custom End G-code",
                "extr_1_nozzle_diameter": 0.4,
                "extr_1_filament_diameter": 1.75,
                "extr_1_nozzle_displacement_x": 10.0,
                "extr_1_nozzle_displacement_y": 5.0,
                "extr_1_fan_number": 1,
                "extr_1_start_g_code": "Extruder 1 Custom Start G-code",
                "extr_1_end_g_code": "Extruder 1 Custom End G-code",
                "extr_2_nozzle_diameter": 0.4,
                "extr_2_filament_diameter": 1.75,
                "extr_2_nozzle_displacement_x": -10.0,
                "extr_2_nozzle_displacement_y": -5.0,
                "extr_2_fan_number": 2,
                "extr_2_start_g_code": "Extruder 2 Custom Start G-code",
                "extr_2_end_g_code": "Extruder 2 Custom End G-code"
            }
        ]
            # Добавьте сколько угодно принтеров по умолчанию
        try:
            for printer_data in default_printers:
                new_printer = Printer(**printer_data)
                session.add(new_printer)
            await session.commit()
        except Exception as e:
            await session.rollback()
            raise HTTPException(status_code=500, detail=str(e))

