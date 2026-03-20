from flask import g

from shared.utils.response import success_response, error_response


def get_current_user():
    from shared.auth.auth_middleware import jwt_required

    @jwt_required
    def _inner():
        # The auth middleware only guarantees user_id and email in the token.
        # Load additional profile info from the identity-service database.
        user_payload = getattr(g, "current_user", {}) or {}
        user_id = user_payload.get("user_id")
        if not user_id:
            return error_response("Unauthorized", 401)

        from app.models import User, UserProfile

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)

        profile = UserProfile.query.get(user_id)

        return success_response(
            "Current user fetched",
            {
                "userId": user.id,
                "userEmail": user.email,
                "userName": user.username,
                "age": profile.age if profile else None,
                "gender": profile.gender if profile else None,
                "height": profile.height if profile else None,
                "weight": profile.weight if profile else None,
            },
        )

    return _inner()

