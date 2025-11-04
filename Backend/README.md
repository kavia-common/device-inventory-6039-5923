# Device Management REST API (Flask + MongoDB)

A Flask backend exposing CRUD APIs for managing network devices with MongoDB storage.

## Configuration

This service supports configuration via a JSON file (recommended) with automatic fallback to environment variables for backward compatibility.

Preferred: create a config.json file (or set CONFIG_PATH to point to it) with:
{
  "mongodb": {
    "uri": "mongodb://localhost:27017",
    "database": "device_inventory",
    "collection": "devices"
  }
}

- Default path: Backend/config.json
- Override path: set environment variable CONFIG_PATH to an absolute or relative path to your config JSON.

Sample file is provided at Backend/config.example.json. Copy it to config.json and adjust values:
cp Backend/config.example.json Backend/config.json

Fallback environment variables (used when config file is not present or CONFIG_PATH is not set):
- MONGODB_URI: MongoDB connection string (e.g., mongodb://localhost:27017)
- MONGODB_DB_NAME or MONGODB_DB: Database name (e.g., device_inventory)
- MONGODB_COLLECTION_NAME or MONGODB_COLLECTION: Collection name (e.g., devices)
- PORT: Port for Flask app to listen on (default: 5000)

Validation:
- URI must start with mongodb:// or mongodb+srv://
- Database and collection must be non-empty strings

## Running Locally

1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Configure MongoDB settings:
   - Either create Backend/config.json (recommended), or
   - Set the fallback environment variables listed above.
4. Ensure MongoDB is accessible with your configured settings.
5. Start the server:
   python run.py

The API will be available at http://localhost:${PORT:-5000} and docs at /docs.

## Docker

Build and run:

- docker build -t device-api .
- Using config file:
  - docker run -v $(pwd)/Backend/config.json:/app/config.json -p 5000:5000 device-api
- Or using env vars (backward compatible):
  - docker run -e MONGODB_URI="mongodb://host.docker.internal:27017" -e MONGODB_DB="device_inventory" -e MONGODB_COLLECTION="devices" -p 5000:5000 device-api

## API Overview

- GET /devices: List all devices
- POST /devices: Create a device (body: {name, ip_address, type, location})
- GET /devices/{name}: Get a device by name
- PUT /devices/{name}: Update a device's ip_address, type, and location
- DELETE /devices/{name}: Delete a device by name

Standardized error responses:
{
  "error": {
    "code": "BadRequest|NotFound|Conflict|InternalServerError",
    "message": "Description"
  }
}

## Validation Rules

- ip_address must be a valid IPv4 address
- type must be one of: Router, Switch, Server
- name must be unique (enforced by unique index and application checks)
- location is a non-empty string

## OpenAPI

See interfaces/device_api.openapi.json for the API specification.
