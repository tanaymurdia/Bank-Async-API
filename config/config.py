import os

class Config:
    DATABASE_URL = os.getenv("DATABASE_URL")
    SECRET_KEY = os.getenv("SECRET_KEY")
    ACCESS_TOKEN_EXPIRE_MINUTES = 30
    LOGGING_LEVEL = os.getenv("LOGGING_LEVEL", "INFO")