from flask import g, request

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


def update_current_user():
    from shared.auth.auth_middleware import jwt_required

    @jwt_required
    def _inner():
        user_payload = getattr(g, "current_user", {}) or {}
        user_id = user_payload.get("user_id")
        if not user_id:
            return error_response("Unauthorized", 401)

        payload = request.get_json(silent=True) or {}
        if not isinstance(payload, dict) or not payload:
            return error_response("Request body must be a non-empty JSON object", 400)

        # Password updates are intentionally handled in a separate flow.
        blocked_keys = {"password", "userPassword", "password_hash", "pass"}
        if any(key in payload for key in blocked_keys):
            return error_response("Password update is not allowed on this endpoint", 400)

        from app import db
        from app.models import User, UserProfile

        user = User.query.get(user_id)
        if not user:
            return error_response("User not found", 404)

        profile = UserProfile.query.get(user_id)
        if profile is None:
            profile = UserProfile(user_id=user_id)
            db.session.add(profile)

        # Map accepted payload keys to model fields.
        user_key_map = {
            "name": "username",
            "userName": "username",
            "username": "username",
            "mailId": "email",
            "mailid": "email",
            "userEmail": "email",
            "email": "email",
        }
        profile_key_map = {
            "gender": "gender",
            "height": "height",
            "weight": "weight",
        }

        updated_fields = []

        for payload_key, model_field in user_key_map.items():
            if payload_key in payload:
                value = payload[payload_key]
                if value is None:
                    continue
                setattr(user, model_field, str(value).strip())
                updated_fields.append(payload_key)

        # Keep optional numeric parsing forgiving.
        for payload_key, model_field in profile_key_map.items():
            if payload_key not in payload:
                continue

            value = payload[payload_key]
            if model_field in {"height", "weight"} and value is not None:
                try:
                    value = float(value)
                except (TypeError, ValueError):
                    return error_response(f"{payload_key} must be a number", 400)

            setattr(profile, model_field, value)
            updated_fields.append(payload_key)

        if not updated_fields:
            return error_response(
                "No supported fields provided. Allowed: name, mailId/email, gender, height, weight",
                400,
            )

        # Ensure uniqueness for updated email/username.
        if "username" in [user_key_map[k] for k in user_key_map if k in payload]:
            existing_user = User.query.filter(
                User.username == user.username,
                User.id != user.id,
            ).first()
            if existing_user:
                return error_response("Username already in use", 409)

        if "email" in [user_key_map[k] for k in user_key_map if k in payload]:
            existing_email = User.query.filter(
                User.email == user.email,
                User.id != user.id,
            ).first()
            if existing_email:
                return error_response("Email already in use", 409)

        db.session.commit()

        return success_response(
            "Profile updated successfully",
            {
                "userId": user.id,
                "userEmail": user.email,
                "userName": user.username,
                "gender": profile.gender,
                "height": profile.height,
                "weight": profile.weight,
            },
            200,
        )

    return _inner()

