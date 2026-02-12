from http.client import HTTPException
from typing import Annotated

from fastapi import APIRouter, Depends

from app.api.dependencies import get_transfer_service
from app.services.bank_service import TransferService

router = APIRouter()

@router.post("/bank/transfer")
def transfer_money_online(from_account_id: int, to_account_id: int, amount: int,
                         transfer_service: Annotated[TransferService, Depends(get_transfer_service)]):
    """
    Transfer money online between two accounts
    """
    try:
        transfer_service.transfer_money(from_account_id, to_account_id, amount)
        return {"message": "Transfer successful"}
    except ValueError as e:
        raise HTTPException(status_code=400) from e
