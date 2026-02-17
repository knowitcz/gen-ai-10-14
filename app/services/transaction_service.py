import logging
from datetime import datetime

from app.repository.account_repository import AccountRepository
from app.repository.transaction_repository import TransactionRepository

logger = logging.getLogger(__name__)


class TransactionService:
    """
    Service for retrieving transaction history and summaries for a client.
    """

    def __init__(
        self,
        account_repository: AccountRepository,
        transaction_repository: TransactionRepository,
    ):
        self.account_repository = account_repository
        self.transaction_repository = transaction_repository

    def get_client_transactions(
        self,
        client_id: int,
        from_date: datetime | None = None,
        to_date: datetime | None = None,
        account_id: int | None = None,
    ) -> dict:
        """
        Retrieve transaction history and summary for a client.

        :param client_id: The client whose transactions to retrieve.
        :param from_date: Optional start date filter.
        :param to_date: Optional end date filter.
        :param account_id: Optional filter by specific account ID.
        :return: Dict with 'summary' and 'transactions' keys.
        :raises ValueError: If the client has no accounts or the specified account is not found.
        """
        logger.info(
            "Fetching transactions for client %s (from=%s, to=%s, account=%s)",
            client_id,
            from_date,
            to_date,
            account_id,
        )
        try:
            accounts = self.account_repository.get_by_client_id(client_id)
            if not accounts:
                logger.warning("No accounts found for client %s", client_id)
                raise ValueError(f"No accounts found for client {client_id}")

            if account_id is not None:
                matching = [a for a in accounts if a.id == account_id]
                if not matching:
                    logger.warning(
                        "Account %s does not belong to client %s",
                        account_id,
                        client_id,
                    )
                    raise ValueError(
                        f"Account {account_id} does not belong to client {client_id}"
                    )
                account_ids = [account_id]
            else:
                account_ids = [a.id for a in accounts]

            logger.debug("Querying transactions for account IDs: %s", account_ids)

            # Both queries run inside the same DB transaction for consistency
            transactions = self.transaction_repository.find_transactions(
                account_ids, from_date, to_date
            )
            summary = self.transaction_repository.get_summary(
                account_ids, from_date, to_date
            )

            logger.info(
                "Retrieved %d transactions for client %s", len(transactions), client_id
            )
            return {
                "summary": summary,
                "transactions": transactions,
            }
        except Exception as e:
            logger.error(
                "Failed to fetch transactions for client %s: %s",
                client_id,
                e,
                exc_info=True,
            )
            raise
