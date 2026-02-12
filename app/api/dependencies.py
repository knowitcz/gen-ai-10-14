from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db import get_session
from app.repository.account_repository import AccountRepository
from app.services.account_service import AccountService
from app.services.bank_service import OnlineBankService, TransferService


def get_account_service(session: Annotated[Session, Depends(get_session)]) -> AccountService:
    repo = AccountRepository(session)
    return AccountService(repo)

def get_transfer_service(account_service: Annotated[AccountService, Depends(get_account_service)]) -> TransferService:
    return OnlineBankService(account_service)
