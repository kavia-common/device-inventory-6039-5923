from flask_smorest import Blueprint
from flask.views import MethodView
from flask import request, jsonify
from pymongo.errors import DuplicateKeyError, PyMongoError

from ..db import get_mongo_collection
from ..schemas import DeviceCreateSchema, DeviceUpdateSchema
from ..errors import error_response

blp = Blueprint(
    "Devices",
    "devices",
    url_prefix="/devices",
    description="Operations related to network devices",
)


@blp.route("")
class DevicesCollection(MethodView):
    """Collection endpoints for /devices"""

    # PUBLIC_INTERFACE
    def get(self):
        """List all devices.
        Returns:
            200 with DeviceList (array of Device)
            500 on server error
        """
        try:
            client, collection = get_mongo_collection()
            try:
                devices = list(collection.find({}, {"_id": 0}))
                return jsonify(devices), 200
            finally:
                client.close()
        except PyMongoError as exc:
            return error_response(500, "InternalServerError", f"Database error: {exc}")
        except Exception as exc:
            return error_response(500, "InternalServerError", f"Unexpected error: {exc}")

    # PUBLIC_INTERFACE
    def post(self):
        """Create a new device.
        Request body: DeviceCreate
        Returns:
            201 with Device
            400 on validation error
            409 on conflict (duplicate name)
            500 on server error
        """
        json_data = request.get_json(silent=True)
        if json_data is None:
            return error_response(400, "BadRequest", "Request body must be valid JSON.")

        # Validate input
        errors = DeviceCreateSchema().validate(json_data)
        if errors:
            return error_response(400, "BadRequest", f"Validation error: {errors}")

        try:
            client, collection = get_mongo_collection()
            try:
                # Enforce unique name at app level too
                name = json_data.get("name")
                if collection.find_one({"name": name}):
                    return error_response(409, "Conflict", f"Device with name '{name}' already exists.")

                collection.insert_one(json_data)
                # Return created device without _id
                created = collection.find_one({"name": name}, {"_id": 0})
                return jsonify(created), 201
            except DuplicateKeyError:
                return error_response(409, "Conflict", f"Device with name '{json_data.get('name')}' already exists.")
            finally:
                client.close()
        except PyMongoError as exc:
            return error_response(500, "InternalServerError", f"Database error: {exc}")
        except Exception as exc:
            return error_response(500, "InternalServerError", f"Unexpected error: {exc}")


@blp.route("/<string:name>")
class DeviceItem(MethodView):
    """Item endpoints for /devices/{name}"""

    # PUBLIC_INTERFACE
    def get(self, name: str):
        """Get a device by name.
        Path params:
            name: Unique device name
        Returns:
            200 with Device
            404 if not found
            500 on server error
        """
        try:
            client, collection = get_mongo_collection()
            try:
                doc = collection.find_one({"name": name}, {"_id": 0})
                if not doc:
                    return error_response(404, "NotFound", f"Device '{name}' not found.")
                return jsonify(doc), 200
            finally:
                client.close()
        except PyMongoError as exc:
            return error_response(500, "InternalServerError", f"Database error: {exc}")
        except Exception as exc:
            return error_response(500, "InternalServerError", f"Unexpected error: {exc}")

    # PUBLIC_INTERFACE
    def put(self, name: str):
        """Update a device by name.
        Request body: DeviceUpdate
        Returns:
            200 with Device
            400 on validation error
            404 if not found
            500 on server error
        """
        json_data = request.get_json(silent=True)
        if json_data is None:
            return error_response(400, "BadRequest", "Request body must be valid JSON.")

        errors = DeviceUpdateSchema().validate(json_data)
        if errors:
            return error_response(400, "BadRequest", f"Validation error: {errors}")

        try:
            client, collection = get_mongo_collection()
            try:
                result = collection.update_one({"name": name}, {"$set": json_data})
                if result.matched_count == 0:
                    return error_response(404, "NotFound", f"Device '{name}' not found.")

                updated = collection.find_one({"name": name}, {"_id": 0})
                return jsonify(updated), 200
            finally:
                client.close()
        except PyMongoError as exc:
            return error_response(500, "InternalServerError", f"Database error: {exc}")
        except Exception as exc:
            return error_response(500, "InternalServerError", f"Unexpected error: {exc}")

    # PUBLIC_INTERFACE
    def delete(self, name: str):
        """Delete a device by name.
        Returns:
            200 with {message}
            404 if not found
            500 on server error
        """
        try:
            client, collection = get_mongo_collection()
            try:
                result = collection.delete_one({"name": name})
                if result.deleted_count == 0:
                    return error_response(404, "NotFound", f"Device '{name}' not found.")
                return jsonify({"message": f"Device '{name}' deleted successfully."}), 200
            finally:
                client.close()
        except PyMongoError as exc:
            return error_response(500, "InternalServerError", f"Database error: {exc}")
        except Exception as exc:
            return error_response(500, "InternalServerError", f"Unexpected error: {exc}")
