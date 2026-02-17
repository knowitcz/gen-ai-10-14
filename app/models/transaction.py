from datetime import datetime, timezone

from sqlmodel import Field, SQLModel


class Transaction(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    source_account_id: int | None = Field(default=None, foreign_key="account.id")
    target_account_id: int | None = Field(default=None, foreign_key="account.id")
    amount: int
    date: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
    created_at: datetime = Field(default_factory=lambda: datetime.now(tz=timezone.utc))
