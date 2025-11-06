def is_error_response(payload):
    """
    Basic check for standardized error responses in this project.
    Accepts either {"error": "..."} or {"error": {"code": "...", "message": "..."}} per specs.
    """
    if not isinstance(payload, dict):
        return False
    if "error" not in payload:
        return False
    err = payload["error"]
    if isinstance(err, str):
        return True
    if isinstance(err, dict):
        return "message" in err
    return False
