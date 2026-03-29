import uuid
from datetime import datetime
from sqlalchemy import UniqueConstraint

from app import db


class WorkoutSession(db.Model):
    __tablename__ = "workout_sessions"

    __table_args__ = (
        UniqueConstraint("user_id", "class_id", "date", name="uq_user_class_date"),
    )

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    user_id = db.Column(db.String(36), nullable=False, index=True)
    class_id = db.Column(db.String(36), nullable=False, index=True)
    wgroupsName = db.Column(db.String(255))
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
            "wgroupsName": self.wgroupsName,
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
