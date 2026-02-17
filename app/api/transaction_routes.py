import logging
from datetime import datetime
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException, Query

from app.api.dependencies import get_transaction_service
from app.models.schemas import TransactionHistoryResponse
from app.services.transaction_service import TransactionService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get(
    "/clients/{client_id}/transactions",
    response_model=TransactionHistoryResponse,
)
def get_client_transactions(
    client_id: int,
    transaction_service: Annotated[TransactionService, Depends(get_transaction_service)],
    from_date: Annotated[datetime | None, Query()] = None,
    to_date: Annotated[datetime | None, Query()] = None,
    account_id: Annotated[int | None, Query()] = None,
):
    """
    Retrieve transaction history and summary for a client.
    Optionally filter by date range and/or specific account.
    """
    logger.info(
        "GET /clients/%s/transactions (from=%s, to=%s, account=%s)",
        client_id,
        from_date,
        to_date,
        account_id,
    )
    try:
        return transaction_service.get_client_transactions(
            client_id=client_id,
            from_date=from_date,
            to_date=to_date,
            account_id=account_id,
        )
    except ValueError as e:
        raise HTTPException(status_code=404, detail=str(e)) from e
