
from pydantic import BaseSettings

class Settings(BaseSettings):
    DATABASE_URL: str
    EMAIL_HOST: str
    EMAIL_PORT: int
    EMAIL_USERNAME: str
    EMAIL_PASSWORD: str
    EMAIL_FROM: str
    EMAIL_FROM_NAME: str
    SECRET_KEY: str
    FRONTEND_URL: str
    ENVIRONMENT: str

    class Config:
        env_file = ".env"

settings = Settings()


