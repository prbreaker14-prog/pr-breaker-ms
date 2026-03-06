import uuid
from datetime import datetime

from app import db


class Workout(db.Model):
    __tablename__ = "workouts"

    id = db.Column(db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()))
    name = db.Column(db.String(255), nullable=False)
    type = db.Column(db.String(100), nullable=True)
    has_sets = db.Column(db.Boolean, default=False, nullable=False)
    has_reps = db.Column(db.Boolean, default=False, nullable=False)
    has_weight = db.Column(db.Boolean, default=False, nullable=False)
    has_duration = db.Column(db.Boolean, default=False, nullable=False)
    has_calories = db.Column(db.Boolean, default=False, nullable=False)
    notes = db.Column(db.Text, nullable=True)
    created_at = db.Column(db.DateTime, default=datetime.utcnow, nullable=False)
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )

