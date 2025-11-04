Configuration Guide

This backend reads MongoDB connection settings from a JSON config file by default and falls back to environment variables for backward compatibility.

1) Config file (recommended)

- Default location: Backend/config.json
- Override via env var: set CONFIG_PATH to a path pointing to the JSON file

Sample config (see Backend/config.example.json):
{
  "mongodb": {
    "uri": "mongodb://localhost:27017",
    "database": "device_inventory",
    "collection": "devices"
  }
}

Validation:
- mongodb.uri must start with mongodb:// or mongodb+srv://
- mongodb.database and mongodb.collection must be non-empty strings

Usage examples:
- Local run:
  cp Backend/config.example.json Backend/config.json
  # edit Backend/config.json as needed
  python run.py

- Docker bind mount:
  docker run -v $(pwd)/Backend/config.json:/app/config.json -p 5000:5000 device-api

- Custom location using CONFIG_PATH:
  CONFIG_PATH=/some/path/custom.json python run.py

2) Environment variables (fallback)

If no valid config file is present, the service will read:
- MONGODB_URI
- MONGODB_DB_NAME or MONGODB_DB
- MONGODB_COLLECTION_NAME or MONGODB_COLLECTION

PORT can still be used to set the HTTP port (default: 5000).

Error behavior:
- If CONFIG_PATH is set but invalid or the file is missing/invalid, the application fails fast with a clear error.
- If the default config.json exists but is invalid, the app falls back to env vars to preserve backward compatibility. If env vars are also missing, startup fails with an explanatory error.
