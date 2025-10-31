# Device Management REST API (Flask + MongoDB)

A Flask backend exposing CRUD APIs for managing network devices with MongoDB storage.

## Environment Variables

Set the following environment variables (see .env.example in your deployment):

- MONGODB_URI: MongoDB connection string (e.g., mongodb://localhost:27017)
- MONGODB_DB: Database name (e.g., device_inventory)
- MONGODB_COLLECTION: Collection name (e.g., devices)
- PORT: Port for Flask app to listen on (default: 5000)

## Running Locally

1. Create and activate a virtual environment.
2. Install dependencies:
   pip install -r requirements.txt
3. Ensure MongoDB is accessible with your configured env vars.
4. Start the server:
   python run.py

The API will be available at http://localhost:${PORT:-5000} and docs at /docs.

## Docker

Build and run:

- docker build -t device-api .
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
