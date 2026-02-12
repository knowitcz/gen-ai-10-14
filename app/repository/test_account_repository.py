from unittest.mock import Mock

import pytest

from app.repository.account_repository import AccountRepository


class DummyAccount:
    def __init__(self, id=1, balance=100, client_id=1):
        self.id = id
        self.balance = balance
        self.client_id = client_id

def test_get_by_id_returns_account():
    session = Mock()
    account = DummyAccount()
    session.exec.return_value.first.return_value = account
    repo = AccountRepository(session)
    result = repo.get_by_id(1)
    assert result is account
    session.exec.assert_called()

def test_get_by_id_returns_none():
    session = Mock()
    session.exec.return_value.first.return_value = None
    repo = AccountRepository(session)
    result = repo.get_by_id(2)
    assert result is None

def test_withdraw_money_success():
    repo = AccountRepository(Mock())
    repo.get_by_id = Mock(return_value=DummyAccount(balance=200))
    repo.session = Mock()
    account = repo.get_by_id(1)
    repo.withdraw_money(1, 50)
    assert account.balance == 150
    repo.session.add.assert_called_once_with(account)

def test_withdraw_money_account_not_found():
    repo = AccountRepository(Mock())
    repo.get_by_id = Mock(return_value=None)
    with pytest.raises(ValueError, match="Account not found"):
        repo.withdraw_money(1, 10)

def test_withdraw_money_insufficient_balance():
    repo = AccountRepository(Mock())
    repo.get_by_id = Mock(return_value=DummyAccount(balance=20))
    with pytest.raises(ValueError, match="Insufficient balance"):
        repo.withdraw_money(1, 50)

def test_deposit_money_success():
    repo = AccountRepository(Mock())
    repo.get_by_id = Mock(return_value=DummyAccount(balance=100))
    repo.session = Mock()
    account = repo.get_by_id(1)
    repo.deposit_money(1, 30)
    assert account.balance == 130
    repo.session.add.assert_called_once_with(account)

def test_deposit_money_account_not_found():
    repo = AccountRepository(Mock())
    repo.get_by_id = Mock(return_value=None)
    with pytest.raises(ValueError, match="Account not found"):
        repo.deposit_money(1, 10)
