from flask import Blueprint

from shared.auth.auth_middleware import jwt_required

from app.controllers.workout_controller import (
    list_workouts_controller,
    create_workout_controller,
    get_workout_controller,
    update_workout_controller,
    delete_workout_controller,
)


workouts_bp = Blueprint("workouts", __name__)


@workouts_bp.get("")
@jwt_required
def list_workouts():
    return list_workouts_controller()


@workouts_bp.post("")
@jwt_required
def create_workout():
    return create_workout_controller()


@workouts_bp.get("/<workout_id>")
@jwt_required
def get_workout(workout_id: str):
    return get_workout_controller(workout_id)


@workouts_bp.put("/<workout_id>")
@workouts_bp.patch("/<workout_id>")
@jwt_required
def update_workout(workout_id: str):
    return update_workout_controller(workout_id)


@workouts_bp.delete("/<workout_id>")
@jwt_required
def delete_workout(workout_id: str):
    return delete_workout_controller(workout_id)

