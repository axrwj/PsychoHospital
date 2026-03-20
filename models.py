from sqlalchemy import Column, Integer, String, Date, DateTime, Text, ForeignKey
from sqlalchemy.orm import relationship
from database import Base
from datetime import datetime


class Patient(Base):
    __tablename__ = "patients"
    id = Column(Integer, primary_key=True, index=True)
    full_name = Column(String, index=True)
    birth_date = Column(String)
    ward_number = Column(String)
    diagnosis = Column(String)
    status = Column(String, default="Активен")
    created_at = Column(DateTime, default=datetime.now)

    logs = relationship("PatientLog", back_populates="patient")


class PatientLog(Base):
    __tablename__ = "logs"
    id = Column(Integer, primary_key=True, index=True)
    patient_id = Column(Integer, ForeignKey("patients.id"))
    content = Column(Text)
    doctor_name = Column(String)
    created_at = Column(DateTime, default=datetime.now)

    patient = relationship("Patient", back_populates="logs")