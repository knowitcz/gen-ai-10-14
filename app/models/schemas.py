from datetime import datetime

from pydantic import computed_field
from sqlmodel import SQLModel


class AccountRead(SQLModel):
    id: int
    name: str
    balance: int
    type: str
    client_id: int


class ClientRead(SQLModel):
    id: int
    name: str
    national_number: str


class ClientDetailRead(ClientRead):
    accounts: list[AccountRead] = []


class TransactionRead(SQLModel):
    id: int
    source_account_id: int | None
    target_account_id: int | None
    amount: int
    date: datetime

    @computed_field  # type: ignore[prop-decorator]
    @property
    def type(self) -> str:
        if self.source_account_id is None:
            return "DEPOSIT"
        if self.target_account_id is None:
            return "WITHDRAWAL"
        return "TRANSFER"


class TransactionSummary(SQLModel):
    total_incoming: int
    total_outgoing: int


class TransactionHistoryResponse(SQLModel):
    summary: TransactionSummary
    transactions: list[TransactionRead] = []
