from unittest.mock import Mock

import pytest

from app.services.health_service import HealthService


def test_check_health_returns_ok_status() -> None:
    repo = Mock()
    service = HealthService(repo)

    result = service.check_health()

    assert result == {"status": "ok"}
    repo.check_database.assert_called_once_with()


def test_check_health_propagates_repository_errors() -> None:
    repo = Mock()
    repo.check_database.side_effect = RuntimeError("db down")
    service = HealthService(repo)

    with pytest.raises(RuntimeError, match="db down"):
        service.check_health()
