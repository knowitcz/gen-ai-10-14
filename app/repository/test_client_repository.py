from unittest.mock import Mock

from app.repository.client_repository import ClientRepository


class DummyClient:
    def __init__(self, id=1, name="Alice", national_number="123456", accounts=None):
        self.id = id
        self.name = name
        self.national_number = national_number
        self.accounts = accounts if accounts is not None else []


class DummyAccount:
    def __init__(self, id=1, balance=100, client_id=1):
        self.id = id
        self.balance = balance
        self.client_id = client_id


def test_get_all_returns_empty_list():
    session = Mock()
    session.exec.return_value.all.return_value = []
    repo = ClientRepository(session)
    result = repo.get_all()
    assert result == []
    session.exec.assert_called()


def test_get_all_returns_all_clients():
    session = Mock()
    clients = [
        DummyClient(id=1, name="Alice"),
        DummyClient(id=2, name="Bob"),
    ]
    session.exec.return_value.all.return_value = clients
    repo = ClientRepository(session)
    result = repo.get_all()
    assert len(result) == 2
    assert result[0] is clients[0]
    assert result[1] is clients[1]


def test_get_by_id_returns_client():
    session = Mock()
    client = DummyClient(id=1, name="Alice")
    session.exec.return_value.first.return_value = client
    repo = ClientRepository(session)
    result = repo.get_by_id(1)
    assert result is client
    session.exec.assert_called()


def test_get_by_id_returns_none():
    session = Mock()
    session.exec.return_value.first.return_value = None
    repo = ClientRepository(session)
    result = repo.get_by_id(999)
    assert result is None


def test_get_by_id_includes_accounts():
    session = Mock()
    account1 = DummyAccount(id=1, balance=100, client_id=1)
    account2 = DummyAccount(id=2, balance=200, client_id=1)
    client = DummyClient(id=1, name="Alice", accounts=[account1, account2])
    session.exec.return_value.first.return_value = client
    repo = ClientRepository(session)
    result = repo.get_by_id(1)
    assert result is client
    assert len(result.accounts) == 2
    assert result.accounts[0] is account1
    assert result.accounts[1] is account2


def test_get_by_id_client_with_no_accounts():
    session = Mock()
    client = DummyClient(id=1, name="Alice", accounts=[])
    session.exec.return_value.first.return_value = client
    repo = ClientRepository(session)
    result = repo.get_by_id(1)
    assert result is client
    assert result.accounts == []
