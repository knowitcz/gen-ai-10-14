from typing import Annotated

from fastapi import Depends
from sqlmodel import Session

from app.db import get_session
from app.repository.account_repository import AccountRepository
from app.repository.client_repository import ClientRepository
from app.repository.health_repository import HealthRepository
from app.services.account_service import AccountService
from app.services.bank_service import OnlineBankService, TransferService
from app.services.client_service import ClientService
from app.services.health_service import HealthService


def get_account_service(session: Annotated[Session, Depends(get_session)]) -> AccountService:
    repo = AccountRepository(session)
    return AccountService(repo)


def get_health_service(session: Annotated[Session, Depends(get_session)]) -> HealthService:
    repo = HealthRepository(session)
    return HealthService(repo)


def get_transfer_service(account_service: Annotated[AccountService, Depends(get_account_service)]) -> TransferService:
    return OnlineBankService(account_service)


def get_client_service(session: Annotated[Session, Depends(get_session)]) -> ClientService:
    repo = ClientRepository(session)
    return ClientService(repo)
