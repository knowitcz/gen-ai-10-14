from datetime import datetime, timezone
from unittest.mock import Mock

import pytest

from app.services.transaction_service import TransactionService


class DummyAccount:
    def __init__(self, id=1, client_id=1):
        self.id = id
        self.client_id = client_id


def _make_service(accounts=None, transactions=None, summary=None):
    account_repo = Mock()
    tx_repo = Mock()
    account_repo.get_by_client_id.return_value = accounts or []
    tx_repo.find_transactions.return_value = transactions or []
    tx_repo.get_summary.return_value = summary or {"total_incoming": 0, "total_outgoing": 0}
    return TransactionService(account_repo, tx_repo), account_repo, tx_repo


def test_get_client_transactions_returns_summary_and_list():
    accounts = [DummyAccount(id=1), DummyAccount(id=2)]
    tx_list = [Mock(id=1), Mock(id=2)]
    summary = {"total_incoming": 300, "total_outgoing": 100}
    service, account_repo, tx_repo = _make_service(accounts, tx_list, summary)

    result = service.get_client_transactions(client_id=1)

    account_repo.get_by_client_id.assert_called_once_with(1)
    tx_repo.find_transactions.assert_called_once_with([1, 2], None, None)
    tx_repo.get_summary.assert_called_once_with([1, 2], None, None)
    assert result["summary"] == summary
    assert result["transactions"] == tx_list


def test_get_client_transactions_with_date_filters():
    accounts = [DummyAccount(id=5)]
    service, _, tx_repo = _make_service(accounts)

    from_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 12, 31, tzinfo=timezone.utc)
    service.get_client_transactions(client_id=1, from_date=from_date, to_date=to_date)

    tx_repo.find_transactions.assert_called_once_with([5], from_date, to_date)
    tx_repo.get_summary.assert_called_once_with([5], from_date, to_date)


def test_get_client_transactions_filter_by_account_id():
    accounts = [DummyAccount(id=10), DummyAccount(id=20)]
    service, _, tx_repo = _make_service(accounts)

    service.get_client_transactions(client_id=1, account_id=20)

    tx_repo.find_transactions.assert_called_once_with([20], None, None)
    tx_repo.get_summary.assert_called_once_with([20], None, None)


def test_get_client_transactions_raises_if_no_accounts():
    service, _, _ = _make_service(accounts=[])

    with pytest.raises(ValueError, match="No accounts found"):
        service.get_client_transactions(client_id=99)


def test_get_client_transactions_raises_if_account_not_owned():
    accounts = [DummyAccount(id=1)]
    service, _, _ = _make_service(accounts)

    with pytest.raises(ValueError, match="does not belong to client"):
        service.get_client_transactions(client_id=1, account_id=999)
