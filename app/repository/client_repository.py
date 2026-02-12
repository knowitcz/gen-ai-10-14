import logging

from sqlalchemy.orm import selectinload
from sqlmodel import Session, select

from app.models.client import Client

logger = logging.getLogger(__name__)


class ClientRepository:
    """
    Repository class for performing operations on Client objects in the database.
    """

    def __init__(self, session: Session):
        """
        Initialize the ClientRepository with a database session.

        :param session: SQLModel Session object for database operations.
        """
        self.session = session

    def get_all(self) -> list[Client]:
        """
        Get all clients.

        :return: A list of all Client objects.
        """
        logger.debug("Fetching all clients")
        statement = select(Client)
        clients = self.session.exec(statement).all()
        logger.debug(f"Found {len(clients)} clients")
        return list(clients)

    def get_by_id(self, client_id: int) -> Client | None:
        """
        Get a client by ID, including their associated accounts.

        :param client_id: The ID of the client to retrieve.
        :return: The Client object if found, otherwise None.
        """
        logger.debug(f"Fetching client with ID: {client_id}")
        statement = (
            select(Client)
            .where(Client.id == client_id)
            .options(selectinload(Client.accounts))  # type: ignore[arg-type]
        )
        client = self.session.exec(statement).first()
        return client

    def create(self, name: str, national_number: str) -> Client:
        """
        Create a new client.

        :param name: The name of the client.
        :param national_number: The unique national number of the client.
        :return: The newly created Client object with its generated ID.
        """
        logger.debug(f"Creating client with national number: {national_number}")
        client = Client(name=name, national_number=national_number)
        self.session.add(client)
        self.session.flush()
        self.session.refresh(client)
        return client

    def update(self, client_id: int, name: str | None = None, national_number: str | None = None) -> Client | None:
        """
        Update an existing client. Only the provided fields are changed.

        :param client_id: The ID of the client to update.
        :param name: The new name, or None to leave unchanged.
        :param national_number: The new national number, or None to leave unchanged.
        :return: The updated Client object, or None if the client does not exist.
        """
        logger.debug(f"Updating client with ID: {client_id}")
        client = self.get_by_id(client_id)
        if not client:
            return None
        if name is not None:
            client.name = name
        if national_number is not None:
            client.national_number = national_number
        self.session.add(client)
        return client

    def delete(self, client_id: int) -> bool:
        """
        Delete a client by ID.

        :param client_id: The ID of the client to delete.
        :return: True if a client was deleted, False if none was found.
        """
        logger.debug(f"Deleting client with ID: {client_id}")
        client = self.get_by_id(client_id)
        if not client:
            return False
        self.session.delete(client)
        return True
