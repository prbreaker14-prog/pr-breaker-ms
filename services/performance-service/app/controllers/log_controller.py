from flask import request,jsonify

from app.services import log_service
from app.utils.response import error_response, success_response

from app import db
from app.models import WorkoutLog, WorkoutSession 


# Fields that are valid metric inputs on a set
_VALID_METRIC_KEYS = {"reps", "weight", "duration", "calories"}
_VALID_LOG_UPDATE_KEYS = _VALID_METRIC_KEYS | {"workoutName"}


def log_sets(current_user: dict):
    body = request.get_json(silent=True) or {}

    session_id = body.get("sessionId")
    workout_id = body.get("workoutId")
    workout_name = body.get("workoutName")
    sets       = body.get("sets")

    if not session_id or not isinstance(session_id, str):
        return error_response("sessionId (UUID string) is required.", status_code=400)
    if not workout_id or not isinstance(workout_id, str):
        return error_response("workoutId (UUID string) is required.", status_code=400)
    if not workout_name or not isinstance(workout_name, str):
        return error_response("workoutName (string) is required.", status_code=400)
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
            workout_name=workout_name.strip(),
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
    from datetime import date

    workout_id = request.args.get("workoutId") or None

    # Parse fromDate
    raw_from = request.args.get("fromDate")
    from_date = None
    if raw_from:
        try:
            from_date = date.fromisoformat(raw_from)
        except ValueError:
            return error_response("Invalid fromDate format. Use YYYY-MM-DD.", status_code=400)

    # Parse toDate
    raw_to = request.args.get("toDate")
    to_date = None
    if raw_to:
        try:
            to_date = date.fromisoformat(raw_to)
        except ValueError:
            return error_response("Invalid toDate format. Use YYYY-MM-DD.", status_code=400)

    try:
        logs = log_service.get_logs_for_session(
            session_id=session_id,
            requesting_user_id=current_user["id"],
            workout_id=workout_id,
            from_date=from_date,
            to_date=to_date,
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
    updatable = {}
    for key in _VALID_LOG_UPDATE_KEYS:
        if key in body:
            if key == "workoutName":
                updatable["workout_name"] = body[key]
            else:
                updatable[key] = body[key]
    if not updatable:
        return error_response(
            "Provide at least one of: reps, weight, duration, calories, workoutName.",
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

def delete_workout_log():
    data = request.get_json()

    log_id = data.get("logId")
    workout_id = data.get("workoutId")
    set_number = data.get("setNumber")
    date = data.get("date")
    user_id = request.user_id  # assuming auth middleware

    try:
        if log_id:
            # 🔥 Delete by logId
            log = WorkoutLog.query.filter_by(id=log_id, user_id=user_id).first()

            if not log:
                return jsonify({"message": "Log not found"}), 404

            db.session.delete(log)

        else:
            # 🔥 Resolve session from date
            session = WorkoutSession.query.filter_by(
                user_id=user_id,
                date=date
            ).first()

            if not session:
                return jsonify({"message": "Session not found"}), 404

            log = WorkoutLog.query.filter_by(
                user_id=user_id,
                session_id=session.id,
                workout_id=workout_id,
                set_number=set_number
            ).first()

            if not log:
                return jsonify({"message": "Log not found"}), 404

            db.session.delete(log)

        db.session.commit()

        return jsonify({"message": "Log deleted successfully"}), 200

    except Exception as e:
        db.session.rollback()
        return jsonify({"error": str(e)}), 500



def upsert_workout_logs(current_user: dict):
    body = request.get_json(silent=True) or {}

    # date = body.get("date")
    session_id = body.get("sessionId")
    workout_id = body.get("workoutId")
    workout_name = body.get("workoutName")
    sets = body.get("sets", [])

    user_id = current_user["id"]

    #  Validation
    if not user_id:
        return error_response("Unauthorized: user not found", status_code=401)

    if not session_id:
        return error_response("date is required (YYYY-MM-DD)", status_code=400)

    if not workout_id:
        return error_response("workoutId is required", status_code=400)

    if not workout_name or not isinstance(workout_name, str):
        return error_response("workoutName is required", status_code=400)

    if not sets or not isinstance(sets, list):
        return error_response("sets must be a non-empty list", status_code=400)

    for i, s in enumerate(sets, start=1):
        if not isinstance(s, dict):
            return error_response(f"Set {i} must be an object", status_code=400)

        if not s.get("setNumber"):
            return error_response(f"Set {i} missing setNumber", status_code=400)

    try:
        logs = log_service.upsert_workout_logs(
            user_id=user_id,
            session_id=session_id,
            workout_id=workout_id,
            workout_name=workout_name.strip(),
            sets=sets
        )

    except ValueError as e:
        return error_response(str(e), status_code=404)

    except PermissionError as e:
        return error_response(str(e), status_code=403)

    except Exception as e:
        return error_response(f"Failed to upsert logs: {str(e)}", status_code=500)

    return success_response(
        "Logs processed successfully",
        data=[log.to_dict() for log in logs],
        status_code=200
    )