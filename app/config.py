from pydantic_settings import BaseSettings


class Settings(BaseSettings):
    # Change SECRET_KEY in production (e.g. load from env var)
    SECRET_KEY: str = "CHANGE_THIS_TO_A_LONG_RANDOM_SECRET"
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60 * 24  # 1 day
    DATABASE_URL: str = "sqlite:///./property_dealer.db"

    # OTP config
    OTP_EXPIRE_MINUTES: int = 5
    OTP_LENGTH: int = 4


settings = Settings()
