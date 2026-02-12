from typing import TYPE_CHECKING

from sqlmodel import Field, Relationship, SQLModel

if TYPE_CHECKING:
    from app.models.account import Account


class Client(SQLModel, table=True):
    id: int | None = Field(default=None, primary_key=True)
    name: str
    national_number: str = Field(unique=True)

    accounts: list["Account"] = Relationship(back_populates="client")
