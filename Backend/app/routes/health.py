from flask_smorest import Blueprint
from flask.views import MethodView
from flask import jsonify
from pymongo import MongoClient
from pymongo.errors import PyMongoError
from ..config import load_mongo_settings
from ..errors import error_response

# Health check blueprint
blp = Blueprint(
    "Health",
    "health",
    url_prefix="/",
    description="Health endpoints for service and MongoDB connectivity",
)


@blp.route("/healthz")
class Healthz(MethodView):
    # PUBLIC_INTERFACE
    def get(self):
        """Connectivity health check for MongoDB.
        Returns:
            200 with {"status": "ok"} if the application can connect to MongoDB and access the configured collection.
            503 with standardized ErrorResponse JSON if connectivity fails or configuration is invalid.
        """
        try:
            settings = load_mongo_settings()
        except Exception as exc:
            # Config invalid or missing
            return error_response(503, "ServiceUnavailable", f"Configuration error: {exc}")

        client: MongoClient = None
        try:
            client = MongoClient(settings.uri, serverSelectionTimeoutMS=2000)
            db = client[settings.database]
            coll = db[settings.collection]
            # Use ping to validate server connection and a lightweight find_one to ensure collection access
            client.admin.command("ping")
            _ = coll.find_one({}, {"_id": 0})
            return jsonify({"status": "ok"}), 200
        except PyMongoError as exc:
            return error_response(503, "ServiceUnavailable", f"Database connectivity error: {exc}")
        except Exception as exc:
            return error_response(503, "ServiceUnavailable", f"Health check failed: {exc}")
        finally:
            if client is not None:
                try:
                    client.close()
                except Exception:
                    pass
