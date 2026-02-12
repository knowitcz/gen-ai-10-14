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

    def create_client(self, name: str, national_number: str) -> Client:
        """
        Create a new client.
        """
        logger.info(f"Creating client with national number: {national_number}")
        try:
            with self.client_repository.session.begin():
                client = self.client_repository.create(name, national_number)
                client_id = client.id
            logger.info(f"Client {client_id} created successfully")
            return self.client_repository.get_by_id(client_id)
        except Exception as e:
            logger.error(f"Failed to create client: {e}", exc_info=True)
            raise

    def update_client(
        self, client_id: int, name: str | None = None, national_number: str | None = None
    ) -> Client | None:
        """
        Update an existing client.
        """
        logger.info(f"Updating client with ID: {client_id}")
        try:
            with self.client_repository.session.begin():
                updated = self.client_repository.update(client_id, name, national_number)
            if updated is None:
                logger.warning(f"Client {client_id} not found for update")
                return None
            logger.info(f"Client {client_id} updated successfully")
            return self.client_repository.get_by_id(client_id)
        except Exception as e:
            logger.error(f"Failed to update client {client_id}: {e}", exc_info=True)
            raise

    def delete_client(self, client_id: int) -> bool:
        """
        Delete a client by ID.
        """
        logger.info(f"Deleting client with ID: {client_id}")
        try:
            with self.client_repository.session.begin():
                deleted = self.client_repository.delete(client_id)
            if deleted:
                logger.info(f"Client {client_id} deleted successfully")
            else:
                logger.warning(f"Client {client_id} not found for deletion")
            return deleted
        except Exception as e:
            logger.error(f"Failed to delete client {client_id}: {e}", exc_info=True)
            raise
