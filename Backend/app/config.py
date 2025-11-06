import json
import os
from dataclasses import dataclass
from typing import Optional


@dataclass(frozen=True)
class MongoSettings:
    """Immutable settings for MongoDB connection."""
    uri: str
    database: str
    collection: str


def _validate_mongo_uri(uri: str) -> None:
    """Basic validation for Mongo URI to ensure it's non-empty and has a scheme."""
    if not isinstance(uri, str) or not uri.strip():
        raise ValueError("MongoDB URI must be a non-empty string.")
    # Basic scheme check; allow mongodb and mongodb+srv
    lowered = uri.lower()
    if not (lowered.startswith("mongodb://") or lowered.startswith("mongodb+srv://")):
        raise ValueError("MongoDB URI must start with 'mongodb://' or 'mongodb+srv://'")


def _validate_non_empty(name: str, value: str) -> None:
    if not isinstance(value, str) or not value.strip():
        raise ValueError(f"{name} must be a non-empty string.")


def _load_json_file(path: str) -> dict:
    """Load JSON from path and return dict. Raises ValueError on invalid JSON."""
    with open(path, "r", encoding="utf-8") as f:
        try:
            return json.load(f)
        except json.JSONDecodeError as exc:
            raise ValueError(f"Invalid JSON in config file '{path}': {exc}") from exc


def _from_dict(cfg: dict, fallback_env: bool = True) -> MongoSettings:
    """Extract MongoSettings from the given dict with validation.

    If fallback_env is True, any missing keys will be complemented from environment variables.
    """
    mongodb = cfg.get("mongodb", {}) if isinstance(cfg, dict) else {}
    uri = mongodb.get("uri")
    database = mongodb.get("database")
    collection = mongodb.get("collection")

    # Prefer explicit config values, gracefully fall back to env vars for missing keys
    if fallback_env:
        uri = uri or os.getenv("MONGODB_URI")
        database = database or os.getenv("MONGODB_DB_NAME") or os.getenv("MONGODB_DB")
        collection = collection or os.getenv("MONGODB_COLLECTION_NAME") or os.getenv("MONGODB_COLLECTION")

    if uri is None or database is None or collection is None:
        raise ValueError("Config missing required fields under 'mongodb': uri, database, collection.")

    _validate_mongo_uri(uri)
    _validate_non_empty("Database name", database)
    _validate_non_empty("Collection name", collection)
    return MongoSettings(uri=uri, database=database, collection=collection)


def _resolve_config_path() -> Optional[str]:
    """Determine which config file path to use.

    Precedence:
      1) CONFIG_PATH env var (explicit). If set, must point to a readable JSON file.
         If this file is missing or malformed, we fail fast with a clear error.
      2) Backend/config.json relative to the project root (recommended default).
         If present and valid, use it. If present but malformed, we fall back to env vars.
      3) ./config.json in current working directory (e.g., container workdir /app).
         If present and valid, use it. If present but malformed, we fall back to env vars.

    Returns:
        The resolved path if a candidate exists, otherwise None.
    """
    explicit = os.getenv("CONFIG_PATH")
    if explicit:
        return explicit

    # Try Backend/config.json relative to repository root or execution context.
    backend_default = os.path.join(os.getcwd(), "Backend", "config.json")
    if os.path.isfile(backend_default):
        return backend_default

    # Try config.json in current working directory (e.g., /app/config.json in Docker)
    cwd_default = os.path.join(os.getcwd(), "config.json")
    if os.path.isfile(cwd_default):
        return cwd_default

    return None


# PUBLIC_INTERFACE
def load_mongo_settings() -> MongoSettings:
    """Load MongoDB settings from a config file in Backend or from environment variables.

    Configuration sources and precedence:
    1) Explicit config file path via CONFIG_PATH environment variable. If set, the file must exist and be valid JSON
       using the format:
         {
           "mongodb": {
             "uri": "mongodb://... or mongodb+srv://...",
             "database": "device_inventory",
             "collection": "devices"
           }
         }
       If CONFIG_PATH is set but the file is missing or malformed, the function raises ValueError with a clear message.
    2) Backend/config.json (recommended default). If present and valid, these values are used.
       - Missing keys in the file are complemented from environment variables (graceful fallback).
       - If the file exists but is malformed, we fall back to environment variables for backward compatibility.
    3) ./config.json in the current working directory (e.g., /app/config.json in Docker). Same behavior as (2).
    4) Environment variables only (complete fallback) when no valid config file is found or chosen:
       - MONGODB_URI
       - MONGODB_DB_NAME (preferred) or MONGODB_DB
       - MONGODB_COLLECTION_NAME (preferred) or MONGODB_COLLECTION

    Notes:
    - Explicit CONFIG_PATH has strict behavior: if provided and invalid, we fail fast to surface misconfiguration.
    - For default config paths, we preserve backward compatibility by falling back to environment variables when the
      file is absent or malformed.
    - Explicit config values always take precedence over environment variables; env vars are only used to fill in
      missing keys.

    Returns:
        MongoSettings with validated uri, database, and collection.

    Raises:
        ValueError: If neither a valid configuration file nor the required environment variables are provided.
    """
    resolved_path = _resolve_config_path()

    # If explicit CONFIG_PATH is set, enforce strict behavior
    explicit_path = os.getenv("CONFIG_PATH")
    if explicit_path:
        if not os.path.isfile(explicit_path):
            raise ValueError(f"CONFIG_PATH is set to '{explicit_path}' but file does not exist.")
        try:
            cfg = _load_json_file(explicit_path)
            # Prefer file values; only fill missing keys from env
            return _from_dict(cfg, fallback_env=True)
        except Exception as exc:
            # Fail fast for explicit CONFIG_PATH per documentation
            raise ValueError(f"Failed to load configuration from CONFIG_PATH='{explicit_path}': {exc}") from exc

    # If we have a discovered default file (Backend/config.json or ./config.json), use it if valid.
    if resolved_path:
        try:
            cfg = _load_json_file(resolved_path)
            return _from_dict(cfg, fallback_env=True)
        except Exception:
            # For default config paths, fall back to pure env vars for backward compatibility
            pass

    # Fall back entirely to environment variables
    uri = os.getenv("MONGODB_URI")
    db = os.getenv("MONGODB_DB_NAME") or os.getenv("MONGODB_DB")
    coll = os.getenv("MONGODB_COLLECTION_NAME") or os.getenv("MONGODB_COLLECTION")

    if uri and db and coll:
        _validate_mongo_uri(uri)
        _validate_non_empty("Database name", db)
        _validate_non_empty("Collection name", coll)
        return MongoSettings(uri=uri, database=db, collection=coll)

    # Provide detailed guidance in the error
    raise ValueError(
        "MongoDB settings not found. Provide Backend/config.json, set CONFIG_PATH to a valid JSON config, "
        "or set environment variables MONGODB_URI, MONGODB_DB_NAME (or MONGODB_DB), and "
        "MONGODB_COLLECTION_NAME (or MONGODB_COLLECTION)."
    )
