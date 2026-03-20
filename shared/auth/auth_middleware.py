from functools import wraps
from typing import Callable, TypeVar, Any

from flask import request, g

from shared.auth.jwt_utils import decode_token


F = TypeVar("F", bound=Callable[..., Any])


def jwt_required(fn: F) -> F:
    @wraps(fn)
    def wrapper(*args, **kwargs):
        auth_header = request.headers.get("Authorization", "")
        parts = auth_header.split()
        if len(parts) != 2 or parts[0].lower() != "bearer":
            from shared.utils.response import error_response

            return error_response("Authorization header missing or invalid", 401)

        token = parts[1]
        ok, payload, error = decode_token(token)
        if not ok or payload is None:
            from shared.utils.response import error_response

            return error_response(error or "Invalid token", 401)

        # Only allow access tokens for protected endpoints
        if payload.get("type") not in (None, "access"):
            from shared.utils.response import error_response

            return error_response("Invalid token type", 401)

        # Attach user payload to flask global context (support both snake_case and camelCase)
        g.current_user = {
            "user_id": payload.get("user_id"),
            "userId": payload.get("user_id"),
            "email": payload.get("email"),
            "userEmail": payload.get("email"),
        }

        # Also attach user_id to request.user for convenience
        request.user = payload.get("user_id")

        return fn(*args, **kwargs)

    return wrapper  # type: ignore[return-value]

