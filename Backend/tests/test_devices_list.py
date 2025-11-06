import pytest
from .utils import is_error_response

pytestmark = [pytest.mark.devices, pytest.mark.xfail_devices_missing]


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_list_devices_success(client, mock_pymongo):
    # Arrange mock DB returns two devices
    mock_pymongo["collection"].find.return_value = [
        {
            "name": "router-01",
            "ip_address": "192.168.1.1",
            "type": "Router",
            "location": "DC-A",
        },
        {
            "name": "switch-01",
            "ip_address": "10.0.0.5",
            "type": "Switch",
            "location": "DC-B",
        },
    ]

    # Act
    resp = client.get("/devices")

    # Assert
    assert resp.status_code == 200
    data = resp.get_json()
    assert isinstance(data, list)
    assert len(data) == 2
    assert all(
        {"name", "ip_address", "type", "location"}.issubset(d.keys()) for d in data
    )


@pytest.mark.xfail(reason="Endpoint /devices not implemented yet", raises=AssertionError, strict=False)
def test_list_devices_internal_error(client, mock_pymongo, monkeypatch):
    # Force an unexpected error in find()
    def boom(*args, **kwargs):
        raise RuntimeError("unexpected")

    mock_pymongo["collection"].find.side_effect = boom

    resp = client.get("/devices")
    # Expect 500 with error payload
    assert resp.status_code == 500
    data = resp.get_json()
    assert is_error_response(data)
