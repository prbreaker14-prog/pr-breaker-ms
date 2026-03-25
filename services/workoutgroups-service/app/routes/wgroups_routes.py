from flask import Blueprint

from shared.auth.auth_middleware import jwt_required

from app.controllers.wgroups_controller import (
    list_wgroups_controller,
    create_wgroups_controller,
    get_wgroups_controller,
    update_wgroups_controller,
    delete_wgroups_controller,
    add_workout_to_group_controller,
    remove_workout_from_group_controller,
    list_group_workouts_controller,
    clear_workout_from_all_groups_controller,
)


wgroups_bp = Blueprint("wgroups", __name__)


@wgroups_bp.get("")
@jwt_required
def list_wgroups():
    return list_wgroups_controller()


@wgroups_bp.post("")
@jwt_required
def create_wgroups():
    return create_wgroups_controller()


@wgroups_bp.get("/<wgroup_id>")
@jwt_required
def get_wgroups(wgroup_id: str):
    return get_wgroups_controller(wgroup_id)


@wgroups_bp.put("/<wgroup_id>")
@wgroups_bp.patch("/<wgroup_id>")
@jwt_required
def update_wgroups(wgroup_id: str):
    return update_wgroups_controller(wgroup_id)


@wgroups_bp.delete("/<wgroup_id>")
@jwt_required
def delete_wgroups(wgroup_id: str):
    return delete_wgroups_controller(wgroup_id)


@wgroups_bp.post("/<wgroup_id>/workouts")
@jwt_required
def add_workout_to_group(wgroup_id: str):
    return add_workout_to_group_controller(wgroup_id)


@wgroups_bp.delete("/<wgroup_id>/workouts/<workout_id>")
@jwt_required
def remove_workout_from_group(wgroup_id: str, workout_id: str):
    return remove_workout_from_group_controller(wgroup_id, workout_id)


@wgroups_bp.get("/<wgroup_id>/workouts")
@jwt_required
def list_group_workouts(wgroup_id: str):
    return list_group_workouts_controller(wgroup_id)


@wgroups_bp.delete("/workouts/<workout_id>")
@jwt_required
def clear_workout_from_all_groups(workout_id: str):
    return clear_workout_from_all_groups_controller(workout_id)

