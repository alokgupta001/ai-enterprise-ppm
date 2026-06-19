import os
from dotenv import load_dotenv

load_dotenv()

# JWT Config
SECRET_KEY = os.getenv("SECRET_KEY", "prod-ppm-super-secret-key-change-in-production-192830")
ALGORITHM = os.getenv("ALGORITHM", "HS256")
ACCESS_TOKEN_EXPIRE_MINUTES = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "60"))

# Database
DATABASE_URL = os.getenv("DATABASE_URL", "postgresql://postgres:9001@localhost:5432/ppm_platform")

# AI API Keys
OPENAI_API_KEY = os.getenv("OPENAI_API_KEY")
GEMINI_API_KEY = os.getenv("GEMINI_API_KEY")

# Environment & CORS configuration
ENV = os.getenv("ENV", "development")
cors_origins_raw = os.getenv("CORS_ORIGINS", "http://localhost:3000")
CORS_ORIGINS = [origin.strip() for origin in cors_origins_raw.split(",") if origin.strip()]

