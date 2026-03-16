import uuid
from datetime import datetime

from app import db


class GroupWorkout(db.Model):
    __tablename__ = "group_workouts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    group_id = db.Column(db.String(36), db.ForeignKey("groups.id"), nullable=False)
    # Workout ID is a plain string, not a foreign key (workout lives in another service).
    workout_id = db.Column(db.String(36), nullable=False)
    position = db.Column(db.Integer, nullable=False, default=0)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)

    group = db.relationship("WorkoutGroup", back_populates="workouts")

