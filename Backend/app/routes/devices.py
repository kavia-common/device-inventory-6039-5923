from flask import request, jsonify
from flask_smorest import Blueprint
from flask.views import MethodView
from pymongo import MongoClient
import os
from typing import Dict, Any, List

# Initialize blueprint for Devices routes
blp_devices = Blueprint(
    "Devices",
    "devices",
    url_prefix="/devices",
    description="Device inventory management operations",
)

# Environment variables for MongoDB configuration
# Note: These should be provided via .env in deployment. Sensible defaults provided for local dev/tests.
MONGO_URI = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
MONGO_DB = os.getenv("MONGODB_DB", "device_inventory")
MONGO_COLLECTION = os.getenv("MONGODB_COLLECTION", "devices")


def _get_collection():
    """
    Internal helper to access the MongoDB collection using pymongo.
    Tests patch pymongo.MongoClient, so this indirection is important.
    """
    client = MongoClient(MONGO_URI)
    db = client[MONGO_DB]
    collection = db[MONGO_COLLECTION]
    return collection


def _error(code: int, message: str):
    """
    Standardized JSON error response body and status code.
    The tests accept either {"error": "msg"} or {"error": {"message": "..."}}
    We choose the latter for richer structure.
    """
    payload = {"error": {"code": str(code), "message": message}}
    return jsonify(payload), code


def _validate_device_create(payload: Dict[str, Any]) -> List[str]:
    """
    Validate the payload for creating a device.
    Required: name, ip_address, type, location
    type must be one of Router|Switch|Server
    """
    errors: List[str] = []
    required = ["name", "ip_address", "type", "location"]
    for field in required:
        if field not in payload or payload.get(field) in (None, ""):
            errors.append(f"Missing required field: {field}")

    allowed_types = {"Router", "Switch", "Server"}
    if "type" in payload and payload.get("type") not in allowed_types:
        errors.append("Field 'type' must be one of: Router, Switch, Server")
    return errors


def _validate_device_update(payload: Dict[str, Any]) -> List[str]:
    """
    Validate the payload for updating a device.
    Required: ip_address, type, location
    """
    errors: List[str] = []
    required = ["ip_address", "type", "location"]
    for field in required:
        if field not in payload or payload.get(field) in (None, ""):
            errors.append(f"Missing required field: {field}")

    allowed_types = {"Router", "Switch", "Server"}
    if "type" in payload and payload.get("type") not in allowed_types:
        errors.append("Field 'type' must be one of: Router, Switch, Server")
    return errors


# PUBLIC_INTERFACE
@blp_devices.route("/")
class DevicesList(MethodView):
    """
    List and create devices.

    GET /devices
      - Returns list of all devices.
      - 200: [Device]
      - 500: error response

    POST /devices
      - Creates a new device; enforces unique 'name'.
      - 201: created Device
      - 400: validation error
      - 409: conflict if device with same name exists
      - 500: error response
    """

    @blp_devices.response(200, description="A list of devices")
    @blp_devices.doc(summary="List all devices", description="Return all devices in the inventory")
    def get(self):
        try:
            coll = _get_collection()
            devices = list(coll.find())
            # Convert Mongo documents to plain JSON-friendly dicts (remove _id)
            normalized = []
            for d in devices:
                d.pop("_id", None)
                normalized.append(d)
            return jsonify(normalized), 200
        except Exception as exc:  # pragma: no cover - covered via tests as 500
            return _error(500, f"Internal server error: {str(exc)}")

    @blp_devices.response(201, description="Device created successfully")
    @blp_devices.doc(summary="Add a new device", description="Create a new device with unique name")
    def post(self):
        try:
            payload = request.get_json(silent=True) or {}
            errors = _validate_device_create(payload)
            if errors:
                return _error(400, "; ".join(errors))

            coll = _get_collection()
            existing = coll.find_one({"name": payload["name"]})
            if existing:
                return _error(409, "Device name already exists")

            # Insert and echo back the created device (without Mongo _id)
            coll.insert_one({
                "name": payload["name"],
                "ip_address": payload["ip_address"],
                "type": payload["type"],
                "location": payload["location"],
            })
            created = {
                "name": payload["name"],
                "ip_address": payload["ip_address"],
                "type": payload["type"],
                "location": payload["location"],
            }
            return jsonify(created), 201
        except Exception as exc:  # pragma: no cover
            return _error(500, f"Internal server error: {str(exc)}")


# PUBLIC_INTERFACE
@blp_devices.route("/<string:name>")
class DeviceDetail(MethodView):
    """
    Retrieve, update, and delete a device by name.

    GET /devices/{name}
      - 200: Device
      - 404: Not found
      - 500: Error

    PUT /devices/{name}
      - 200: Updated Device
      - 400: Validation error
      - 404: Not found
      - 500: Error

    DELETE /devices/{name}
      - 204: Deleted successfully (or 200 in some variants)
      - 404: Not found
      - 500: Error
    """

    @blp_devices.response(200, description="Device details")
    @blp_devices.doc(summary="Retrieve device details by name")
    def get(self, name: str):
        try:
            coll = _get_collection()
            doc = coll.find_one({"name": name})
            if not doc:
                return _error(404, "Device not found")
            doc.pop("_id", None)
            return jsonify(doc), 200
        except Exception as exc:  # pragma: no cover
            return _error(500, f"Internal server error: {str(exc)}")

    @blp_devices.response(200, description="Device updated successfully")
    @blp_devices.doc(summary="Update device attributes (except name)")
    def put(self, name: str):
        try:
            payload = request.get_json(silent=True) or {}
            errors = _validate_device_update(payload)
            if errors:
                return _error(400, "; ".join(errors))

            coll = _get_collection()
            existing = coll.find_one({"name": name})
            if not existing:
                return _error(404, "Device not found")

            update_fields = {
                "ip_address": payload["ip_address"],
                "type": payload["type"],
                "location": payload["location"],
            }
            coll.update_one({"name": name}, {"$set": update_fields})
            updated = {
                "name": name,
                **update_fields,
            }
            return jsonify(updated), 200
        except Exception as exc:  # pragma: no cover
            return _error(500, f"Internal server error: {str(exc)}")

    @blp_devices.response(204, description="Device deleted successfully")
    @blp_devices.doc(summary="Remove a device")
    def delete(self, name: str):
        try:
            coll = _get_collection()
            existing = coll.find_one({"name": name})
            if not existing:
                return _error(404, "Device not found")
            res = coll.delete_one({"name": name})
            # Return 204 if a document was deleted, otherwise 404 already covered
            if getattr(res, "deleted_count", 0) > 0:
                return "", 204
            return _error(404, "Device not found")
        except Exception as exc:  # pragma: no cover
            return _error(500, f"Internal server error: {str(exc)}")
