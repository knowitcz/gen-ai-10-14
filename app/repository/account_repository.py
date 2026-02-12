from sqlmodel import Session, select

from app.models.account import Account


class AccountRepository:
    """
    Repository class for performing operations on Account objects in the database.
    """

    def __init__(self, session: Session):
        """
        Initialize the AccountRepository with a database session.

        :param session: SQLModel Session object for database operations.
        """
        self.session = session

    def get_by_id(self, account_id: int) -> Account | None:
        """
        Get an account by ID.

        :param account_id: The ID of the account to retrieve.
        :return: The Account object if found, otherwise None.
        """
        statement = select(Account).where(Account.id == account_id)
        account = self.session.exec(statement).first()
        return account

    def withdraw_money(self, account_id: int, amount: int) -> None:
        """
        Withdraw money from an account.

        :param account_id: The ID of the account to withdraw from.
        :param amount: The amount of money to withdraw.
        :raises ValueError: If the account is not found or has insufficient balance.
        :return: None
        """
        account = self.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        if account.balance < amount:
            raise ValueError("Insufficient balance")
        account.balance -= amount
        self.session.add(account)

    def deposit_money(self, account_id: int, amount: int) -> None:
        """
        Deposit money into an account.

        :param account_id: The ID of the account to deposit into.
        :param amount: The amount of money to deposit.
        :raises ValueError: If the account is not found.
        :return: None
        """
        account = self.get_by_id(account_id)
        if not account:
            raise ValueError("Account not found")
        account.balance += amount
        self.session.add(account)
