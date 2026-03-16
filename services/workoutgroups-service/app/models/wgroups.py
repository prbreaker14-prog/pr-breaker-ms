import uuid
from datetime import datetime

from app import db


class WorkoutGroup(db.Model):
    __tablename__ = "groups"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    # User ID is stored as a plain string (no cross-service FK).
    user_id = db.Column(db.String(36), nullable=False)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

    workouts = db.relationship(
        "GroupWorkout",
        back_populates="group",
        cascade="all, delete-orphan",
    )

    def __repr__(self) -> str:  # pragma: no cover - helper
        return f"<WorkoutGroup {self.name}>"

