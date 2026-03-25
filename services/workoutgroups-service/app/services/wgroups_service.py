import os
from typing import Any, Dict, List, Optional, Tuple

import requests
from flask import current_app

from app import db
from app.models import WorkoutGroup, GroupWorkout


def _get_workout_service_base() -> str:
    # Prefer Flask config, fall back to environment variable
    base = current_app.config.get("WORKOUT_SERVICE_URL") or os.getenv(
        "WORKOUT_SERVICE_URL", "http://workout-service:5000"
    )
    return str(base).rstrip("/")


def _fetch_workout_detail(
    workout_id: str, auth_header: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    base = _get_workout_service_base()
    url = f"{base}/workouts/{workout_id}"
    headers: Dict[str, str] = {}
    if auth_header:
        headers["Authorization"] = auth_header

    try:
        resp = requests.get(url, headers=headers, timeout=5)
        if resp.status_code != 200:
            return None
        payload = resp.json()
        # Our workout-service wraps responses in {success, message, data}
        if isinstance(payload, dict) and "data" in payload:
            return payload["data"]
        return payload
    except requests.RequestException:
        return None


def _serialize_group(
    group: WorkoutGroup,
    include_workouts: bool = False,
    auth_header: Optional[str] = None,
) -> Dict[str, Any]:
    # Basic group fields
    data: Dict[str, Any] = {
        "id": group.id,
        "workoutGroupName": group.workoutGroupName,
        "user_id": group.user_id,
        "created_at": group.created_at.isoformat() if group.created_at else None,
        "updated_at": group.updated_at.isoformat() if group.updated_at else None,
    }

    # Always include linking info; optionally enrich with workout details
    workouts = []
    for gw in group.workouts:
        item: Dict[str, Any] = {
            "id": gw.id,
            "workout_id": gw.workout_id,
        }
        if include_workouts:
            detail = _fetch_workout_detail(gw.workout_id, auth_header=auth_header)
            if detail is not None:
                item["workout"] = detail
        workouts.append(item)

    data["workouts"] = workouts
    return data


def list_groups_service(
    user_id: str, include_workouts: bool = False, auth_header: Optional[str] = None
) -> List[Dict[str, Any]]:
    groups = WorkoutGroup.query.filter_by(user_id=user_id).order_by(WorkoutGroup.created_at.asc()).all()
    return [
        _serialize_group(g, include_workouts=include_workouts, auth_header=auth_header)
        for g in groups
    ]


def create_group_service(data: Dict[str, Any], user_id: str) -> Dict[str, Any]:
    group = WorkoutGroup(
        workoutGroupName=data.get("workoutGroupName"),
        user_id=user_id,
    )
    db.session.add(group)
    db.session.flush()

    workouts_data = data.get("workouts") or []
    for item in workouts_data:
        gw = GroupWorkout(
            group_id=group.id,
            workout_id=item.get("workout_id"),
        )
        db.session.add(gw)

    db.session.commit()
    return _serialize_group(group)


def get_group_service(
    group_id: str, user_id: str, include_workouts: bool = False, auth_header: Optional[str] = None
) -> Optional[Dict[str, Any]]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return None
    return _serialize_group(group, include_workouts=include_workouts, auth_header=auth_header)


def update_group_service(group_id: str, data: Dict[str, Any], user_id: str) -> Optional[Dict[str, Any]]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return None

    if "workoutGroupName" in data:
        group.workoutGroupName = data["workoutGroupName"]
    # Do not allow updating user_id

    # If workouts list is provided, replace links.
    if "workouts" in data:
        # Clear existing links
        GroupWorkout.query.filter_by(group_id=group.id).delete()
        workouts_data = data.get("workouts") or []
        for item in workouts_data:
            gw = GroupWorkout(
                group_id=group.id,
                workout_id=item.get("workout_id"),
            )
            db.session.add(gw)

    db.session.commit()
    return _serialize_group(group)


def delete_group_service(group_id: str, user_id: str) -> bool:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False
    # Explicitly delete link rows first, then the group (even though cascade also exists)
    GroupWorkout.query.filter_by(group_id=group.id).delete()
    db.session.delete(group)
    db.session.commit()
    return True


def add_workout_to_group_service(
    group_id: str, workout_id: str, user_id: str
) -> Tuple[bool, Any]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False, "Group not found"

    existing = GroupWorkout.query.filter_by(
        group_id=group.id, workout_id=workout_id
    ).first()
    if existing:
        return False, "Workout is already in this group"

    gw = GroupWorkout(
        group_id=group.id,
        workout_id=workout_id,
    )
    db.session.add(gw)
    db.session.commit()

    return True, {
        "id": gw.id,
        "group_id": gw.group_id,
        "workout_id": gw.workout_id,
    }


def remove_workout_from_group_service(
    group_id: str, workout_id: str, user_id: str
) -> Tuple[bool, str]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False, "Group not found"

    gw = GroupWorkout.query.filter_by(
        group_id=group.id, workout_id=workout_id
    ).first()
    if not gw:
        return False, "Workout not found in this group"

    db.session.delete(gw)
    db.session.commit()
    return True, "Removed"


def list_group_workouts_service(
    group_id: str, user_id: str, auth_header: Optional[str] = None
) -> Tuple[bool, Any]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False, "Group not found"

    items: List[Dict[str, Any]] = []
    for gw in GroupWorkout.query.filter_by(group_id=group.id).all():
        detail = _fetch_workout_detail(gw.workout_id, auth_header=auth_header)
        items.append(
            {
                "id": gw.id,
                "group_id": gw.group_id,
                "workout_id": gw.workout_id,
                "workout": detail,
            }
        )
    return True, items


def clear_workout_from_all_groups_service(workout_id: str) -> bool:
    GroupWorkout.query.filter_by(workout_id=workout_id).delete()
    db.session.commit()
    return True

