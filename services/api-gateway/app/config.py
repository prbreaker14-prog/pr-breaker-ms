import os


class Config:
    DEBUG = os.getenv("DEBUG", "false").lower() == "true"
    PORT = int(os.getenv("PORT", "5000"))

    IDENTITY_SERVICE_URL = os.getenv("IDENTITY_SERVICE_URL", "http://identity-service:5000")
    WORKOUT_SERVICE_URL = os.getenv("WORKOUT_SERVICE_URL", "http://workout-service:5000")
    WGROUPS_SERVICE_URL = os.getenv("WGROUPS_SERVICE_URL", "http://workoutgroups-service:5000")
    PERFORMANCE_SERVICE_URL = os.getenv("PERFORMANCE_SERVICE_URL", "http://performance-service:5000")

    # Comma-separated allowlist of origins. If empty, no CORS headers are added.
    CORS_ALLOW_ORIGINS = os.getenv("CORS_ALLOW_ORIGINS", "")


def get_config():
    return Config

