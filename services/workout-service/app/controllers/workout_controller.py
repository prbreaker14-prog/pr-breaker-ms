from flask import request

from app.services.workout_service import (
    list_workouts_service,
    create_workout_service,
    get_workout_service,
    update_workout_service,
    delete_workout_service,
)
from shared.utils.response import success_response, error_response


def list_workouts_controller():
    user_id = request.user
    workouts = list_workouts_service(user_id)
    return success_response("Workouts fetched", workouts)


def create_workout_controller():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name:
        return error_response("name is required", 400)

    user_id = request.user
    created = create_workout_service(payload, user_id)
    return success_response("Workout created", created, 201)


def get_workout_controller(workout_id: str):
    user_id = request.user
    workout = get_workout_service(workout_id, user_id)
    if not workout:
        return error_response("Workout not found", 404)
    return success_response("Workout fetched", workout)


def update_workout_controller(workout_id: str):
    payload = request.get_json(silent=True) or {}
    user_id = request.user
    updated = update_workout_service(workout_id, payload, user_id)
    if not updated:
        return error_response("Workout not found", 404)
    return success_response("Workout updated", updated)


def delete_workout_controller(workout_id: str):
    user_id = request.user
    ok = delete_workout_service(workout_id, user_id)
    if not ok:
        return error_response("Workout not found", 404)
    return success_response("Workout deleted", {})

