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
        "name": group.name,
        "user_id": group.user_id,
        "created_at": group.created_at.isoformat() if group.created_at else None,
        "updated_at": group.updated_at.isoformat() if group.updated_at else None,
    }

    # Always include linking info; optionally enrich with workout details
    workouts = []
    for gw in sorted(group.workouts, key=lambda gw: gw.position):
        item: Dict[str, Any] = {
            "id": gw.id,
            "workout_id": gw.workout_id,
            "position": gw.position,
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
        name=data.get("name"),
        user_id=user_id,
    )
    db.session.add(group)
    db.session.flush()

    workouts_data = data.get("workouts") or []
    for item in workouts_data:
        gw = GroupWorkout(
            group_id=group.id,
            workout_id=item.get("workout_id"),
            position=int(item.get("position", 0)),
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

    if "name" in data:
        group.name = data["name"]
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
                position=int(item.get("position", 0)),
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
    group_id: str, workout_id: str, user_id: str, position: Optional[int] = None
) -> Tuple[bool, Any]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False, "Group not found"

    existing = GroupWorkout.query.filter_by(
        group_id=group.id, workout_id=workout_id
    ).first()
    if existing:
        return False, "Workout is already in this group"

    if position is None:
        # Append at the end
        max_pos = (
            db.session.query(db.func.max(GroupWorkout.position))
            .filter_by(group_id=group.id)
            .scalar()
        )
        position = (max_pos or 0) + 1

    gw = GroupWorkout(
        group_id=group.id,
        workout_id=workout_id,
        position=int(position),
    )
    db.session.add(gw)
    db.session.commit()

    return True, {
        "id": gw.id,
        "group_id": gw.group_id,
        "workout_id": gw.workout_id,
        "position": gw.position,
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
    for gw in (
        GroupWorkout.query.filter_by(group_id=group.id)
        .order_by(GroupWorkout.position.asc())
        .all()
    ):
        detail = _fetch_workout_detail(gw.workout_id, auth_header=auth_header)
        items.append(
            {
                "id": gw.id,
                "group_id": gw.group_id,
                "workout_id": gw.workout_id,
                "position": gw.position,
                "workout": detail,
            }
        )
    return True, items


def reorder_group_workouts_service(
    group_id: str, user_id: str, order: List[Dict[str, Any]]
) -> Tuple[bool, Any]:
    group = WorkoutGroup.query.filter_by(id=group_id, user_id=user_id).first()
    if not group:
        return False, "Group not found"

    # order is expected as a list of { "workout_id": "...", "position": N }
    workout_ids_in_group = {
        gw.workout_id
        for gw in GroupWorkout.query.filter_by(group_id=group.id).all()
    }

    for entry in order:
        wid = entry.get("workout_id")
        pos = entry.get("position")
        if not wid or pos is None:
            return False, "Each entry in order must have workout_id and position"
        if wid not in workout_ids_in_group:
            return False, f"Workout {wid} is not in this group"

    for entry in order:
        wid = entry["workout_id"]
        pos = int(entry["position"])
        gw = GroupWorkout.query.filter_by(
            group_id=group.id, workout_id=wid
        ).first()
        if gw:
            gw.position = pos

    db.session.commit()

    # Return updated ordered list
    updated = (
        GroupWorkout.query.filter_by(group_id=group.id)
        .order_by(GroupWorkout.position.asc())
        .all()
    )
    result = [
        {
            "id": gw.id,
            "group_id": gw.group_id,
            "workout_id": gw.workout_id,
            "position": gw.position,
        }
        for gw in updated
    ]
    return True, result

