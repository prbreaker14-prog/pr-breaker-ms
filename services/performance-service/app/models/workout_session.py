import uuid
from datetime import datetime

from app import db


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    class_id = db.Column(db.String(36), nullable=False, index=True)
    date = db.Column(db.Date, nullable=False, index=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    logs = db.relationship(
        "WorkoutLog",
        back_populates="session",
        cascade="all, delete-orphan",
        lazy="select",
    )


    def to_dict(self, include_logs: bool = False) -> dict:
        data = {
            "id": self.id,
            "userId": self.user_id,
            "classId": self.class_id,
            "date": self.date.isoformat() if self.date else None,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }
        if include_logs:
            data["logs"] = [log.to_dict() for log in self.logs]
        return data

    def __repr__(self) -> str:
        return (
            f"<WorkoutSession id={self.id} user={self.user_id} date={self.date}>"
        )
