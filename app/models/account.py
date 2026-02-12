from typing import TYPE_CHECKING, Optional

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.client import Client


class Account(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    balance: int
    type: str
    client_id: int = Field(foreign_key="client.id")

    client: Optional["Client"] = Relationship(back_populates="accounts")
