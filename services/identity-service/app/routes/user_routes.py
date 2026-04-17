from flask import Blueprint

from app.controllers.user_controller import get_current_user, update_current_user


users_bp = Blueprint("users", __name__)


@users_bp.get("/me")
def me():
    return get_current_user()


@users_bp.patch("/me")
def update_me():
    return update_current_user()

