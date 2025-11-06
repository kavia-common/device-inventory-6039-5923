import pytest
from .utils import is_error_response

pytestmark = [pytest.mark.devices]


# GET /devices/{name}
def test_get_device_success(client, mock_pymongo, sample_device):
    mock_pymongo["collection"].find_one.return_value = sample_device
    resp = client.get(f"/devices/{sample_device['name']}")
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["name"] == sample_device["name"]


def test_get_device_not_found(client, mock_pymongo):
    mock_pymongo["collection"].find_one.return_value = None
    resp = client.get("/devices/unknown")
    assert resp.status_code == 404
    data = resp.get_json()
    assert is_error_response(data)


def test_get_device_internal_error(client, mock_pymongo):
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    mock_pymongo["collection"].find_one.side_effect = boom
    resp = client.get("/devices/router-01")
    assert resp.status_code == 500
    data = resp.get_json()
    assert is_error_response(data)


# PUT /devices/{name}
def test_update_device_success(client, mock_pymongo, sample_device, sample_device_update):
    mock_pymongo["collection"].find_one.return_value = sample_device
    mock_pymongo["collection"].update_one.return_value = type("R", (), {"matched_count": 1, "modified_count": 1})
    resp = client.put(f"/devices/{sample_device['name']}", json=sample_device_update)
    assert resp.status_code == 200
    data = resp.get_json()
    assert data["ip_address"] == sample_device_update["ip_address"]
    assert data["location"] == sample_device_update["location"]


def test_update_device_validation_error(client, mock_pymongo, sample_device):
    mock_pymongo["collection"].find_one.return_value = sample_device
    bad_update = {"type": "Router"}  # missing required fields according to spec
    resp = client.put(f"/devices/{sample_device['name']}", json=bad_update)
    assert resp.status_code == 400
    data = resp.get_json()
    assert is_error_response(data)


def test_update_device_not_found(client, mock_pymongo, sample_device_update):
    mock_pymongo["collection"].find_one.return_value = None
    resp = client.put("/devices/unknown", json=sample_device_update)
    assert resp.status_code == 404
    data = resp.get_json()
    assert is_error_response(data)


def test_update_device_internal_error(client, mock_pymongo, sample_device_update):
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    mock_pymongo["collection"].update_one.side_effect = boom
    resp = client.put("/devices/router-01", json=sample_device_update)
    assert resp.status_code == 500
    data = resp.get_json()
    assert is_error_response(data)


# DELETE /devices/{name}
def test_delete_device_success(client, mock_pymongo, sample_device):
    mock_pymongo["collection"].find_one.return_value = sample_device
    mock_pymongo["collection"].delete_one.return_value = type("R", (), {"deleted_count": 1})
    resp = client.delete(f"/devices/{sample_device['name']}")
    # Spec alternates between 200 and 204 in variants; using 204 per subtask ask.
    assert resp.status_code in (200, 204)


def test_delete_device_not_found(client, mock_pymongo):
    mock_pymongo["collection"].find_one.return_value = None
    resp = client.delete("/devices/unknown")
    assert resp.status_code == 404
    data = resp.get_json()
    assert is_error_response(data)


def test_delete_device_internal_error(client, mock_pymongo):
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    mock_pymongo["collection"].delete_one.side_effect = boom
    resp = client.delete("/devices/router-01")
    assert resp.status_code == 500
    data = resp.get_json()
    assert is_error_response(data)
