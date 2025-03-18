from pydantic import BaseModel, Field
from typing import List, Optional

class ProcessTestInput(BaseModel):
    uid: str = Field(..., description="Unique identifier for the image")
    target: str = Field(..., description="Comma-separated list of defect types")
    userUid: str = Field(..., description="Unique identifier for the user")

class ProcessTestOutput(BaseModel):
    status: str = Field(..., description="Status of the operation")
    uid: str = Field(..., description="Unique identifier for the image")
    created: List[int] = Field(..., description="List of defect types created")

class ExportCSVOutput(BaseModel):
    file_url: str = Field(..., description="URL to download the CSV file")

class DefectCountInput(BaseModel):
    userUid: str = Field(..., description="Unique identifier for the user")

class DefectCountOutput(BaseModel):
    count: int = Field(..., description="Total number of defects marked by the user")