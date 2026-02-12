from unittest.mock import Mock

from fastapi.testclient import TestClient

from app.api.dependencies import get_client_service
from app.main import app


class DummyClient:
    def __init__(self, id=1, name="Alice", national_number="123456", accounts=None):
        self.id = id
        self.name = name
        self.national_number = national_number
        self.accounts = accounts if accounts is not None else []


class DummyAccount:
    def __init__(self, id=1, name="Savings", balance=100, type="savings", client_id=1):
        self.id = id
        self.name = name
        self.balance = balance
        self.type = type
        self.client_id = client_id


def _create_test_client(service_mock):
    """Create a FastAPI TestClient with a mocked ClientService."""
    app.dependency_overrides[get_client_service] = lambda: service_mock
    client = TestClient(app)
    yield client
    app.dependency_overrides.clear()


def _get_test_client(service_mock):
    app.dependency_overrides[get_client_service] = lambda: service_mock
    return TestClient(app)


def test_get_clients_endpoint_returns_200():
    service = Mock()
    service.get_all_clients.return_value = [
        DummyClient(id=1, name="Alice", national_number="111"),
        DummyClient(id=2, name="Bob", national_number="222"),
    ]
    client = _get_test_client(service)
    try:
        response = client.get("/api/v1/client")
        assert response.status_code == 200
        data = response.json()
        assert len(data) == 2
        assert data[0]["name"] == "Alice"
        assert data[1]["name"] == "Bob"
    finally:
        app.dependency_overrides.clear()


def test_get_client_by_id_endpoint_returns_200():
    service = Mock()
    service.get_client_by_id.return_value = DummyClient(
        id=1, name="Alice", national_number="111", accounts=[]
    )
    client = _get_test_client(service)
    try:
        response = client.get("/api/v1/client/1")
        assert response.status_code == 200
        data = response.json()
        assert data["id"] == 1
        assert data["name"] == "Alice"
        assert data["national_number"] == "111"
    finally:
        app.dependency_overrides.clear()


def test_get_client_by_id_endpoint_returns_404():
    service = Mock()
    service.get_client_by_id.return_value = None
    client = _get_test_client(service)
    try:
        response = client.get("/api/v1/client/999")
        assert response.status_code == 404
    finally:
        app.dependency_overrides.clear()


def test_get_client_by_id_includes_accounts():
    service = Mock()
    accounts = [
        DummyAccount(id=1, name="Savings", balance=100, type="savings", client_id=1),
        DummyAccount(id=2, name="Checking", balance=200, type="checking", client_id=1),
    ]
    service.get_client_by_id.return_value = DummyClient(
        id=1, name="Alice", national_number="111", accounts=accounts
    )
    client = _get_test_client(service)
    try:
        response = client.get("/api/v1/client/1")
        assert response.status_code == 200
        data = response.json()
        assert len(data["accounts"]) == 2
        assert data["accounts"][0]["name"] == "Savings"
        assert data["accounts"][1]["name"] == "Checking"
        assert data["accounts"][0]["client_id"] == 1
    finally:
        app.dependency_overrides.clear()
