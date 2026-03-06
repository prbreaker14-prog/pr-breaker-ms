from flask import g

from shared.utils.response import success_response


def get_current_user():
    from shared.auth.auth_middleware import jwt_required

    @jwt_required
    def _inner():
        user = getattr(g, "current_user", None) or {}
        return success_response("Current user fetched", user)

    return _inner()

