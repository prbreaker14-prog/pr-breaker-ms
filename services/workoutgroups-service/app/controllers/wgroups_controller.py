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
    reorder_group_workouts_service,
)
from shared.utils.response import success_response, error_response


def _include_workouts_param() -> bool:
    value = (request.args.get("include_workouts") or "").lower()
    return value in ("1", "true", "yes")


def list_wgroups_controller():
    include_workouts = _include_workouts_param()
    auth_header = request.headers.get("Authorization")
    groups = list_groups_service(include_workouts=include_workouts, auth_header=auth_header)
    return success_response("Groups fetched", groups)


def create_wgroups_controller():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    user_id = payload.get("user_id")

    if not name or not user_id:
        return error_response("name and user_id are required", 400)

    created = create_group_service(payload)
    return success_response("Group created", created, 201)


def get_wgroups_controller(group_id: str):
    include_workouts = _include_workouts_param()
    auth_header = request.headers.get("Authorization")
    group = get_group_service(group_id, include_workouts=include_workouts, auth_header=auth_header)
    if not group:
        return error_response("Group not found", 404)
    return success_response("Group fetched", group)


def update_wgroups_controller(group_id: str):
    payload = request.get_json(silent=True) or {}
    updated = update_group_service(group_id, payload)
    if not updated:
        return error_response("Group not found", 404)
    return success_response("Group updated", updated)


def delete_wgroups_controller(group_id: str):
    ok = delete_group_service(group_id)
    if not ok:
        return error_response("Group not found", 404)
    return success_response("Group deleted", {})


def add_workout_to_group_controller(group_id: str):
    payload = request.get_json(silent=True) or {}
    workout_id = payload.get("workout_id")
    position = payload.get("position")

    if not workout_id:
        return error_response("workout_id is required", 400)

    ok, result_or_msg = add_workout_to_group_service(group_id, workout_id, position)
    if not ok:
        return error_response(result_or_msg, 400)

    return success_response("Workout added to group", result_or_msg, 201)


def remove_workout_from_group_controller(group_id: str, workout_id: str):
    ok, msg = remove_workout_from_group_service(group_id, workout_id)
    if not ok:
        return error_response(msg, 404)
    return success_response("Workout removed from group", {})


def list_group_workouts_controller(group_id: str):
    auth_header = request.headers.get("Authorization")
    ok, result_or_msg = list_group_workouts_service(group_id, auth_header=auth_header)
    if not ok:
        return error_response(result_or_msg, 404)
    return success_response("Group workouts fetched", result_or_msg)


def reorder_group_workouts_controller(group_id: str):
    payload = request.get_json(silent=True) or {}
    order = payload.get("order") or []
    if not isinstance(order, list) or not order:
        return error_response("order must be a non-empty list", 400)

    ok, result_or_msg = reorder_group_workouts_service(group_id, order)
    if not ok:
        return error_response(result_or_msg, 400)
    return success_response("Group workouts reordered", result_or_msg)


