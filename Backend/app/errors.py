from flask import jsonify


# PUBLIC_INTERFACE
def error_response(status_code: int, code: str, message: str):
    """Return standardized JSON error response."""
    payload = {"error": {"code": code, "message": message}}
    return jsonify(payload), status_code
