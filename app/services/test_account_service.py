from unittest.mock import MagicMock, Mock

from app.services.account_service import AccountService


class DummyAccount:
    pass

def test_get_account_by_id_returns_account():
    repo = Mock()
    account = DummyAccount()
    repo.get_by_id.return_value = account
    service = AccountService(repo)
    result = service.get_account_by_id(1)
    assert result is account
    repo.get_by_id.assert_called_once_with(1)

def test_transfer_money_calls_withdraw_and_deposit():
    repo = Mock()
    repo.session = MagicMock()
    repo.session.begin.return_value.__enter__.return_value = None
    repo.withdraw_money = Mock()
    repo.deposit_money = Mock()
    service = AccountService(repo)
    service.transfer_money(1, 2, 100)
    repo.withdraw_money.assert_called_once_with(1, 100)
    repo.deposit_money.assert_called_once_with(2, 100)


def test_withdraw_money_calls_repo():
    repo = Mock()
    repo.session = MagicMock()
    repo.session.begin.return_value.__enter__.return_value = None
    repo.withdraw_money = Mock()
    service = AccountService(repo)
    service.withdraw_money(1, 50)
    repo.withdraw_money.assert_called_once_with(1, 50)


def test_deposit_money_calls_repo():
    repo = Mock()
    repo.session = MagicMock()
    repo.session.begin.return_value.__enter__.return_value = None
    repo.deposit_money = Mock()
    service = AccountService(repo)
    service.deposit_money(1, 75)
    repo.deposit_money.assert_called_once_with(1, 75)
