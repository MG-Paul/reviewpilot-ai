from pydantic_settings import BaseSettings
from pydantic import Field
from typing import Optional

class Settings(BaseSettings):
    PROJECT_NAME: str = "ReviewPilot AI"
    API_V1_STR: str = "/api/v1"
    
    # Database Settings
    DATABASE_URL: str = Field(
        default="postgresql+asyncpg://reviewpilot:reviewpilot_password@postgres:5432/reviewpilot_dev",
        validation_alias="DATABASE_URL"
    )
    
    # Redis URL
    REDIS_URL: str = Field(
        default="redis://redis:6379/0",
        validation_alias="REDIS_URL"
    )
    
    # AWS S3 / R2 Configuration
    S3_BUCKET_NAME: str = "reviewpilot-pdfs"
    AWS_ACCESS_KEY_ID: Optional[str] = None
    AWS_SECRET_ACCESS_KEY: Optional[str] = None
    AWS_REGION: str = "us-east-1"
    
    # Clerk Settings (Auth)
    CLERK_API_KEY: Optional[str] = None
    CLERK_JWT_PEM: Optional[str] = None # Public key to verify tokens locally
    
    # OpenAI Settings
    OPENAI_API_KEY: Optional[str] = None
    
    # R Sandbox Url
    R_SANDBOX_URL: str = "http://r-sandbox:8000"

    class Config:
        case_sensitive = True
        env_file = ".env"

settings = Settings()
