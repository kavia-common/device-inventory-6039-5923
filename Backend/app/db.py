from typing import Tuple
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection
from .config import load_mongo_settings


# PUBLIC_INTERFACE
def get_mongo_collection() -> Tuple[MongoClient, Collection]:
    """Return a connected MongoClient and the configured collection.

    The configuration is resolved via app.config.load_mongo_settings(), which:
      - Loads from CONFIG_PATH JSON file, or ./config.json if present
      - Falls back to environment variables for backward compatibility
    """
    settings = load_mongo_settings()

    client = MongoClient(settings.uri)
    db = client[settings.database]
    collection = db[settings.collection]

    # Ensure unique index on name
    collection.create_index([("name", ASCENDING)], unique=True, name="uniq_name")

    return client, collection
