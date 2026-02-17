from datetime import datetime, timezone
from unittest.mock import Mock

from app.models.transaction import Transaction
from app.repository.transaction_repository import TransactionRepository


def test_create_adds_transaction_to_session():
    session = Mock()
    repo = TransactionRepository(session)
    tx = Transaction(
        source_account_id=None,
        target_account_id=1,
        amount=100,
    )
    result = repo.create(tx)
    session.add.assert_called_once_with(tx)
    assert result is tx


def test_find_transactions_returns_list():
    session = Mock()
    tx1 = Transaction(id=1, target_account_id=1, amount=50)
    tx2 = Transaction(id=2, source_account_id=1, amount=30)
    session.exec.return_value.all.return_value = [tx1, tx2]
    repo = TransactionRepository(session)

    result = repo.find_transactions([1])
    assert len(result) == 2
    session.exec.assert_called_once()


def test_find_transactions_with_date_filters():
    session = Mock()
    session.exec.return_value.all.return_value = []
    repo = TransactionRepository(session)

    from_date = datetime(2025, 1, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 12, 31, tzinfo=timezone.utc)
    result = repo.find_transactions([1, 2], from_date=from_date, to_date=to_date)
    assert result == []
    session.exec.assert_called_once()


def test_get_summary_returns_totals():
    session = Mock()
    session.exec.return_value.one.return_value = (500, 200)
    repo = TransactionRepository(session)

    summary = repo.get_summary([1, 2])
    assert summary == {"total_incoming": 500, "total_outgoing": 200}
    session.exec.assert_called_once()


def test_get_summary_with_date_filters():
    session = Mock()
    session.exec.return_value.one.return_value = (100, 50)
    repo = TransactionRepository(session)

    from_date = datetime(2025, 6, 1, tzinfo=timezone.utc)
    to_date = datetime(2025, 6, 30, tzinfo=timezone.utc)
    summary = repo.get_summary([1], from_date=from_date, to_date=to_date)
    assert summary == {"total_incoming": 100, "total_outgoing": 50}
