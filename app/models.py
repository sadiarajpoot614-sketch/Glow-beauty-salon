from sqlalchemy import Column, Integer, String, Text, DateTime
from .database import Base
from datetime import datetime


# =========================
# USER MODEL
# =========================

class User(Base):

    __tablename__ = "users"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        unique=True,
        nullable=False,
        index=True
    )

    password = Column(
        String(255),
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )


# =========================
# APPOINTMENT MODEL
# =========================

class Appointment(Base):

    __tablename__ = "appointments"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    name = Column(
        String(100),
        nullable=False
    )

    email = Column(
        String(150),
        nullable=False
    )

    phone = Column(
        String(30),
        nullable=False
    )

    service = Column(
        String(100),
        nullable=False
    )

    appointment_date = Column(
        String(30),
        nullable=False
    )

    appointment_time = Column(
        String(30),
        nullable=False
    )

    message = Column(
        Text,
        nullable=True
    )

    status = Column(
        String(30),
        default="New",
        nullable=False
    )


# =========================
# OTP VERIFICATION MODEL
# =========================

class OTPVerification(Base):

    __tablename__ = "otp_verifications"

    id = Column(
        Integer,
        primary_key=True,
        index=True
    )

    email = Column(
        String(150),
        nullable=False,
        index=True
    )

    otp = Column(
        String(6),
        nullable=False
    )

    expires_at = Column(
        DateTime,
        nullable=False
    )

    verified = Column(
        Integer,
        default=0,
        nullable=False
    )

    created_at = Column(
        DateTime,
        default=datetime.utcnow
    )