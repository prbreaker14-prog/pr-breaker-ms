from flask import jsonify


def success_response(message: str, data=None, status_code: int = 200):
    """
    Return a Flask JSON response in the standard ApiResponse envelope.

        { "success": true, "message": "...", "data": { ... } }

    Matches the Spring monolith's ApiResponse.success() exactly.
    """
    return (
        jsonify({"success": True, "message": message, "data": data}),
        status_code,
    )


def error_response(message: str, data=None, status_code: int = 400):
    """
    Return a Flask JSON error response in the standard ApiResponse envelope.

        { "success": false, "message": "...", "data": null }
    """
    return (
        jsonify({"success": False, "message": message, "data": data}),
        status_code,
    )