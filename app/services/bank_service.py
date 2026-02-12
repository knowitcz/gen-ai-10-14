import abc

from app.services.account_service import AccountService
from app.validator.amount_validator import AmountValidator


class CashService(abc.ABC):
    @abc.abstractmethod
    def deposit_money(self, account_id: int, amount: int) -> None:
        """
        Deposit money into an account
        """
        ...

    @abc.abstractmethod
    def withdraw_money(self, account_id: int, amount: int) -> None:
        """
        Withdraw money from an account
        """
        ...


class TransferService(abc.ABC):
    @abc.abstractmethod
    def transfer_money(self, from_account_id: int, to_account_id: int, amount: int) -> None:
        """
        Transfer money between two accounts
        """
        ...


class BranchBankService(CashService, TransferService):
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def deposit_money(self, account_id: int, amount: int) -> None:
        self.account_service.deposit_money(account_id, amount)

    def withdraw_money(self, account_id: int, amount: int) -> None:
        self.account_service.withdraw_money(account_id, amount)

    def transfer_money(self, from_account_id: int, to_account_id: int, amount: int) -> None:
        self.account_service.transfer_money(from_account_id, to_account_id, amount)


class AtmBankService(CashService):
    def __init__(self, account_service: AccountService, amount_validator: AmountValidator):
        self.account_service = account_service
        self.amount_validator = amount_validator

    def deposit_money(self, account_id: int, amount: int) -> None:
        self.amount_validator(amount).raise_if_error()
        self.account_service.deposit_money(account_id, amount)

    def withdraw_money(self, account_id: int, amount: int) -> None:
        self.amount_validator(amount).raise_if_error()
        self.account_service.withdraw_money(account_id, amount)


class OnlineBankService(TransferService):
    def __init__(self, account_service: AccountService):
        self.account_service = account_service

    def transfer_money(self, from_account_id: int, to_account_id: int, amount: int) -> None:
        self.account_service.transfer_money(from_account_id, to_account_id, amount)
