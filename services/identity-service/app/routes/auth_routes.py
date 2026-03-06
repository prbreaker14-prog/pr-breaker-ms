from flask import Blueprint

from app.controllers.auth_controller import register_user, login_user


auth_bp = Blueprint("auth", __name__)


@auth_bp.post("/register")
def register():
    return register_user()


@auth_bp.post("/login")
def login():
    return login_user()

