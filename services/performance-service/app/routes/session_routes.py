from flask import Blueprint

from app.utils.auth import token_required
from app.controllers import session_controller

# The app registers this blueprint with url_prefix="/sessions",
# so we keep the blueprint itself un-prefixed to avoid double-prefix paths.
session_bp = Blueprint("sessions", __name__)


@session_bp.route("", methods=["POST"])
@token_required
def create_session(current_user: dict):
    return session_controller.create_session(current_user)


@session_bp.route("", methods=["GET"])
@token_required
def list_sessions(current_user: dict):
    return session_controller.list_sessions(current_user)


@session_bp.route("/<string:session_id>", methods=["GET"])
@token_required
def get_session(current_user: dict, session_id: str):
    return session_controller.get_session(current_user, session_id)


@session_bp.route("/<string:session_id>", methods=["DELETE"])
@token_required
def delete_session(current_user: dict, session_id: str):
    return session_controller.delete_session(current_user, session_id)