from pydantic import BaseModel
from typing import Optional

class PatientCreate(BaseModel):
    full_name: str
    birth_date: str
    ward_number: str
    diagnosis: str

class LogCreate(BaseModel):
    patient_id: int
    content: str
    doctor_name: str