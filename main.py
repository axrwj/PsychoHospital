from fastapi import FastAPI, Request, Depends, Form, HTTPException
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session
from database import engine, get_db, Base
from models import Patient, PatientLog
from datetime import datetime

Base.metadata.create_all(bind=engine)

app = FastAPI(title="Психо-Учет")
templates = Jinja2Templates(directory="templates")



@app.get("/")
def home(request: Request, db: Session = Depends(get_db), search: str = ""):
    if search:
        patients = db.query(Patient).filter(Patient.full_name.contains(search)).all()
    else:
        patients = db.query(Patient).all()

    total = db.query(Patient).count()
    active = db.query(Patient).filter(Patient.status == "Активен").count()

    return templates.TemplateResponse("index.html", {
        "request": request,
        "patients": patients,
        "search": search,
        "total": total,
        "active": active
    })


@app.post("/add_patient")
def add_patient(
        full_name: str = Form(...),
        birth_date: str = Form(""),
        ward_number: str = Form(...),
        diagnosis: str = Form(...),
        status: str = Form("Активен"),
        db: Session = Depends(get_db)
):
    new_patient = Patient(
        full_name=full_name,
        birth_date=birth_date if birth_date else None,
        ward_number=ward_number,
        diagnosis=diagnosis,
        status=status
    )
    db.add(new_patient)
    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.get("/edit/{patient_id}")
def edit_form(request: Request, patient_id: int, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")
    return templates.TemplateResponse("edit.html", {
        "request": request,
        "patient": patient
    })


@app.post("/edit/{patient_id}")
def update_patient(
        patient_id: int,
        full_name: str = Form(...),
        birth_date: str = Form(""),
        ward_number: str = Form(...),
        diagnosis: str = Form(...),
        status: str = Form("Активен"),
        db: Session = Depends(get_db)
):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    patient.full_name = full_name
    patient.birth_date = birth_date if birth_date else None
    patient.ward_number = ward_number
    patient.diagnosis = diagnosis
    patient.status = status

    db.commit()
    return RedirectResponse(url="/", status_code=303)


@app.post("/delete/{patient_id}")
def delete_patient(patient_id: int, request: Request, db: Session = Depends(get_db)):
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    logs = db.query(PatientLog).filter(PatientLog.patient_id == patient_id).all()
    for log in logs:
        db.delete(log)

    db.delete(patient)
    db.commit()
    return RedirectResponse(url="/", status_code=303)



@app.get("/logs")
def view_logs(request: Request, db: Session = Depends(get_db)):
    """Просмотр всех записей журнала"""
    logs = db.query(PatientLog).order_by(PatientLog.created_at.desc()).limit(100).all()
    patients = db.query(Patient).all()

    total = db.query(Patient).count()
    active = db.query(Patient).filter(Patient.status == "Активен").count()

    return templates.TemplateResponse("logs.html", {
        "request": request,
        "logs": logs,
        "patients": patients,
        "total": total,
        "active": active
    })


@app.get("/patient/{patient_id}/logs")
def patient_logs(request: Request, patient_id: int, db: Session = Depends(get_db)):
    """Просмотр записей журнала конкретного пациента"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    logs = db.query(PatientLog).filter(PatientLog.patient_id == patient_id).order_by(PatientLog.created_at.desc()).all()

    total = db.query(Patient).count()
    active = db.query(Patient).filter(Patient.status == "Активен").count()

    return templates.TemplateResponse("patient_logs.html", {
        "request": request,
        "patient": patient,
        "logs": logs,
        "total": total,
        "active": active
    })


@app.post("/add_log")
def add_log(
        patient_id: int = Form(...),
        content: str = Form(...),
        doctor_name: str = Form(...),
        db: Session = Depends(get_db)
):
    """Добавление записи в журнал"""
    patient = db.query(Patient).filter(Patient.id == patient_id).first()
    if not patient:
        raise HTTPException(status_code=404, detail="Пациент не найден")

    new_log = PatientLog(
        patient_id=patient_id,
        content=content,
        doctor_name=doctor_name
    )
    db.add(new_log)
    db.commit()

    return RedirectResponse(url=f"/patient/{patient_id}/logs", status_code=303)


@app.post("/delete_log/{log_id}")
def delete_log(log_id: int, request: Request, db: Session = Depends(get_db)):
    """Удаление записи из журнала"""
    log = db.query(PatientLog).filter(PatientLog.id == log_id).first()
    if not log:
        raise HTTPException(status_code=404, detail="Запись не найдена")

    patient_id = log.patient_id
    db.delete(log)
    db.commit()

    return RedirectResponse(url=f"/patient/{patient_id}/logs", status_code=303)


if __name__ == "__main__":
    import uvicorn

    uvicorn.run(app, host="0.0.0.0", port=8000)