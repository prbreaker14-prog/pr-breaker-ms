import typing as t

from flask import jsonify


def success_response(
    message: str = "Operation successful",
    data: t.Optional[t.Any] = None,
    status_code: int = 200,
):
    payload = {
        "success": True,
        "message": message,
        "data": data or {},
    }
    return jsonify(payload), status_code


def error_response(
    message: str = "Operation failed",
    status_code: int = 400,
    data: t.Optional[t.Any] = None,
):
    payload = {
        "success": False,
        "message": message,
        "data": data or {},
    }
    return jsonify(payload), status_code

