import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # Database
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "IDENTITY_DATABASE_URL",
        "postgresql+psycopg2://identity_user:identity_password@localhost:5432/identity_db",
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    # JWT
    JWT_SECRET = os.getenv("JWT_SECRET")

    # Service URLs (environment-agnostic)
    IDENTITY_SERVICE_URL = os.getenv("IDENTITY_SERVICE_URL", "http://identity-service")
    WORKOUT_SERVICE_URL = os.getenv("WORKOUT_SERVICE_URL", "http://workout-service")

    # Port configuration (for local dev; Docker/K8s can override)
    PORT = int(os.getenv("PORT", "5001"))


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

