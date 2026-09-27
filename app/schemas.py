from datetime import datetime
from typing import Optional, List

from pydantic import BaseModel, Field

from .models import CategoryEnum, YesNoEnum, FloorEnum


# ---------- Auth ----------

class OTPRequest(BaseModel):
    phone_number: str = Field(..., examples=["9876543210"])


class OTPVerify(BaseModel):
    phone_number: str
    code: str
    name: Optional[str] = None  # used to create the user on first login


class Token(BaseModel):
    access_token: str
    token_type: str = "bearer"


class TokenData(BaseModel):
    phone_number: Optional[str] = None


# ---------- User ----------

class UserOut(BaseModel):
    id: int
    name: Optional[str]
    phone_number: str
    is_active: bool

    class Config:
        from_attributes = True


# ---------- Property ----------

class PropertyBase(BaseModel):
    property_name: str
    property_slug: str
    property_address: str
    property_floor: Optional[FloorEnum] = None
    property_price: int
    property_washroom: Optional[YesNoEnum] = YesNoEnum.N
    property_type: Optional[str] = None
    category: CategoryEnum
    personal_name: str
    personal_phone: str
    status: Optional[str] = "active"


class PropertyCreate(PropertyBase):
    property_image: Optional[List[str]] = None  # multiple image URLs


class PropertyUpdate(BaseModel):
    property_name: Optional[str] = None
    property_slug: Optional[str] = None
    property_address: Optional[str] = None
    property_floor: Optional[FloorEnum] = None
    property_price: Optional[int] = None
    property_washroom: Optional[YesNoEnum] = None
    property_type: Optional[str] = None
    category: Optional[CategoryEnum] = None
    personal_name: Optional[str] = None
    personal_phone: Optional[str] = None
    status: Optional[str] = None
    property_image: Optional[List[str]] = None


class PropertyOut(PropertyBase):
    id: int
    property_image: Optional[List[str]] = None
    owner_id: int
    created_at: datetime
    updated_at: datetime

    class Config:
        from_attributes = True

    @staticmethod
    def from_orm_obj(obj):
        data = PropertyOut.model_validate(obj, from_attributes=True)
        data.property_image = obj.property_image.split(",") if obj.property_image else []
        return data
