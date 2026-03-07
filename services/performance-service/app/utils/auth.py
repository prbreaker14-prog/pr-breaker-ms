from functools import wraps

from flask import current_app, request

from app.utils.response import error_response
from shared.auth.jwt_utils import decode_token


def _get_bearer_token() -> str | None:
    """Extract the raw JWT string from the Authorization header."""
    auth_header = request.headers.get("Authorization", "")
    parts = auth_header.split()
    # Must be exactly: Bearer <token>
    if len(parts) == 2 and parts[0].lower() == "bearer":
        return parts[1]
    return None


def _validate_token_locally(token: str) -> dict | None:
    """
    Validate the JWT locally using the shared jwt_utils helper.

    Returns a normalized user dict on success, or None on any failure.
    """
    ok, payload, error = decode_token(token)
    if not ok or not payload:
        current_app.logger.warning("Token validation failed: %s", error or "Unknown error")
        return None

    # Normalize to the shape expected by controllers: current_user["id"]
    return {
        "id": payload.get("user_id"),
        "email": payload.get("email"),
    }


def token_required(f):
    """
    Decorator for protected routes.

    Validates the Bearer token by calling the identity-service.
    On success, injects `current_user` (dict) as the first argument
    after `self`/nothing — just before any route kwargs.

    Usage:
        @token_required
        def my_route(current_user):
            user_id = current_user["userId"]
    """
    @wraps(f)
    def decorated(*args, **kwargs):
        token = _get_bearer_token()
        if not token:
            return error_response("Authentication token is required.", status_code=401)

        user = _validate_token_locally(token)
        if not user:
            return error_response(
                "Invalid or expired token. Please log in again.", status_code=401
            )

        return f(user, *args, **kwargs)

    return decorated