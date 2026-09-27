import random
from datetime import datetime, timedelta, timezone

from fastapi import Depends, HTTPException, status
from fastapi.security import OAuth2PasswordBearer
from jose import JWTError, jwt
from sqlalchemy.orm import Session

from . import models, schemas
from .config import settings
from .database import get_db

oauth2_scheme = OAuth2PasswordBearer(tokenUrl="/auth/verify-otp")


# ---------- OTP helpers ----------

def generate_otp() -> str:
    return "".join(random.choices("0123456789", k=settings.OTP_LENGTH))


def create_otp(db: Session, phone_number: str) -> models.OTP:
    code = generate_otp()
    expires_at = datetime.utcnow() + timedelta(minutes=settings.OTP_EXPIRE_MINUTES)
    otp = models.OTP(phone_number=phone_number, code=code, expires_at=expires_at)
    db.add(otp)
    db.commit()
    db.refresh(otp)
    return otp


def verify_otp(db: Session, phone_number: str, code: str) -> bool:
    otp = (
        db.query(models.OTP)
        .filter(
            models.OTP.phone_number == phone_number,
            models.OTP.code == code,
            models.OTP.is_used == False,  # noqa: E712
        )
        .order_by(models.OTP.created_at.desc())
        .first()
    )
    if not otp:
        return False
    if otp.expires_at < datetime.utcnow():
        return False
    otp.is_used = True
    db.commit()
    return True


# ---------- JWT helpers ----------

def create_access_token(data: dict, expires_delta: timedelta | None = None) -> str:
    to_encode = data.copy()
    expire = datetime.now(timezone.utc) + (
        expires_delta or timedelta(minutes=settings.ACCESS_TOKEN_EXPIRE_MINUTES)
    )
    to_encode.update({"exp": expire})
    return jwt.encode(to_encode, settings.SECRET_KEY, algorithm=settings.ALGORITHM)


def get_current_user(
    token: str = Depends(oauth2_scheme), db: Session = Depends(get_db)
) -> models.User:
    credentials_exception = HTTPException(
        status_code=status.HTTP_401_UNAUTHORIZED,
        detail="Could not validate credentials",
        headers={"WWW-Authenticate": "Bearer"},
    )
    try:
        payload = jwt.decode(token, settings.SECRET_KEY, algorithms=[settings.ALGORITHM])
        phone_number: str = payload.get("sub")
        if phone_number is None:
            raise credentials_exception
        token_data = schemas.TokenData(phone_number=phone_number)
    except JWTError:
        raise credentials_exception

    user = (
        db.query(models.User)
        .filter(models.User.phone_number == token_data.phone_number)
        .first()
    )
    if user is None:
        raise credentials_exception
    if not user.is_active:
        raise HTTPException(status_code=400, detail="Inactive user")
    return user
