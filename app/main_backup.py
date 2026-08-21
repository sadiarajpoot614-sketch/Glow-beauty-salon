from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse
from sqlalchemy.orm import Session

from .database import SessionLocal
from .models import Appointment


app = FastAPI(title="Glow Beauty Salon")

app.mount("/static", StaticFiles(directory="app/static"), name="static")

templates = Jinja2Templates(directory="app/templates")


@app.get("/")
def home(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="home.html"
    )


@app.get("/about")
def about(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="about.html"
    )


@app.get("/services")
def services(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="services.html"
    )


@app.get("/contact")
def contact(request: Request):
    return templates.TemplateResponse(
        request=request,
        name="contact.html"
    )


@app.post("/contact")
def book_appointment(
    name: str = Form(...),
    email: str = Form(...),
    phone: str = Form(...),
    service: str = Form(...),
    appointment_date: str = Form(...),
    appointment_time: str = Form(...),
    message: str = Form("")
):
    db: Session = SessionLocal()

    appointment = Appointment(
        name=name,
        email=email,
        phone=phone,
        service=service,
        appointment_date=appointment_date,
        appointment_time=appointment_time,
        message=message,
        status="New"
    )

    db.add(appointment)
    db.commit()
    db.close()

    return RedirectResponse(
        url="/contact?success=1",
        status_code=303
    )


@app.get("/crm")
def crm(request: Request):
    db: Session = SessionLocal()

    appointments = (
        db.query(Appointment)
        .order_by(Appointment.id.desc())
        .all()
    )

    db.close()

    return templates.TemplateResponse(
        request=request,
        name="crm.html",
        context={
            "request": request,
            "appointments": appointments
        }
    )


@app.post("/crm/delete/{appointment_id}")
def delete_appointment(appointment_id: int):
    db: Session = SessionLocal()

    appointment = (
        db.query(Appointment)
        .filter(Appointment.id == appointment_id)
        .first()
    )

    if appointment:
        db.delete(appointment)
        db.commit()

    db.close()

    return RedirectResponse(
        url="/crm",
        status_code=303
    )
