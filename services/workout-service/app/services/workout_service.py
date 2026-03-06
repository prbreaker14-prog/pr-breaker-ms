from typing import Any, Dict, List, Optional

from app import db
from app.models import Workout


def _serialize(workout: Workout) -> Dict[str, Any]:
    return {
        "id": workout.id,
        "name": workout.name,
        "type": workout.type,
        "has_sets": workout.has_sets,
        "has_reps": workout.has_reps,
        "has_weight": workout.has_weight,
        "has_duration": workout.has_duration,
        "has_calories": workout.has_calories,
        "notes": workout.notes,
        "created_at": workout.created_at.isoformat() if workout.created_at else None,
        "updated_at": workout.updated_at.isoformat() if workout.updated_at else None,
    }


def list_workouts_service() -> List[Dict[str, Any]]:
    workouts = Workout.query.order_by(Workout.name.asc()).all()
    return [_serialize(w) for w in workouts]


def create_workout_service(data: Dict[str, Any]) -> Dict[str, Any]:
    workout = Workout(
        name=data.get("name"),
        type=data.get("type"),
        has_sets=bool(data.get("has_sets", False)),
        has_reps=bool(data.get("has_reps", False)),
        has_weight=bool(data.get("has_weight", False)),
        has_duration=bool(data.get("has_duration", False)),
        has_calories=bool(data.get("has_calories", False)),
        notes=data.get("notes"),
    )
    db.session.add(workout)
    db.session.commit()
    return _serialize(workout)


def get_workout_service(workout_id: str) -> Optional[Dict[str, Any]]:
    workout = Workout.query.get(workout_id)
    if not workout:
        return None
    return _serialize(workout)


def update_workout_service(workout_id: str, data: Dict[str, Any]) -> Optional[Dict[str, Any]]:
    workout = Workout.query.get(workout_id)
    if not workout:
        return None

    for field in [
        "name",
        "type",
        "has_sets",
        "has_reps",
        "has_weight",
        "has_duration",
        "has_calories",
        "notes",
    ]:
        if field in data:
            setattr(workout, field, data[field])

    db.session.commit()
    return _serialize(workout)


def delete_workout_service(workout_id: str) -> bool:
    workout = Workout.query.get(workout_id)
    if not workout:
        return False
    db.session.delete(workout)
    db.session.commit()
    return True

