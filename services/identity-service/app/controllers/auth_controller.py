from flask import request

from app.services.auth_service import (
    register_user_service,
    login_user_service,
    refresh_token_service,
    forgot_password_service,
    verify_reset_otp_service,
    reset_password_service,
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


def refresh_token():
    payload = request.get_json(silent=True) or {}
    token = payload.get("refresh_token")
    if not token:
        return error_response("refresh_token is required", 400)

    ok, result_or_msg = refresh_token_service(token)
    if not ok:
        return error_response(result_or_msg, 401)

    return success_response("Token refreshed", result_or_msg, 200)


def forgot_password():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    if not email:
        return error_response("email is required", 400)

    ok, data = forgot_password_service(email)
    if not ok:
        return error_response("Failed to start password reset", 400)

    return success_response("If the email exists, an OTP was sent", data, 200)


def verify_otp():
    payload = request.get_json(silent=True) or {}
    email = payload.get("email")
    otp = payload.get("otp")
    if not email or not otp:
        return error_response("email and otp are required", 400)

    ok, result_or_msg = verify_reset_otp_service(email, otp)
    if not ok:
        return error_response(result_or_msg, 400)

    return success_response("OTP verified", result_or_msg, 200)


def reset_password():
    payload = request.get_json(silent=True) or {}
    token = payload.get("reset_token")
    new_password = payload.get("new_password")
    if not token or not new_password:
        return error_response("reset_token and new_password are required", 400)

    ok, result_or_msg = reset_password_service(token, new_password)
    if not ok:
        return error_response(result_or_msg, 400)

    return success_response("Password reset successful", result_or_msg, 200)

