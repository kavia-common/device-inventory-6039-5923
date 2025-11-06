import pytest
from .utils import is_error_response

pytestmark = [pytest.mark.devices, pytest.mark.xfail_devices_missing]


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_create_device_success(client, mock_pymongo, sample_device):
    mock_pymongo["collection"].find_one.return_value = None  # no existing
    resp = client.post("/devices", json=sample_device)

    assert resp.status_code == 201
    data = resp.get_json()
    # Echo created device
    assert data["name"] == sample_device["name"]
    assert data["ip_address"] == sample_device["ip_address"]
    assert data["type"] == sample_device["type"]
    assert data["location"] == sample_device["location"]


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_create_device_validation_error(client, mock_pymongo, sample_device):
    bad = dict(sample_device)
    bad.pop("ip_address")  # missing required
    resp = client.post("/devices", json=bad)

    assert resp.status_code == 400
    data = resp.get_json()
    assert is_error_response(data)


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_create_device_conflict(client, mock_pymongo, sample_device):
    # pretend a device with same name exists
    mock_pymongo["collection"].find_one.return_value = sample_device

    resp = client.post("/devices", json=sample_device)

    assert resp.status_code == 409
    data = resp.get_json()
    assert is_error_response(data)


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_create_device_internal_error(client, mock_pymongo, sample_device, monkeypatch):
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    mock_pymongo["collection"].insert_one.side_effect = boom

    resp = client.post("/devices", json=sample_device)

    assert resp.status_code == 500
    data = resp.get_json()
    assert is_error_response(data)
