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
