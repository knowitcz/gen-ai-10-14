import logging
from datetime import datetime

from sqlmodel import Session, case, col, func, or_, select

from app.models.transaction import Transaction

logger = logging.getLogger(__name__)


class TransactionRepository:
    """
    Repository class for performing operations on Transaction objects in the database.
    """

    def __init__(self, session: Session):
        """
        Initialize the TransactionRepository with a database session.

        :param session: SQLModel Session object for database operations.
        """
        self.session = session

    def create(self, transaction: Transaction) -> Transaction:
        """
        Persist a new transaction record.

        :param transaction: The Transaction object to persist.
        :return: The persisted Transaction object.
        """
        logger.debug(
            "Creating transaction: amount=%s, source=%s, target=%s",
            transaction.amount,
            transaction.source_account_id,
            transaction.target_account_id,
        )
        self.session.add(transaction)
        return transaction

    def find_transactions(
        self,
        account_ids: list[int],
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> list[Transaction]:
        """
        Find transactions involving any of the given account IDs, with optional date filters.

        :param account_ids: List of account IDs to filter by.
        :param from_date: Optional start date filter (inclusive).
        :param to_date: Optional end date filter (inclusive).
        :return: List of matching Transaction objects.
        """
        logger.debug(
            "Finding transactions for accounts %s, from=%s, to=%s",
            account_ids,
            from_date,
            to_date,
        )
        statement = select(Transaction).where(
            or_(
                col(Transaction.source_account_id).in_(account_ids),
                col(Transaction.target_account_id).in_(account_ids),
            )
        )

        if from_date is not None:
            statement = statement.where(Transaction.date >= from_date)
        if to_date is not None:
            statement = statement.where(Transaction.date <= to_date)

        statement = statement.order_by(Transaction.date.desc())  # type: ignore[union-attr]

        transactions = self.session.exec(statement).all()
        logger.debug("Found %d transactions", len(transactions))
        return list(transactions)

    def get_summary(
        self,
        account_ids: list[int],
        from_date: datetime | None = None,
        to_date: datetime | None = None,
    ) -> dict[str, int]:
        """
        Compute aggregate summary (total_incoming, total_outgoing) for the given accounts.

        :param account_ids: List of account IDs to filter by.
        :param from_date: Optional start date filter (inclusive).
        :param to_date: Optional end date filter (inclusive).
        :return: Dict with 'total_incoming' and 'total_outgoing' keys.
        """
        logger.debug(
            "Computing summary for accounts %s, from=%s, to=%s",
            account_ids,
            from_date,
            to_date,
        )

        total_incoming = func.coalesce(
            func.sum(
                case(
                    (
                        col(Transaction.source_account_id).is_(None),
                        Transaction.amount,
                    ),
                    else_=0,
                )
            ),
            0,
        )
        total_outgoing = func.coalesce(
            func.sum(
                case(
                    (
                        col(Transaction.target_account_id).is_(None),
                        Transaction.amount,
                    ),
                    else_=0,
                )
            ),
            0,
        )

        statement = select(total_incoming, total_outgoing).where(
            or_(
                col(Transaction.source_account_id).in_(account_ids),
                col(Transaction.target_account_id).in_(account_ids),
            )
        )

        if from_date is not None:
            statement = statement.where(Transaction.date >= from_date)
        if to_date is not None:
            statement = statement.where(Transaction.date <= to_date)

        logger.info("Executing query: %s", str(statement))

        result = self.session.exec(statement).one()
        summary = {
            "total_incoming": result[0],
            "total_outgoing": result[1],
        }
        logger.debug("Summary: %s", summary)
        return summary
