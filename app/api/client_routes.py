import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_client_service
from app.models.schemas import ClientDetailRead, ClientRead
from app.services.client_service import ClientService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/client", response_model=list[ClientRead])
def get_clients(
    client_service: Annotated[ClientService, Depends(get_client_service)],
):
    logger.info("GET /client - listing all clients")
    return client_service.get_all_clients()


@router.get("/client/{id}", response_model=ClientDetailRead)
def get_client(
    id: int,
    client_service: Annotated[ClientService, Depends(get_client_service)],
):
    logger.info(f"GET /client/{id} - fetching client details")
    if client := client_service.get_client_by_id(id):
        return client
    raise HTTPException(status_code=404, detail="Client not found")
