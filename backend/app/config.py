import os

class Settings:
    PROJECT_NAME: str = "Agentic Analytics Tool"
    VERSION: str = "0.1.0"
    DB_URL: str = os.getenv("DB_URL", "sqlite:///./test.db")
    SECRET_KEY: str = os.getenv("SECRET_KEY", "supersecret")
    ACCESS_TOKEN_EXPIRE_MINUTES: int = 60

settings = Settings()