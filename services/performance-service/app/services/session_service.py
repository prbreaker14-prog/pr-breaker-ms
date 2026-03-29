from datetime import date as date_type
from typing import Optional
import requests

from app import db
from app.models import WorkoutSession

from sqlalchemy.exc import IntegrityError


def create_session(user_id: str, class_id: str, wgroupsName: str, date: date_type):
    existing_session = (
        WorkoutSession.query
        .filter_by(user_id=user_id, class_id=class_id, date=date)
        .first()
    )

    if existing_session:
        return existing_session, True  # already exists

    try:
        session = WorkoutSession(
            user_id=user_id,
            class_id=class_id,
            wgroupsName=wgroupsName,
            date=date,
        )
        db.session.add(session)
        db.session.commit()

        return session, False  # newly created

    except IntegrityError:
        db.session.rollback()

        existing_session = (
            WorkoutSession.query
            .filter_by(user_id=user_id, class_id=class_id, wgroupsName=wgroupsName, date=date)
            .first()
        )

        return existing_session, True

def get_session_by_id(session_id: str) -> WorkoutSession:
    session = db.session.get(WorkoutSession, session_id)
    if not session:
        raise ValueError(f"Session '{session_id}' not found.")
    return session


def get_sessions_for_user(
    user_id: str,
    class_id: Optional[str] = None,
    from_date: Optional[date_type] = None,
    to_date: Optional[date_type] = None,
) -> list[WorkoutSession]:
    # Start from all sessions for this user
    query = WorkoutSession.query.filter_by(user_id=user_id)

    if class_id is not None:
        query = query.filter_by(class_id=class_id)
    if from_date is not None:
        query = query.filter(WorkoutSession.date >= from_date)
    if to_date is not None:
        query = query.filter(WorkoutSession.date <= to_date)

    return query.order_by(WorkoutSession.date.desc()).all()


def delete_session(session_id: str, requesting_user_id: str) -> None:
    session = get_session_by_id(session_id)

    if session.user_id != requesting_user_id:
        raise PermissionError("You do not have permission to delete this session.")

    db.session.delete(session)
    db.session.commit()
