from fastapi import FastAPI

from .database import Base, engine
from .routers import auth_router, property_router

Base.metadata.create_all(bind=engine)

app = FastAPI(
    title="Property Dealer API",
    description="FastAPI backend for the Property Dealer project (mobile OTP + JWT login).",
    version="1.0.0",
)

app.include_router(auth_router.router)
app.include_router(property_router.router)


@app.get("/")
def root():
    return {"message": "Property Dealer API is running"}
