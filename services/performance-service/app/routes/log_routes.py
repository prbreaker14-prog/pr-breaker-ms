from flask import Blueprint

from app.utils.auth import token_required
from app.controllers import log_controller

# The app registers this blueprint with url_prefix="/logs",
# so we keep the blueprint itself un-prefixed to avoid double-prefix paths.
log_bp = Blueprint("logs", __name__)


@log_bp.route("", methods=["POST"])
@token_required
def log_sets(current_user: dict):
    return log_controller.log_sets(current_user)


@log_bp.route("/upsert", methods=["POST"])
@token_required
def upsert_logs(current_user: dict):
    return log_controller.upsert_workout_logs(current_user)


@log_bp.route("/session/<string:session_id>", methods=["GET"])
@token_required
def get_logs_for_session(current_user: dict, session_id: str):
    return log_controller.get_logs_for_session(current_user, session_id)


@log_bp.route("/history/<string:workout_id>", methods=["GET"])
@token_required
def get_workout_history(current_user: dict, workout_id: str):
    return log_controller.get_workout_history(current_user, workout_id)


@log_bp.route("/<string:log_id>", methods=["PATCH"])
@token_required
def update_log(current_user: dict, log_id: str):
    return log_controller.update_log(current_user, log_id)


@log_bp.route("/<string:log_id>", methods=["DELETE"])
@token_required
def delete_log(current_user: dict, log_id: str):
    return log_controller.delete_log(current_user, log_id)