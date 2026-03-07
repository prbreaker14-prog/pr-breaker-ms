from flask import request

from app.services import log_service
from app.utils.response import error_response, success_response

# Fields that are valid metric inputs on a set
_VALID_METRIC_KEYS = {"reps", "weight", "duration", "calories"}


def log_sets(current_user: dict):
    body = request.get_json(silent=True) or {}

    session_id = body.get("sessionId")
    workout_id = body.get("workoutId")
    sets       = body.get("sets")

    if not session_id or not isinstance(session_id, str):
        return error_response("sessionId (UUID string) is required.", status_code=400)
    if not workout_id or not isinstance(workout_id, str):
        return error_response("workoutId (UUID string) is required.", status_code=400)
    if not sets or not isinstance(sets, list) or len(sets) == 0:
        return error_response(
            "sets must be a non-empty list of set objects.", status_code=400
        )

    for i, s in enumerate(sets, start=1):
        if not isinstance(s, dict):
            return error_response(f"Set {i} must be an object.", status_code=400)
        if not any(k in s for k in _VALID_METRIC_KEYS):
            return error_response(
                f"Set {i} must include at least one of: reps, weight, duration, calories.",
                status_code=400,
            )

    try:
        logs = log_service.log_sets(
            session_id=session_id.strip(),
            workout_id=workout_id.strip(),
            sets=sets,
            requesting_user_id=current_user["id"],
        )
    except ValueError as e:
        return error_response(str(e), status_code=404)
    except PermissionError as e:
        return error_response(str(e), status_code=403)
    except Exception as e:
        return error_response(f"Failed to log sets: {str(e)}", status_code=500)

    return success_response(
        f"{len(logs)} set(s) logged.",
        data=[log.to_dict() for log in logs],
        status_code=201,
    )


def get_logs_for_session(current_user: dict, session_id: str):
    workout_id = request.args.get("workoutId") or None
    try:
        logs = log_service.get_logs_for_session(
            session_id=session_id,
            requesting_user_id=current_user["id"],
            workout_id=workout_id,
        )
    except ValueError as e:
        return error_response(str(e), status_code=404)
    except PermissionError as e:
        return error_response(str(e), status_code=403)

    return success_response(f"{len(logs)} log(s) found.", data=[log.to_dict() for log in logs])


def get_workout_history(current_user: dict, workout_id: str):
    raw_limit = request.args.get("limit", default=10, type=int)
    limit     = min(max(raw_limit, 1), 50)

    history = log_service.get_history_for_workout(
        user_id=current_user["id"],
        workout_id=workout_id,
        limit=limit,
    )

    return success_response(
        f"{len(history)} session(s) of history found.",
        data=history,
    )


def update_log(current_user: dict, log_id: str):
    body = request.get_json(silent=True) or {}
    updatable = {k: v for k, v in body.items() if k in _VALID_METRIC_KEYS}
    if not updatable:
        return error_response(
            "Provide at least one of: reps, weight, duration, calories.",
            status_code=400,
        )

    try:
        log = log_service.update_log(
            log_id=log_id,
            requesting_user_id=current_user["id"],
            data=updatable,
        )
    except ValueError as e:
        return error_response(str(e), status_code=404)
    except PermissionError as e:
        return error_response(str(e), status_code=403)

    return success_response("Log updated.", data=log.to_dict())


def delete_log(current_user: dict, log_id: str):
    try:
        log_service.delete_log(
            log_id=log_id,
            requesting_user_id=current_user["id"],
        )
    except ValueError as e:
        return error_response(str(e), status_code=404)
    except PermissionError as e:
        return error_response(str(e), status_code=403)

    return success_response("Log entry deleted.")