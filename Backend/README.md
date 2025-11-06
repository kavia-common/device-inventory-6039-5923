# Backend - Device Inventory

This is the Flask backend for the Device Inventory project. It exposes RESTful endpoints and integrates with MongoDB via `pymongo`.

## Running the server (dev)

- Install dependencies:
  pip install -r requirements.txt

- Run:
  python run.py

The API docs (via flask-smorest) will be available at `/docs`.

## Configuration

The backend reads MongoDB configuration from environment variables. Sensible defaults are used for local development if not provided.

- MONGODB_URI (default: mongodb://localhost:27017)
- MONGODB_DB (default: device_inventory)
- MONGODB_COLLECTION (default: devices)

Do NOT commit real credentials. Use a .env file managed by the deployment/orchestrator.

## Testing

This backend uses `pytest` for automated tests. Tests are located under `Backend/tests/`.

- Run tests from the repository root with make:
  make -C device-inventory-6039-5923/Backend test

- Or from the Backend directory:
  pytest -q

Notes:
- Tests mock MongoDB/pymongo so no real database is used.
- The suite includes tests for `/devices` and `/devices/{name}`. Error responses are standardized as:
  {"error": {"code": "<status_code>", "message": "<description>"}}

## Make targets

- make test: Run tests in CI-friendly mode
- make test-verbose: Run verbose tests
- make lint: Run flake8 on the `app/` folder
