# src/planificador/tests/unit/test_repositories/schedule/fixtures.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.schedule.schedule_repository_facade import ScheduleRepositoryFacade

@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture que crea un mock para la sesión asíncrona de SQLAlchemy."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def schedule_repository(mock_session: AsyncMock) -> ScheduleRepositoryFacade:
    """Fixture que crea una instancia del ScheduleRepositoryFacade con módulos mockeados."""
    facade = ScheduleRepositoryFacade(session=mock_session)
    
    # Mockear todos los módulos internos
    facade.crud_module = AsyncMock()
    facade.query_module = AsyncMock()
    facade.validation_module = AsyncMock()
    facade.relationship_module = AsyncMock()
    facade.statistics_module = AsyncMock()
    
    return facade