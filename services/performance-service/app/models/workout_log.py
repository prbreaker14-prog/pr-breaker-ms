import uuid
from datetime import datetime

from app import db


class WorkoutLog(db.Model):
    __tablename__ = "workout_logs"

    __table_args__ = (
    db.UniqueConstraint(
        "session_id", "workout_id", "set_number",
        name="unique_session_workout_set"
    ),
)

    id = db.Column( db.String(36), primary_key=True, default=lambda: str(uuid.uuid4()),)
    session_id = db.Column(db.String(36), db.ForeignKey("workout_sessions.id", ondelete="CASCADE"), nullable=False, index=True,)
    user_id = db.Column(db.String(36),nullable=False,index=True,)
    workout_id = db.Column(db.String(36), nullable=False, index=True)
    set_number = db.Column(db.Integer, nullable=False)
    reps = db.Column(db.Integer, nullable=True)
    weight = db.Column(db.Float, nullable=True)    
    duration = db.Column(db.Float, nullable=True) 
    calories = db.Column(db.Float, nullable=True)

    created_at = db.Column(
        db.DateTime, default=datetime.utcnow, nullable=False
    )
    updated_at = db.Column(
        db.DateTime, default=datetime.utcnow, onupdate=datetime.utcnow, nullable=False
    )
    session = db.relationship("WorkoutSession", back_populates="logs")

    #── Serialisation ──────────────────────────────────────────────────────────

    def to_dict(self) -> dict:
        """Return a JSON-safe dictionary of this log entry."""
        return {
            "id": self.id,
            "sessionId": self.session_id,
            "userId": self.user_id,  
            "workoutId": self.workout_id,
            "setNumber": self.set_number,
            "reps": self.reps,
            "weight": self.weight,
            "duration": self.duration,
            "calories": self.calories,
            "createdAt": self.created_at.isoformat() if self.created_at else None,
            "updatedAt": self.updated_at.isoformat() if self.updated_at else None,
        }

    def __repr__(self) -> str:
        return (
            f"<WorkoutLog id={self.id} session={self.session_id} "
            f"workout={self.workout_id} set={self.set_number}>"
        )