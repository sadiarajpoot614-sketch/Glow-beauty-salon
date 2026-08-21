import os
import random
from datetime import datetime, timedelta

from fastapi import FastAPI, Request, Form
from fastapi.staticfiles import StaticFiles
from fastapi.templating import Jinja2Templates
from fastapi.responses import RedirectResponse

from starlette.middleware.sessions import SessionMiddleware

from sqlalchemy.orm import Session

from dotenv import load_dotenv

from fastapi_mail import (
    FastMail,
    MessageSchema,
    ConnectionConfig
)

from passlib.context import CryptContext

from .database import SessionLocal
from .models import (
    User,
    Appointment,
    OTPVerification
)


# =====================================================
# LOAD ENVIRONMENT VARIABLES
# =====================================================

load_dotenv()


# =====================================================
# PASSWORD HASHING
# =====================================================

pwd_context = CryptContext(
    schemes=["bcrypt"],
    deprecated="auto"
)


# =====================================================
# EMAIL CONFIGURATION
# =====================================================

conf = ConnectionConfig(
    MAIL_USERNAME=os.getenv("EMAIL_HOST_USER"),
    MAIL_PASSWORD=os.getenv("EMAIL_HOST_PASSWORD"),
    MAIL_FROM=os.getenv("EMAIL_HOST_USER"),
    MAIL_PORT=465,
    MAIL_SERVER="smtp.gmail.com",
    MAIL_STARTTLS=False,
    MAIL_SSL_TLS=True,
    USE_CREDENTIALS=True,
)


# =====================================================
# APPLICATION
# =====================================================

app = FastAPI(
    title="Glow Beauty Salon",
    description="Professional Beauty Salon Appointment System",
    version="1.0.0"
)


# =====================================================
# SESSION
# IMPORTANT:
# Session remains available for 24 hours.
# Actual automatic logout after 10 minutes of
# INACTIVITY is handled in base.html.
# =====================================================

app.add_middleware(
    SessionMiddleware,
    secret_key=os.getenv(
        "SECRET_KEY",
        "glow_beauty_salon_secret_2026"
    ),
    max_age=60 * 60 * 24
)


# =====================================================
# STATIC FILES
# =====================================================

app.mount(
    "/static",
    StaticFiles(
        directory="app/static"
    ),
    name="static"
)


# =====================================================
# TEMPLATES
# =====================================================

templates = Jinja2Templates(
    directory="app/templates"
)


# =====================================================
# GET CURRENT USER
# =====================================================

def get_current_user(request: Request):

    user_id = request.session.get("user_id")

    if not user_id:
        return None

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.id == user_id
            )
            .first()
        )

        return user

    finally:

        db.close()


# =====================================================
# SIGNUP PAGE
# =====================================================

@app.get("/signup")
def signup_page(
    request: Request
):

    return templates.TemplateResponse(
        request=request,
        name="signup.html"
    )


# =====================================================
# CREATE ACCOUNT
# =====================================================

@app.post("/signup")
def signup(

    request: Request,

    name: str = Form(...),

    email: str = Form(...),

    password: str = Form(...),

    confirm_password: str = Form(...)

):

    name = name.strip()
    email = email.strip().lower()

    # Password confirmation
    if password != confirm_password:

        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "error": "Passwords do not match.",
                "name": name,
                "email": email
            }
        )

    # Password length check
    if len(password.encode("utf-8")) > 72:

        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "error": "Password must be 72 characters or less.",
                "name": name,
                "email": email
            }
        )

    # Basic password check
    if len(password) < 6:

        return templates.TemplateResponse(
            request=request,
            name="signup.html",
            context={
                "error": "Password must be at least 6 characters.",
                "name": name,
                "email": email
            }
        )

    db = SessionLocal()

    try:

        # Check existing user
        existing_user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if existing_user:

            return templates.TemplateResponse(
                request=request,
                name="signup.html",
                context={
                    "error": "This email is already registered. Please login.",
                    "name": name,
                    "email": email
                }
            )

        # Hash password
        hashed_password = pwd_context.hash(
            password
        )

        # Create user
        new_user = User(
            name=name,
            email=email,
            password=hashed_password
        )

        db.add(new_user)

        db.commit()

        db.refresh(new_user)

        # Login automatically after signup
        request.session.clear()

        request.session["user_id"] = new_user.id
        request.session["user_name"] = new_user.name

        return RedirectResponse(
            url="/",
            status_code=303
        )

    finally:

        db.close()


# =====================================================
# LOGIN PAGE
# =====================================================

@app.get("/login")
def login_page(
    request: Request
):

    error = request.query_params.get("error")

    error_message = None

    if error == "1":
        error_message = "Invalid email or password."

    return templates.TemplateResponse(

        request=request,

        name="login.html",

        context={
            "error": error_message
        }
    )


# =====================================================
# LOGIN USER
# =====================================================

