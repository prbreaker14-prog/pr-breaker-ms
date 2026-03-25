from flask import request

from app.services.wgroups_service import (
    list_groups_service,
    create_group_service,
    get_group_service,
    update_group_service,
    delete_group_service,
    add_workout_to_group_service,
    remove_workout_from_group_service,
    list_group_workouts_service,
    clear_workout_from_all_groups_service,
)
from shared.utils.response import success_response, error_response


def _include_workouts_param() -> bool:
    value = (request.args.get("include_workouts") or "").lower()
    return value in ("1", "true", "yes")


def list_wgroups_controller():
    include_workouts = _include_workouts_param()
    user_id = request.user
    auth_header = request.headers.get("Authorization")
    groups = list_groups_service(user_id, include_workouts=include_workouts, auth_header=auth_header)
    return success_response("Groups fetched", groups)


def create_wgroups_controller():
    payload = request.get_json(silent=True) or {}
    workoutGroupName = payload.get("workoutGroupName")

    if not workoutGroupName:
        return error_response("workoutGroupName is required", 400)

    user_id = request.user
    created = create_group_service(payload, user_id)
    return success_response("Group created", created, 201)


def get_wgroups_controller(group_id: str):
    include_workouts = _include_workouts_param()
    user_id = request.user
    auth_header = request.headers.get("Authorization")
    group = get_group_service(group_id, user_id, include_workouts=include_workouts, auth_header=auth_header)
    if not group:
        return error_response("Group not found", 404)
    return success_response("Group fetched", group)


def update_wgroups_controller(group_id: str):
    payload = request.get_json(silent=True) or {}
    user_id = request.user
    updated = update_group_service(group_id, payload, user_id)
    if not updated:
        return error_response("Group not found", 404)
    return success_response("Group updated", updated)


def delete_wgroups_controller(group_id: str):
    user_id = request.user
    ok = delete_group_service(group_id, user_id)
    if not ok:
        return error_response("Group not found", 404)
    return success_response("Group deleted", {})


def add_workout_to_group_controller(group_id: str):
    payload = request.get_json(silent=True) or {}
    workout_id = payload.get("workout_id")
    user_id = request.user

    if not workout_id:
        return error_response("workout_id is required", 400)

    ok, result_or_msg = add_workout_to_group_service(group_id, workout_id, user_id)
    if not ok:
        return error_response(result_or_msg, 400)

    return success_response("Workout added to group", result_or_msg, 201)


def remove_workout_from_group_controller(group_id: str, workout_id: str):
    user_id = request.user
    ok, msg = remove_workout_from_group_service(group_id, workout_id, user_id)
    if not ok:
        return error_response(msg, 404)
    return success_response("Workout removed from group", {})


def list_group_workouts_controller(group_id: str):
    user_id = request.user
    auth_header = request.headers.get("Authorization")
    ok, result_or_msg = list_group_workouts_service(group_id, user_id, auth_header=auth_header)
    if not ok:
        return error_response(result_or_msg, 404)
    return success_response("Group workouts fetched", result_or_msg)


def clear_workout_from_all_groups_controller(workout_id: str):
    ok = clear_workout_from_all_groups_service(workout_id)
    if not ok:
        return error_response("Failed to clear workout from groups", 500)
    return success_response("Workout cleared from all groups", {})


