import logging

from app.models.account import Account
from app.repository.account_repository import AccountRepository

logger = logging.getLogger(__name__)


class AccountService:
    def __init__(self, account_repository: AccountRepository):
        self.account_repository = account_repository

    def get_account_by_id(self, account_id: int) -> Account | None:
        """
        Get account by ID
        """
        logger.debug("Fetching account with ID: %d", account_id)
        account = self.account_repository.get_by_id(account_id)
        if account:
            logger.info("Account %d retrieved successfully", account_id)
        else:
            logger.warning("Account %d not found", account_id)
        return account

    def transfer_money(self, from_account_id: int, to_account_id: int, amount: int) -> None:
        """
        Transfer money from one account to another within a single transaction
        """
        logger.info("Transfer initiated: %d from account %d to %d", amount, from_account_id, to_account_id)
        try:
            with self.account_repository.session.begin():
                self.account_repository.withdraw_money(from_account_id, amount)
                self.account_repository.deposit_money(to_account_id, amount)
            logger.info("Transfer completed successfully: %d from %d to %d", amount, from_account_id, to_account_id)
        except Exception as e:
            logger.error("Transfer failed: %s", e, exc_info=True)
            raise

    def withdraw_money(self, account_id: int, amount: int) -> None:
        """
        Withdraw money from an account
        """
        logger.info("Withdrawal initiated: %d from account %d", amount, account_id)
        try:
            with self.account_repository.session.begin():
                self.account_repository.withdraw_money(account_id, amount)
            logger.info("Withdrawal completed: %d from account %d", amount, account_id)
        except Exception as e:
            logger.error("Withdrawal failed: %s", e, exc_info=True)
            raise

    def deposit_money(self, account_id: int, amount: int) -> None:
        """
        Deposit money into an account
        """
        logger.info("Deposit initiated: %d to account %d", amount, account_id)
        try:
            with self.account_repository.session.begin():
                self.account_repository.deposit_money(account_id, amount)
            logger.info("Deposit completed: %d to account %d", amount, account_id)
        except Exception as e:
            logger.error("Deposit failed: %s", e, exc_info=True)
            raise
