import os


BASE_DIR = os.path.abspath(os.path.dirname(__file__))


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    SECRET_KEY = os.getenv("SECRET_KEY", "change-me-in-production")

    # Prefer a service-specific URL, but also support the generic DATABASE_URL
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "PERFORMANCE_DATABASE_URL",
        os.getenv(
            "DATABASE_URL",
            "postgresql+psycopg2://performance_user:performance_password@performance-db:5432/performance_db",
        ),
    )
    SQLALCHEMY_TRACK_MODIFICATIONS = False

    JWT_SECRET = os.getenv("JWT_SECRET", "super-secret-change-me")

    IDENTITY_SERVICE_URL = os.getenv("IDENTITY_SERVICE_URL", "http://identity-service:5000")
    WORKOUT_SERVICE_URL = os.getenv("WORKOUT_SERVICE_URL", "http://workout-service:5000")
    PERFORMANCE_SERVICE_URL = os.getenv("PERFORMANCE_SERVICE_URL", "http://performance-service:5000")

    PORT = int(os.getenv("PORT", "5004"))


class TestConfig(Config):
    TESTING = True
    SQLALCHEMY_DATABASE_URI = os.getenv(
        "PERFORMANCE_TEST_DATABASE_URL",
        "sqlite:///:memory:",
    )


config_by_name = {
    "default": Config,
    "testing": TestConfig,
}


def get_config(name: str | None = None):
    return config_by_name.get(name or "default", Config)