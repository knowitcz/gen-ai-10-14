import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_client_service
from app.models.schemas import ClientCreate, ClientDetailRead, ClientRead, ClientUpdate
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


@router.post("/client", response_model=ClientDetailRead, status_code=201)
def create_client(
    payload: ClientCreate,
    client_service: Annotated[ClientService, Depends(get_client_service)],
):
    logger.info("POST /client - creating a new client")
    return client_service.create_client(payload.name, payload.national_number)


@router.put("/client/{id}", response_model=ClientDetailRead)
def update_client(
    id: int,
    payload: ClientUpdate,
    client_service: Annotated[ClientService, Depends(get_client_service)],
):
    logger.info(f"PUT /client/{id} - updating client")
    if client := client_service.update_client(id, payload.name, payload.national_number):
        return client
    raise HTTPException(status_code=404, detail="Client not found")


@router.delete("/client/{id}", status_code=204)
def delete_client(
    id: int,
    client_service: Annotated[ClientService, Depends(get_client_service)],
):
    logger.info(f"DELETE /client/{id} - deleting client")
    if not client_service.delete_client(id):
        raise HTTPException(status_code=404, detail="Client not found")
