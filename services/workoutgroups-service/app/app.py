import os
import sys

from flask import Flask

from app import db, migrate


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

    # Auto-create tables on first run (simple bootstrap)
    with app.app_context():
        db.create_all()

    # Register blueprints
    from app.routes.wgroups_routes import wgroups_bp

    app.register_blueprint(wgroups_bp, url_prefix="/wgroups")

    @app.route("/health", methods=["GET"])
    def health():
        return {"status": "ok", "service": "workoutgroups-service"}

    return app


def main():
    app = create_app()
    port = app.config.get("PORT", 5003)
    app.run(host="0.0.0.0", port=port)


if __name__ == "__main__":
    main()