@app.post("/login")
def login(

    request: Request,

    email: str = Form(...),

    password: str = Form(...)

):

    email = email.strip().lower()

    db = SessionLocal()

    try:

        user = (
            db.query(User)
            .filter(
                User.email == email
            )
            .first()
        )

        if not user:

            return RedirectResponse(
                url="/login?error=1",
                status_code=303
            )

        # Verify password
        try:

            password_correct = pwd_context.verify(
                password,
                user.password
            )

        except Exception as e:

            print(
                "Password verification error:",
                e
            )

            password_correct = False

        if not password_correct:

            return RedirectResponse(
                url="/login?error=1",
                status_code=303
            )

        # Clear old session
        request.session.clear()

        # Create new session
        request.session["user_id"] = user.id
        request.session["user_name"] = user.name

        return RedirectResponse(
            url="/",
            status_code=303
        )

    finally:

        db.close()


# =====================================================
# LOGOUT
# =====================================================

@app.get("/logout")
def logout(
    request: Request
):

    request.session.clear()

    return RedirectResponse(
        url="/login",
        status_code=303
    )


# =====================================================
# HOME
# =====================================================

@app.get("/")
def home(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="home.html",

        context={
            "user": user
        }
    )


# =====================================================
# ABOUT
# =====================================================

@app.get("/about")
def about(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="about.html",

        context={
            "user": user
        }
    )


# =====================================================
# SERVICES
# =====================================================

@app.get("/services")
def services(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="services.html",

        context={
            "user": user
        }
    )


# =====================================================
# CONTACT PAGE
# =====================================================

