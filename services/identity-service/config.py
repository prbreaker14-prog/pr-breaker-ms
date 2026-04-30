import os
from dotenv import load_dotenv
load_dotenv()

BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    SQLALCHEMY_DATABASE_URI = os.getenv(
        "IDENTITY_DATABASE_URL",
        "postgresql+psycopg2://identity_user:identity_password@identity-db:5432/identity_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-change-me")

    IDENTITY_SERVICE_URL = os.getenv("IDENTITY_SERVICE_URL", "http://identity-service:5000")
    WORKOUT_SERVICE_URL = os.getenv("WORKOUT_SERVICE_URL", "http://workout-service:5000")

    PORT = int(os.getenv("PORT", "5001"))
    SMTP_HOST = os.getenv("SMTP_HOST", "smtp.gmail.com")
    SMTP_PORT = int(os.getenv("SMTP_PORT", "587"))
    SMTP_USER = os.getenv("SMTP_USER")
    SMTP_PASSWORD = os.getenv("SMTP_PASSWORD")
    FROM_EMAIL = os.getenv("FROM_EMAIL") or os.getenv("SMTP_USER")
    SMTP_USE_TLS = os.getenv("SMTP_USE_TLS", "true").lower() in ("true", "1", "yes")

    # Development helper
    DEV_SHOW_OTP = os.getenv("DEV_SHOW_OTP", "false").lower() in ("true", "1", "yes")

class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "IDENTITY_TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )


config_by_name = {
    "default": Config,
    "testing": TestConfig,
}


def get_config(name: str | None = None):
    return config_by_name.get(name or "default", Config)