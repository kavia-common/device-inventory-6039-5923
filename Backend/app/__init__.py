import os
from flask import Flask, jsonify
from flask_cors import CORS
from .routes.health import blp as health_blp
from .routes.devices import blp as devices_blp
from flask_smorest import Api
from .errors import error_response


app = Flask(__name__)
app.url_map.strict_slashes = False
CORS(app, resources={r"/*": {"origins": "*"}})

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