@app.get("/contact")
def contact(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(
            url="/login",
            status_code=303
        )

    return templates.TemplateResponse(

        request=request,

        name="contact.html",

        context={
            "user": user
        }
    )


# =====================================================
# SEND OTP
# =====================================================

@app.post("/send-otp")
async def send_otp(

    request: Request,

    email: str = Form(...)

):

    # Check login
    user = get_current_user(
        request
    )

    if not user:

        return {
            "success": False,
            "message": "Please login first."
        }

    email = email.strip().lower()

    # Security:
    # OTP email must match logged-in account
    if email != user.email.lower():

        return {
            "success": False,
            "message": "Please use your registered email address."
        }

    # Generate OTP
    otp = str(
        random.randint(
            100000,
            999999
        )
    )

    db = SessionLocal()

    try:

        # Delete previous OTP
        db.query(
            OTPVerification
        ).filter(
            OTPVerification.email == email
        ).delete()

        # OTP expires after 5 minutes
        expires_at = (
            datetime.utcnow()
            + timedelta(minutes=5)
        )

        otp_record = OTPVerification(

            email=email,

            otp=otp,

            expires_at=expires_at,

            verified=0
        )

        db.add(
            otp_record
        )

        db.commit()

    finally:

        db.close()


    # OTP EMAIL
    email_message = MessageSchema(

        subject=
        "Your Glow Beauty Salon Verification Code",

        recipients=[
            email
        ],

        body=f"""
Hello {user.name}!

Your Glow Beauty Salon verification code is:

{otp}

This OTP will expire in 5 minutes.

Please do not share this code with anyone.

Thank you,
Glow Beauty Salon
""",

        subtype="plain"
    )


    try:

        fm = FastMail(
            conf
        )

        await fm.send_message(
            email_message
        )

        return {

            "success": True,

            "message":
            "OTP sent successfully to your email."
        }

    except Exception as e:

        print(
            "OTP email error:",
            e
        )

        return {

            "success": False,

            "message":
            "Unable to send OTP. Please check your email settings."
        }


# =====================================================
# VERIFY OTP
# =====================================================

@app.post("/verify-otp")
def verify_otp(

    request: Request,

    email: str = Form(...),

    otp: str = Form(...)

):

    # Check login
    user = get_current_user(
        request
    )

    if not user:

        return {
            "success": False,
            "message": "Please login first."
        }

    email = email.strip().lower()
    otp = otp.strip()

    # OTP must belong to logged-in account
    if email != user.email.lower():

        return {
            "success": False,
            "message": "Invalid email."
        }

    db = SessionLocal()

    try:

        record = (

            db.query(
                OTPVerification
            )

            .filter(

                OTPVerification.email == email,

                OTPVerification.otp == otp,

                OTPVerification.verified == 0

            )

            .order_by(

                OTPVerification.id.desc()

            )

            .first()
        )


        if not record:

            return {

                "success": False,

                "message":
                "Invalid OTP."
            }


        # Check expiry
        if datetime.utcnow() > record.expires_at:

            return {

                "success": False,

                "message":
                "OTP has expired. Please request a new OTP."
            }


        # Mark verified
        record.verified = 1

        db.commit()


        return {

            "success": True,

            "message":
            "Email verified successfully."
        }

    finally:

        db.close()


# =====================================================
# AVAILABLE TIME SLOTS
# =====================================================

@app.get("/available-slots")
def available_slots(

    request: Request,

    date: str

):

    user = get_current_user(
        request
    )

    if not user:

        return {

            "success": False,

            "message":
            "Please login first."
        }

    db = SessionLocal()

    try:

        times = [

            "10:00",
            "11:00",
            "12:00",
            "13:00",
            "14:00",
            "15:00",
            "16:00",
            "17:00",
            "18:00",
            "19:00"

        ]


        booked_times = (

            db.query(
                Appointment.appointment_time
            )

            .filter(
                Appointment.appointment_date
                == date
            )

            .all()
        )


        booked = {

            item[0]

            for item in booked_times
        }


        slots = []


        for time in times:

            slots.append({

                "time": time,

                "available":
                time not in booked

            })


        return {

            "date": date,

            "slots": slots

        }

    finally:

        db.close()


# =====================================================
# BOOK APPOINTMENT
# =====================================================

@app.post("/contact")
async def book_appointment(

    request: Request,

    name: str = Form(...),

    email: str = Form(...),

    phone: str = Form(...),

    service: str = Form(...),

    appointment_date: str = Form(...),

    appointment_time: str = Form(...),

    message: str = Form("")

):

    # Check login
    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(

            url="/login",

            status_code=303
        )


    email = email.strip().lower()


    # Appointment email must match account
    if email != user.email.lower():

        return {

            "success": False,

            "message":
            "Please use your registered email address."
        }


    db = SessionLocal()

    try:

        # Check OTP verification
        verified_record = (

            db.query(
                OTPVerification
            )

            .filter(

                OTPVerification.email == email,

                OTPVerification.verified == 1

            )

            .order_by(

                OTPVerification.id.desc()

            )

            .first()
        )


        if not verified_record:

            return {

                "success": False,

                "message":
                "Please verify your email with OTP before booking."
            }


        # Check duplicate slot
        existing_appointment = (

            db.query(
                Appointment
            )

            .filter(

                Appointment.appointment_date
                == appointment_date,

                Appointment.appointment_time
                == appointment_time

            )

            .first()
        )


        if existing_appointment:

            return {

                "success": False,

                "message":
                "This appointment time is already booked."
            }


        # Create appointment
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


        db.add(
            appointment
        )

        db.commit()

    finally:

        db.close()


    # =================================================
    # EMAIL TO SALON
    # =================================================

    salon_email = MessageSchema(

        subject=
        "New Appointment - Glow Beauty Salon",

        recipients=[
            os.getenv(
                "EMAIL_HOST_USER"
            )
        ],

        body=f"""
New appointment received!

================================
GLOW BEAUTY SALON
================================

Customer Name:
{name}

Customer Email:
{email}

Phone:
{phone}

Service:
{service}

Appointment Date:
{appointment_date}

Appointment Time:
{appointment_time}

Message:
{message}

================================
""",

        subtype="plain"
    )


    # =================================================
    # EMAIL TO CUSTOMER
    # =================================================

    customer_email = MessageSchema(

        subject=
        "Appointment Confirmed - Glow Beauty Salon",

        recipients=[
            email
        ],

        body=f"""
Hello {name}!

Your appointment at Glow Beauty Salon
has been successfully booked.

================================
APPOINTMENT DETAILS
================================

Service:
{service}

Date:
{appointment_date}

Time:
{appointment_time}

Phone:
{phone}

================================

Thank you for choosing
Glow Beauty Salon!

We look forward to seeing you.
""",

        subtype="plain"
    )


    # =================================================
    # SEND SALON EMAIL
    # =================================================

    try:

        fm_salon = FastMail(
            conf
        )

        await fm_salon.send_message(
            salon_email
        )

        print(
            "Salon email sent successfully"
        )

    except Exception as e:

        print(
            "Salon email error:",
            e
        )


    # =================================================
    # SEND CUSTOMER EMAIL
    # =================================================

    try:

        fm_customer = FastMail(
            conf
        )

        await fm_customer.send_message(
            customer_email
        )

        print(
            "Customer confirmation email sent successfully"
        )

    except Exception as e:

        print(
            "Customer email error:",
            e
        )


    return RedirectResponse(

        url="/contact?success=1",

        status_code=303
    )


# =====================================================
# CRM DASHBOARD
# =====================================================

@app.get("/crm")
def crm(
    request: Request
):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(

            url="/login",

            status_code=303
        )


    db = SessionLocal()

    try:

        appointments = (

            db.query(
                Appointment
            )

            .order_by(
                Appointment.id.desc()
            )

            .all()
        )


        return templates.TemplateResponse(

            request=request,

            name="crm.html",

            context={

                "user": user,

                "appointments":
                appointments

            }
        )

    finally:

        db.close()


# =====================================================
# DELETE APPOINTMENT
# =====================================================

@app.post(
    "/crm/delete/{appointment_id}"
)
def delete_appointment(

    request: Request,

    appointment_id: int

):

    user = get_current_user(
        request
    )

    if not user:

        return RedirectResponse(

            url="/login",

            status_code=303
        )


    db = SessionLocal()

    try:

        appointment = (

            db.query(
                Appointment
            )

            .filter(

                Appointment.id
                == appointment_id

            )

            .first()
        )


        if appointment:

            db.delete(
                appointment
            )

            db.commit()

    finally:

        db.close()


    return RedirectResponse(

        url="/crm",

        status_code=303
    )
