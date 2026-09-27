import enum
from datetime import datetime

from sqlalchemy import (
    Column, Integer, String, DateTime, Boolean, Enum, ForeignKey, Text
)
from sqlalchemy.orm import relationship

from .database import Base


class CategoryEnum(str, enum.Enum):
    RENT = "Rent"
    SALE = "Sale"


class YesNoEnum(str, enum.Enum):
    Y = "Y"
    N = "N"


class FloorEnum(str, enum.Enum):
    GROUND = "G"
    FIRST = "F"
    SECOND = "S"


class User(Base):
    """Customer / dealer who logs in via mobile number + OTP."""
    __tablename__ = "users"

    id = Column(Integer, primary_key=True, index=True)
    name = Column(String(120), nullable=True)          # Name Customer
    phone_number = Column(String(15), unique=True, index=True, nullable=False)
    is_active = Column(Boolean, default=True)
    created_at = Column(DateTime, default=datetime.utcnow)

    properties = relationship("Property", back_populates="owner")


class OTP(Base):
    """One-time password issued for a phone number login."""
    __tablename__ = "otps"

    id = Column(Integer, primary_key=True, index=True)
    phone_number = Column(String(15), index=True, nullable=False)
    code = Column(String(10), nullable=False)
    expires_at = Column(DateTime, nullable=False)
    is_used = Column(Boolean, default=False)
    created_at = Column(DateTime, default=datetime.utcnow)


class Property(Base):
    """Property Details, matching the notebook field list."""
    __tablename__ = "properties"

    id = Column(Integer, primary_key=True, index=True)

    property_image = Column(Text, nullable=True)     # comma-separated URLs (multiple image option)
    property_name = Column(String(200), nullable=False)
    property_slug = Column(String(220), unique=True, index=True, nullable=False)
    property_address = Column(String(300), nullable=False)
    property_floor = Column(Enum(FloorEnum), nullable=True)
    property_price = Column(Integer, nullable=False)
    property_washroom = Column(Enum(YesNoEnum), default=YesNoEnum.N)
    property_type = Column(String(50), nullable=True)  # e.g. Residential / Commercial

    category = Column(Enum(CategoryEnum), nullable=False)  # Rent / Sale

    personal_name = Column(String(120), nullable=False)   # contact person name
    personal_phone = Column(String(15), nullable=False)   # contact person phone

    status = Column(String(30), default="active")

    owner_id = Column(Integer, ForeignKey("users.id"), nullable=False)
    owner = relationship("User", back_populates="properties")

    created_at = Column(DateTime, default=datetime.utcnow)
    updated_at = Column(DateTime, default=datetime.utcnow, onupdate=datetime.utcnow)
