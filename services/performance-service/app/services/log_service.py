from typing import Optional

from app import db
from app.models import WorkoutLog
from app.models import WorkoutSession
from app.services.session_service import get_session_by_id


def _verify_session_ownership(session: WorkoutSession, requesting_user_id: str) -> None:
    if session.user_id != requesting_user_id:
        raise PermissionError("You do not have permission to log to this session.")


def log_sets( session_id: str, workout_id: str, sets: list[dict], requesting_user_id: str,) -> list[WorkoutLog]:
    session = get_session_by_id(session_id)
    _verify_session_ownership(session, requesting_user_id)

    created_logs = []
    for index, set_data in enumerate(sets, start=1):
        log = WorkoutLog(
            session_id=session_id,
            workout_id=workout_id,
            set_number=index,
            reps=set_data.get("reps"),
            weight=set_data.get("weight"),
            duration=set_data.get("duration"),
            calories=set_data.get("calories"),
        )
        db.session.add(log)
        created_logs.append(log)

    db.session.commit()
    return created_logs


def get_logs_for_session( session_id: str, requesting_user_id: str, workout_id: Optional[str] = None,) -> list[WorkoutLog]:
    session = get_session_by_id(session_id)
    _verify_session_ownership(session, requesting_user_id)

    query = WorkoutLog.query.filter_by(session_id=session_id)
    if workout_id is not None:
        query = query.filter_by(workout_id=workout_id)

    return query.order_by(WorkoutLog.workout_id, WorkoutLog.set_number).all()


def get_history_for_workout( user_id: str, workout_id: str, limit: int = 10,) -> list[dict]:
    rows = ( db.session.query(WorkoutLog, WorkoutSession).join(WorkoutSession, WorkoutLog.session_id == WorkoutSession.id)
        .filter(
            WorkoutSession.user_id == user_id,
            WorkoutLog.workout_id == workout_id,
        )
        .order_by(WorkoutSession.date.desc(), WorkoutLog.set_number.asc())
        .all()
    )
    sessions_seen: dict[str, dict] = {}
    for log, session in rows:
        if session.id not in sessions_seen:
            if len(sessions_seen) >= limit:
                break
            sessions_seen[session.id] = {
                "sessionId": session.id,
                "date": session.date.isoformat(),
                "classId": session.class_id,
                "sets": [],
            }
        sessions_seen[session.id]["sets"].append({
            "setNumber": log.set_number,
            "reps": log.reps,
            "weight": log.weight,
            "duration": log.duration,
            "calories": log.calories,
        })

    return list(sessions_seen.values())


def update_log( log_id: str, requesting_user_id: str, data: dict,) -> WorkoutLog:
    log = db.session.get(WorkoutLog, log_id)
    if not log:
        raise ValueError(f"Log '{log_id}' not found.")

    session = get_session_by_id(log.session_id)
    _verify_session_ownership(session, requesting_user_id)

    for field in ("reps", "weight", "duration", "calories"):
        if field in data:
            setattr(log, field, data[field])

    db.session.commit()
    return log


def delete_log(log_id: str, requesting_user_id: str) -> None:
    log = db.session.get(WorkoutLog, log_id)
    if not log:
        raise ValueError(f"Log '{log_id}' not found.")

    session = get_session_by_id(log.session_id)
    _verify_session_ownership(session, requesting_user_id)

    db.session.delete(log)
    db.session.commit()