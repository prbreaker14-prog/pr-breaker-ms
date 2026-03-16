from flask import Blueprint

from app.controllers.auth_controller import (
    register_user,
    login_user,
    refresh_token,
    forgot_password,
    verify_otp,
    reset_password,
)


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    return register_user()


@auth_bp.post("/login")
def login():
    return login_user()


@auth_bp.post("/refresh")
def refresh():
    return refresh_token()


@auth_bp.post("/forgot-password")
def forgot():
    return forgot_password()


@auth_bp.post("/verify-otp")
def verify():
    return verify_otp()


@auth_bp.post("/reset-password")
def reset():
    return reset_password()

