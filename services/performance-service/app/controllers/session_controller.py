from datetime import date
from flask import request
from app.services import session_service
from app.utils.response import error_response, success_response


def _parse_date_param(param_name: str):
    raw = request.args.get(param_name)
    if not raw:
        return None
    try:
        return date.fromisoformat(raw)
    except ValueError:
        return error_response(
            f"Invalid {param_name} format. Use YYYY-MM-DD.", status_code=400
        )


from datetime import date
from flask import request
from app.services import session_service
from app.utils.response import error_response, success_response


def create_session(current_user: dict):
    body = request.get_json(silent=True) or {}

    class_id = body.get("classId")
    if not class_id or not isinstance(class_id, str) or not class_id.strip():
        return error_response("classId (UUID string) is required.", status_code=400)

    raw_date = body.get("date")
    if raw_date:
        try:
            session_date = date.fromisoformat(raw_date)
        except ValueError:
            return error_response(
                "Invalid date format. Use YYYY-MM-DD.", status_code=400
            )
    else:
        session_date = date.today()

    try:
        # ✅ Now returns (session, already_exists)
        session, already_exists = session_service.create_session(
            user_id=current_user["id"],
            class_id=class_id.strip(),
            date=session_date,
        )

    except Exception as e:
        return error_response(f"Failed to create session: {str(e)}", status_code=500)

    # ✅ Handle duplicate case
    if already_exists:
        return success_response(
            "Session already exists.",
            data=session.to_dict(),
            status_code=200
        )

    # ✅ Normal creation
    return success_response(
        "Workout session created.",
        data=session.to_dict(),
        status_code=201
    )

def list_sessions(current_user: dict):
    class_id  = request.args.get("classId") or None
    from_date = _parse_date_param("fromDate")
    to_date   = _parse_date_param("toDate")
    if isinstance(from_date, tuple):
        return from_date
    if isinstance(to_date, tuple):
        return to_date

    sessions = session_service.get_sessions_for_user(
        user_id=current_user["id"],
        class_id=class_id,
        from_date=from_date,
        to_date=to_date,
    )

    return success_response(
        f"{len(sessions)} session(s) found.",
        data=[s.to_dict() for s in sessions],
    )


def get_session(current_user: dict, session_id: str):
    try:
        session = session_service.get_session_by_id(session_id)
    except ValueError as e:
        return error_response(str(e), status_code=404)

    return success_response("Session retrieved.", data=session.to_dict(include_logs=True))


def delete_session(current_user: dict, session_id: str):
    try:
        session_service.delete_session(
            session_id=session_id,
            requesting_user_id=current_user["id"],
        )
    except ValueError as e:
        return error_response(str(e), status_code=404)
    except PermissionError as e:
        return error_response(str(e), status_code=403)

    return success_response("Session deleted.")