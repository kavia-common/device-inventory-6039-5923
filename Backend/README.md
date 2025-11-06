# Backend - Device Inventory

This is the Flask backend for the Device Inventory project. It exposes RESTful endpoints and integrates with MongoDB via `pymongo` (to be implemented).

## Running the server (dev)

- Install dependencies:
  pip install -r requirements.txt

- Run:
  python run.py

The API docs (via flask-smorest) will be available at `/docs`.

## Testing

This backend uses `pytest` for automated tests. Tests are located under `Backend/tests/`.

- Run tests from the repository root with make:
  make -C device-inventory-6039-5923/Backend test

- Or from the Backend directory:
  pytest -q

Notes:
- Tests mock MongoDB/pymongo so no real database is used.
- The current source only includes a health check route ("/"). The test suite includes comprehensive tests for `/devices` and `/devices/{name}` as defined in the work item, and they are marked with `xfail` until those endpoints are implemented. This ensures the test run does not fail CI prematurely.

## Make targets

- make test: Run tests in CI-friendly mode
- make test-verbose: Run verbose tests
- make lint: Run flake8 on the `app/` folder
