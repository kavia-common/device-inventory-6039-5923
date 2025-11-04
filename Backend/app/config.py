import json
import os
from dataclasses import dataclass


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


def _from_dict(cfg: dict) -> MongoSettings:
    """Extract MongoSettings from the given dict with validation."""
    mongodb = cfg.get("mongodb", {})
    uri = mongodb.get("uri")
    database = mongodb.get("database")
    collection = mongodb.get("collection")

    if uri is None or database is None or collection is None:
        raise ValueError("Config missing required fields under 'mongodb': uri, database, collection.")
    _validate_mongo_uri(uri)
    _validate_non_empty("Database name", database)
    _validate_non_empty("Collection name", collection)
    return MongoSettings(uri=uri, database=database, collection=collection)


# PUBLIC_INTERFACE
def load_mongo_settings() -> MongoSettings:
    """Load MongoDB settings from config file or environment variables.

    Resolution order:
    1. If CONFIG_PATH env var is set, try that file path first.
    2. Else try ./config.json at the project root (Backend working directory).
    3. If no config file found or it's invalid, fall back to environment variables:
       - MONGODB_URI
       - MONGODB_DB_NAME (preferred) or MONGODB_DB
       - MONGODB_COLLECTION_NAME (preferred) or MONGODB_COLLECTION
    Raises:
        ValueError: if neither a valid config file nor required environment variables are provided.
    """
    # Where we expect to run: this module sits in app/, default config is at Backend/config.json
    # Determine candidate path
    config_path = "./Backend/config.json"
    if config_path:
        if os.path.isfile(config_path):
            try:
                cfg = _load_json_file(config_path)
                return _from_dict(cfg)
            except Exception as exc:
                # If explicitly provided config path is invalid, fail fast to surface misconfiguration
                raise ValueError(f"Failed to load configuration from CONFIG_PATH='{config_path}': {exc}") from exc
        else:
            raise ValueError(f"CONFIG_PATH is set to '{config_path}' but file does not exist.")

    # Default path relative to current working directory (Backend root)
    default_path = os.path.join(os.getcwd(), "config.json")
    if os.path.isfile(default_path):
        try:
            cfg = _load_json_file(default_path)
            return _from_dict(cfg)
        except Exception:
            # If default config exists but invalid, fall back to env vars to preserve backward compatibility
            pass

    # Fall back to env vars
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
        "MongoDB settings not found. Provide a config.json at Backend/ or set CONFIG_PATH, "
        "or set environment variables MONGODB_URI, MONGODB_DB_NAME (or MONGODB_DB), "
        "and MONGODB_COLLECTION_NAME (or MONGODB_COLLECTION)."
    )
