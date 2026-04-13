import logging

from app.repository.health_repository import HealthRepository

logger = logging.getLogger(__name__)


class HealthService:
    def __init__(self, health_repository: HealthRepository):
        self.health_repository = health_repository

    def check_health(self) -> dict[str, str]:
        logger.info("Health check started")
        try:
            self.health_repository.check_database()
            logger.info("Health check completed successfully")
            return {"status": "ok"}
        except Exception as error:
            logger.error("Health check failed: %s", error, exc_info=True)
            raise
