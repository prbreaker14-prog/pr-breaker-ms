from datetime import date as date_type
from typing import Optional

from app import db
from app.models import WorkoutLog
from app.models import WorkoutSession 
from app.services.session_service import get_session_by_id


def _verify_session_ownership(session: WorkoutSession, requesting_user_id: str) -> None:
    if session.user_id != requesting_user_id:
        raise PermissionError("You do not have permission to log to this session.")


def log_sets(session_id: str, workout_id: str, sets: list[dict], requesting_user_id: str) -> list[WorkoutLog]:

    session = get_session_by_id(session_id)
    _verify_session_ownership(session, requesting_user_id)

    # 🔹 Step 1: check existing logs in this session
    existing_logs = (
        WorkoutLog.query
        .filter_by(session_id=session_id, workout_id=workout_id)
        .order_by(WorkoutLog.set_number.asc())
        .all()
    )

    # 🚨 CASE: FIRST TIME ENTRY
    if not existing_logs:

        # 🔥 Step 2: find latest session logs for this workout
        latest_session_logs = (
            db.session.query(WorkoutLog, WorkoutSession)
            .join(WorkoutSession, WorkoutLog.session_id == WorkoutSession.id)
            .filter(
                WorkoutSession.user_id == requesting_user_id,
                WorkoutLog.workout_id == workout_id,
                WorkoutLog.session_id != session_id  # exclude current
            )
            .order_by(WorkoutSession.date.desc(), WorkoutLog.set_number.asc())
            .all()
        )

        new_logs = []

        if latest_session_logs:
            # ✅ group by first/latest session
            latest_session_id = latest_session_logs[0][1].id

            latest_sets = [
                log for log, s in latest_session_logs
                if s.id == latest_session_id
            ]

            # 🔥 replicate all sets
            for log in latest_sets:
                new_log = WorkoutLog(
                    user_id=requesting_user_id,
                    session_id=session_id,
                    workout_id=workout_id,
                    set_number=log.set_number,
                    reps=log.reps,
                    weight=log.weight,
                    duration=log.duration,
                    calories=log.calories,
                )
                db.session.add(new_log)
                new_logs.append(new_log)

        else:
            # ✅ No history → create default set 1
            new_log = WorkoutLog(
                user_id=requesting_user_id,
                session_id=session_id,
                workout_id=workout_id,
                set_number=1,
                reps=None,
                weight=None,
                duration=None,
                calories=None,
            )
            db.session.add(new_log)
            new_logs.append(new_log)

        db.session.commit()
        return new_logs

    # 🔹 CASE: ALREADY EXISTS → NORMAL UPDATE FLOW
    updated_logs = []

    for index, set_data in enumerate(sets, start=1):

        log = existing_logs[index - 1] if index <= len(existing_logs) else None

        if log:
            log.reps = set_data.get("reps", log.reps)
            log.weight = set_data.get("weight", log.weight)
            log.duration = set_data.get("duration", log.duration)
            log.calories = set_data.get("calories", log.calories)

        else:
            log = WorkoutLog(
                user_id=requesting_user_id,
                session_id=session_id,
                workout_id=workout_id,
                set_number=index,
                reps=set_data.get("reps"),
                weight=set_data.get("weight"),
                duration=set_data.get("duration"),
                calories=set_data.get("calories"),
            )
            db.session.add(log)

        updated_logs.append(log)

    db.session.commit()
    return updated_logs
def get_logs_for_session(
    session_id: str,
    requesting_user_id: str,
    workout_id: Optional[str] = None,
    from_date: Optional[date_type] = None,
    to_date: Optional[date_type] = None,
) -> list[WorkoutLog]:
    session = get_session_by_id(session_id)
    _verify_session_ownership(session, requesting_user_id)

    query = (
        WorkoutLog.query
        .join(WorkoutSession, WorkoutLog.session_id == WorkoutSession.id)
        .filter(WorkoutLog.session_id == session_id)
    )

    if workout_id is not None:
        query = query.filter(WorkoutLog.workout_id == workout_id)
    if from_date is not None:
        query = query.filter(WorkoutSession.date >= from_date)
    if to_date is not None:
        query = query.filter(WorkoutSession.date <= to_date)

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

def upsert_workout_logs(user_id: str, session_id: str, workout_id: str, sets: list):
    from app.models import WorkoutLog, WorkoutSession
    from app import db

    # # 🔹 Step 1: get session
    # session = WorkoutSession.query.filter_by(
    #     user_id=user_id,
    #     session_id=session_id
    # ).first()

    # if not session:
    #     raise ValueError("Session not found")

    # session_id = session.id

    #  Step 2: existing logs
    existing_logs = WorkoutLog.query.filter_by(
        user_id=user_id,
        session_id=session_id,
        workout_id=workout_id
    ).all()

    existing_map = {log.set_number: log for log in existing_logs}

    results = []

    # 🔹 Step 3: upsert
    for s in sets:
        set_number = s.get("setNumber")

        log = existing_map.get(set_number)

        if log:
            # UPDATE
            log.reps = s.get("reps", log.reps)
            log.weight = s.get("weight", log.weight)
            log.duration = s.get("duration", log.duration)
            log.calories = s.get("calories", log.calories)

        else:
            # CREATE
            log = WorkoutLog(
                user_id=user_id,
                session_id=session_id,
                workout_id=workout_id,
                set_number=set_number,
                reps=s.get("reps"),
                weight=s.get("weight"),
                duration=s.get("duration"),
                calories=s.get("calories"),
            )
            db.session.add(log)

        results.append(log)

    db.session.commit()
    return results