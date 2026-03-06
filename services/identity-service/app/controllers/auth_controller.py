from flask import request

from app.services.auth_service import (
    register_user_service,
    login_user_service,
)
from shared.utils.response import success_response, error_response


def register_user():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    username = payload.get("username")
    password = payload.get("password")

    if not email or not username or not password:
        return error_response("email, username and password are required", 400)

    ok, result_or_msg = register_user_service(email=email, username=username, password=password)
    if not ok:
        return error_response(result_or_msg, 400)

    return success_response("User registered successfully", result_or_msg, 201)


def login_user():
    payload = request.get_json(silent=True) or {}
    email_or_username = payload.get("email") or payload.get("username")
    password = payload.get("password")

    if not email_or_username or not password:
        return error_response("email/username and password are required", 400)

    ok, result_or_msg = login_user_service(identifier=email_or_username, password=password)
    if not ok:
        return error_response(result_or_msg, 401)

    return success_response("Login successful", result_or_msg, 200)

