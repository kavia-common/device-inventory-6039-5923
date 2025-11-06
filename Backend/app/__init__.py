import os
import logging
from flask import Flask, jsonify
from flask_cors import CORS
from .routes.health import blp as health_blp
from .routes.devices import blp as devices_blp
from flask_smorest import Api
from .errors import error_response

# Optional imports used for startup connectivity logging
from .config import load_mongo_settings
from pymongo import MongoClient
from pymongo.errors import PyMongoError

app = Flask(__name__)
app.url_map.strict_slashes = False

# Configure precise CORS: allow only the specified frontend origin and standard methods/headers.
# Note: Origin is specified without trailing slash, as sent in the Origin header.
CORS(
    app,
    resources={r"/*": {"origins": ["https://device-inventory.kavia.app"]}},
    methods=["GET", "POST", "PUT", "DELETE", "OPTIONS"],
    allow_headers=["Content-Type", "Authorization"],
)

# OpenAPI/Swagger configuration
app.config["API_TITLE"] = "Device Management REST API"
app.config["API_VERSION"] = "1.0.0"
app.config["OPENAPI_VERSION"] = "3.0.3"
app.config["OPENAPI_URL_PREFIX"] = "/docs"
app.config["OPENAPI_SWAGGER_UI_PATH"] = ""
app.config["OPENAPI_SWAGGER_UI_URL"] = "https://cdn.jsdelivr.net/npm/swagger-ui-dist/"

api = Api(app)

# Register blueprints
api.register_blueprint(health_blp)
api.register_blueprint(devices_blp)

# Optional startup validation: log Mongo connectivity status without failing startup (backward compatible)
try:
    settings = load_mongo_settings()
    client = MongoClient(settings.uri, serverSelectionTimeoutMS=1500)
    try:
        client.admin.command("ping")
        logging.getLogger(__name__).info(
            "Startup check: MongoDB connectivity OK (db=%s, collection=%s).",
            settings.database,
            settings.collection,
        )
    finally:
        try:
            client.close()
        except Exception:
            pass
except PyMongoError as exc:
    logging.getLogger(__name__).warning("Startup check: MongoDB connectivity error: %s", exc)
except Exception as exc:
    logging.getLogger(__name__).warning("Startup check: configuration not ready or invalid: %s", exc)

# Standardized error handlers (fallbacks)
@app.errorhandler(400)
def handle_400(e):
    return error_response(400, "BadRequest", "Invalid input.")

@app.errorhandler(404)
def handle_404(e):
    return error_response(404, "NotFound", "Resource not found.")

@app.errorhandler(409)
def handle_409(e):
    return error_response(409, "Conflict", "Resource conflict.")

@app.errorhandler(500)
def handle_500(e):
    return error_response(500, "InternalServerError", "Unexpected server error.")
