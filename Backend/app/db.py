import os
from typing import Tuple
from pymongo import MongoClient, ASCENDING
from pymongo.collection import Collection


# PUBLIC_INTERFACE
def get_mongo_collection() -> Tuple[MongoClient, Collection]:
    """Return a connected MongoClient and the configured collection.

    Environment variables:
    - MONGODB_URI: MongoDB connection URI (e.g., mongodb://user:pass@host:27017)
    - MONGODB_DB: Database name
    - MONGODB_COLLECTION: Collection name
    """
    mongo_uri = os.getenv("MONGODB_URI", "mongodb://localhost:27017")
    db_name = os.getenv("MONGODB_DB", "device_inventory")
    coll_name = os.getenv("MONGODB_COLLECTION", "devices")

    client = MongoClient(mongo_uri)
    db = client[db_name]
    collection = db[coll_name]

    # Ensure unique index on name
    collection.create_index([("name", ASCENDING)], unique=True, name="uniq_name")

    return client, collection
