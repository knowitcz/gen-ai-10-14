from unittest.mock import Mock

import pytest

from app.repository.health_repository import HealthRepository


def test_check_database_executes_select() -> None:
    session = Mock()
    repo = HealthRepository(session)

    repo.check_database()

    session.exec.assert_called_once()


def test_check_database_propagates_db_errors() -> None:
    session = Mock()
    session.exec.side_effect = RuntimeError("db down")
    repo = HealthRepository(session)

    with pytest.raises(RuntimeError, match="db down"):
        repo.check_database()
