from fastapi import APIRouter, Depends, HTTPException, status
from sqlalchemy.orm import Session

from .. import models, schemas, auth
from ..database import get_db

router = APIRouter(prefix="/auth", tags=["Auth"])


@router.post("/request-otp", status_code=status.HTTP_200_OK)
def request_otp(payload: schemas.OTPRequest, db: Session = Depends(get_db)):
    """Step 1 of login: send an OTP to the given mobile number."""
    otp = auth.create_otp(db, payload.phone_number)

    # TODO: wire this up to a real SMS gateway (e.g. Twilio, MSG91).
    # Returned here only so the flow is testable without SMS configured.
    return {
        "message": f"OTP sent to {payload.phone_number}",
        "debug_otp": otp.code,
    }


@router.post("/verify-otp", response_model=schemas.Token)
def verify_otp(payload: schemas.OTPVerify, db: Session = Depends(get_db)):
    """Step 2 of login: verify OTP and issue a JWT access token."""
    if not auth.verify_otp(db, payload.phone_number, payload.code):
        raise HTTPException(
            status_code=status.HTTP_400_BAD_REQUEST,
            detail="Invalid or expired OTP",
        )

    user = (
        db.query(models.User)
        .filter(models.User.phone_number == payload.phone_number)
        .first()
    )
    if not user:
        user = models.User(phone_number=payload.phone_number, name=payload.name)
        db.add(user)
        db.commit()
        db.refresh(user)

    access_token = auth.create_access_token(data={"sub": user.phone_number})
    return schemas.Token(access_token=access_token)


@router.get("/me", response_model=schemas.UserOut)
def read_current_user(current_user: models.User = Depends(auth.get_current_user)):
    return current_user
