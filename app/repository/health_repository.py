import logging

from sqlalchemy import text
from sqlmodel import Session

logger = logging.getLogger(__name__)


class HealthRepository:
    def __init__(self, session: Session):
        self.session = session

    def check_database(self) -> None:
        logger.debug("Executing database health check query")
        self.session.exec(text("SELECT 1"))
