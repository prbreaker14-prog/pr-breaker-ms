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
    workouts = list_workouts_service()
    return success_response("Workouts fetched", workouts)


def create_workout_controller():
    payload = request.get_json(silent=True) or {}
    name = payload.get("name")
    if not name:
        return error_response("name is required", 400)

    created = create_workout_service(payload)
    return success_response("Workout created", created, 201)


def get_workout_controller(workout_id: str):
    workout = get_workout_service(workout_id)
    if not workout:
        return error_response("Workout not found", 404)
    return success_response("Workout fetched", workout)


def update_workout_controller(workout_id: str):
    payload = request.get_json(silent=True) or {}
    updated = update_workout_service(workout_id, payload)
    if not updated:
        return error_response("Workout not found", 404)
    return success_response("Workout updated", updated)


def delete_workout_controller(workout_id: str):
    ok = delete_workout_service(workout_id)
    if not ok:
        return error_response("Workout not found", 404)
    return success_response("Workout deleted", {})

