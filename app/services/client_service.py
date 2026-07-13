import logging

from app.models.client import Client
from app.repository.client_repository import ClientRepository

logger = logging.getLogger(__name__)


class ClientService:
    def __init__(self, client_repository: ClientRepository):
        self.client_repository = client_repository

    def get_all_clients(self) -> list[Client]:
        """
        Get all clients.
        """
        logger.info("Fetching all clients")
        try:
            clients = self.client_repository.get_all()
            logger.info(f"Retrieved {len(clients)} clients successfully")
            return clients
        except Exception as e:
            logger.error(f"Failed to fetch clients: {e}", exc_info=True)
            raise

    def get_client_by_id(self, client_id: int) -> Client | None:
        """
        Get a client by ID, including their associated accounts.
        """
        logger.debug(f"Fetching client with ID: {client_id}")
        client = self.client_repository.get_by_id(client_id)
        if client:
            logger.info(f"Client {client_id} retrieved successfully")
        else:
            logger.warning(f"Client {client_id} not found")
        return client
