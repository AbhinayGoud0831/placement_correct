import os
from dotenv import load_dotenv

load_dotenv()


class Settings:
    DATABASE_URL: str = os.getenv(
        "DATABASE_URL",
        "postgresql+psycopg2://placement_user:placement_pass@localhost:5432/placement_db",
    )
    
    _secret_key = os.getenv("SECRET_KEY")
    if not _secret_key:
        raise ValueError(
            "SECRET_KEY environment variable is required. "
            "Generate one with: python3 -c \"import secrets; print(secrets.token_urlsafe(32))\""
        )
    SECRET_KEY: str = _secret_key
    
    ALGORITHM: str = "HS256"
    ACCESS_TOKEN_EXPIRE_MINUTES: int = int(os.getenv("ACCESS_TOKEN_EXPIRE_MINUTES", "1440"))

    OLLAMA_HOST: str = os.getenv("OLLAMA_HOST", "http://localhost:11434")
    OLLAMA_MODEL: str = os.getenv("OLLAMA_MODEL", "qwen2.5")

    EMBEDDING_MODEL: str = os.getenv("EMBEDDING_MODEL", "all-MiniLM-L6-v2")

    UPLOAD_DIR: str = os.getenv("UPLOAD_DIR", "./uploads")

    # Weighted scoring
    WEIGHT_SKILLS: float = 0.5
    WEIGHT_EXPERIENCE: float = 0.3
    WEIGHT_EDUCATION: float = 0.2

    # Public job-source APIs (no API key required).
    REMOTIVE_API_URL: str = os.getenv("REMOTIVE_API_URL", "https://remotive.com/api/remote-jobs")
    ARBEITNOW_API_URL: str = os.getenv("ARBEITNOW_API_URL", "https://www.arbeitnow.com/api/job-board-api")
    JOB_SOURCE_TIMEOUT: int = int(os.getenv("JOB_SOURCE_TIMEOUT", "15"))
    LIVE_JOB_LIMIT: int = int(os.getenv("LIVE_JOB_LIMIT", "50"))


settings = Settings()
os.makedirs(settings.UPLOAD_DIR, exist_ok=True)
