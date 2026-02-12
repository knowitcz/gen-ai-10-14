from unittest.mock import Mock

from app.services.client_service import ClientService


class DummyClient:
    def __init__(self, id=1, name="Alice", national_number="123456", accounts=None):
        self.id = id
        self.name = name
        self.national_number = national_number
        self.accounts = accounts if accounts is not None else []


def test_get_all_clients_delegates_to_repository():
    repo = Mock()
    clients = [DummyClient(id=1), DummyClient(id=2)]
    repo.get_all.return_value = clients
    service = ClientService(repo)
    result = service.get_all_clients()
    assert result is clients
    repo.get_all.assert_called_once()


def test_get_all_clients_returns_empty_list():
    repo = Mock()
    repo.get_all.return_value = []
    service = ClientService(repo)
    result = service.get_all_clients()
    assert result == []
    repo.get_all.assert_called_once()


def test_get_client_by_id_returns_client():
    repo = Mock()
    client = DummyClient(id=1, name="Alice")
    repo.get_by_id.return_value = client
    service = ClientService(repo)
    result = service.get_client_by_id(1)
    assert result is client
    repo.get_by_id.assert_called_once_with(1)


def test_get_client_by_id_returns_none():
    repo = Mock()
    repo.get_by_id.return_value = None
    service = ClientService(repo)
    result = service.get_client_by_id(999)
    assert result is None
    repo.get_by_id.assert_called_once_with(999)
