import os
import types
import pytest
from unittest.mock import MagicMock, patch

# Ensure the Flask app can be imported
os.environ.setdefault("FLASK_ENV", "testing")


@pytest.fixture(scope="session")
def flask_app():
    """
    Create and configure a Flask app instance for testing.
    Imports the app from app.__init__.py.
    """
    from app import app as flask_app_instance
    # Use testing mode for better error propagation
    flask_app_instance.config.update(
        TESTING=True
    )
    return flask_app_instance


@pytest.fixture()
def client(flask_app):
    """
    Flask test client fixture.
    """
    return flask_app.test_client()


@pytest.fixture()
def sample_device():
    return {
        "name": "router-01",
        "ip_address": "192.168.1.1",
        "type": "Router",
        "location": "Data Center A",
    }


@pytest.fixture()
def sample_device_update():
    return {
        "ip_address": "192.168.1.2",
        "type": "Router",
        "location": "Data Center B",
    }


@pytest.fixture()
def mock_pymongo():
    """
    Mock pymongo to avoid any real database interaction.
    This returns a structure resembling client[db][collection].
    """
    # Create nested MagicMocks to emulate pymongo usage
    mock_collection = MagicMock()
    mock_db = MagicMock()
    mock_client = MagicMock()

    # db and collection access patterns
    mock_db.__getitem__.return_value = mock_collection
    mock_client.__getitem__.return_value = mock_db

    # Example default behaviors (can be overridden in individual tests)
    mock_collection.find.return_value = []
    mock_collection.insert_one.return_value = types.SimpleNamespace(inserted_id="fakeid")
    mock_collection.find_one.return_value = None
    mock_collection.update_one.return_value = types.SimpleNamespace(matched_count=0, modified_count=0)
    mock_collection.delete_one.return_value = types.SimpleNamespace(deleted_count=0)

    # Patch points: typical import paths
    patches = [
        patch("pymongo.MongoClient", return_value=mock_client),
        patch("app.routes", create=True),  # in case code accesses app.routes level modules
    ]

    started_patches = [p.start() for p in patches]

    yield {
        "client": mock_client,
        "db": mock_db,
        "collection": mock_collection,
        "patches": started_patches,
    }

    for p in patches:
        p.stop()
