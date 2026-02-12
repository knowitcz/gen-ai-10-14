from app.models.account import Account
from app.models.client import Client


def test_client_has_required_fields():
    client = Client(id=1, name="Alice", national_number="123456")
    assert client.id == 1
    assert client.name == "Alice"
    assert client.national_number == "123456"


def test_account_has_client_id_field():
    account = Account(id=1, name="Savings", balance=100, type="savings", client_id=1)
    assert account.client_id == 1
