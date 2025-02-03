from pydantic_settings import BaseSettings
from functools import lru_cache
from dotenv import load_dotenv

load_dotenv()

class Settings(BaseSettings):
    APP_NAME: str
    ENVIRONMENT: str
    DEBUG: bool
    SECRET_KEY: str
    
    #DATABASE_URL: str
    TEST_DATABASE_URL: str
    
    JWT_SECRET_KEY: str
    ACCESS_TOKEN_EXPIRE_MINUTES: int
    
    STRIPE_SECRET_KEY: str
    STRIPE_WEBHOOK_SECRET: str

    class Config:
        env_file = ".env"  
        extra = "allow"  

@lru_cache()
def get_settings():
    return Settings()

settings = get_settings()
