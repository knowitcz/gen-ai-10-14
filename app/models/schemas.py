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
