from app import db

from .wgroups import WorkoutGroup
from .workout_wgroups import GroupWorkout

__all__ = ["WorkoutGroup", "GroupWorkout", "db"]

