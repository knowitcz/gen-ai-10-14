import logging
from typing import Annotated

from fastapi import APIRouter, Depends, HTTPException

from app.api.dependencies import get_health_service
from app.services.health_service import HealthService

logger = logging.getLogger(__name__)

router = APIRouter()


@router.get("/health")
def health_check(
    health_service: Annotated[HealthService, Depends(get_health_service)],
) -> dict[str, str]:
    logger.info("Health endpoint accessed")
    try:
        return health_service.check_health()
    except Exception as error:
        logger.error("Health endpoint failed: %s", error, exc_info=True)
        raise HTTPException(status_code=503, detail="Service unhealthy") from error
