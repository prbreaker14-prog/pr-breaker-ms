import os
import sys

from flask import Flask
from sqlalchemy import inspect, text

from . import db, migrate


def _ensure_paths():
    """
    Ensure repository root and service root are on sys.path so we can import
    shared utilities and the service config module without hardcoding hosts.
    """
    current_dir = os.path.dirname(os.path.abspath(__file__))
    service_root = os.path.abspath(os.path.join(current_dir, ".."))
    repo_root = os.path.abspath(os.path.join(service_root, "..", ".."))

    for path in (service_root, repo_root):
        if path not in sys.path:
            sys.path.append(path)


def create_app(config_name: str | None = None) -> Flask:
    _ensure_paths()

    import config  # type: ignore[import]

    app = Flask(__name__)
    app_config = config.get_config(config_name)
    app.config.from_object(app_config)

    db.init_app(app)
    migrate.init_app(app, db)

    # Import models so migrations can detect them
    from app import models as _models  # noqa: F401

    # For initial setup, auto-create tables if they don't exist yet.
    # In a more advanced setup you would run migrations instead.
    with app.app_context():
        db.create_all()
        _ensure_workout_name_column()

    # Register blueprints
    from app.routes.session_routes import session_bp
    from app.routes.log_routes import log_bp 
    
    app.register_blueprint(session_bp, url_prefix="/performance/sessions")
    app.register_blueprint(log_bp, url_prefix="/performance/logs")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "performance-service"}

    return app


def _ensure_workout_name_column() -> None:
    """
    Backfill schema for existing databases that predate workout_name.
    """
    inspector = inspect(db.engine)
    if not inspector.has_table("workout_logs"):
        return

    columns = {column["name"] for column in inspector.get_columns("workout_logs")}
    if "workout_name" in columns:
        return

    dialect = db.engine.dialect.name
    if dialect == "postgresql":
        db.session.execute(
            text("ALTER TABLE workout_logs ADD COLUMN workout_name VARCHAR(255) NOT NULL DEFAULT ''")
        )
    elif dialect == "sqlite":
        db.session.execute(
            text("ALTER TABLE workout_logs ADD COLUMN workout_name VARCHAR(255) NOT NULL DEFAULT ''")
        )
    else:
        db.session.execute(
            text("ALTER TABLE workout_logs ADD COLUMN workout_name VARCHAR(255)")
        )
    db.session.commit()


def main():
    app = create_app()
    port = app.config.get("PORT", 5004)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

