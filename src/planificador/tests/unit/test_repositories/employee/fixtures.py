# c:\Users\raare\Documents\Personal\01Trabajo\AkGroup\Planificador2\src\planificador\tests\unit\test_repositories\employee\fixtures.py
import pytest
from unittest.mock import AsyncMock
from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.employee.employee_repository_facade import EmployeeRepositoryFacade

@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture que crea un mock para la sesión asíncrona de SQLAlchemy."""
    return AsyncMock(spec=AsyncSession)

@pytest.fixture
def employee_repository(mock_session: AsyncMock) -> EmployeeRepositoryFacade:
    """Fixture que crea una instancia del EmployeeRepositoryFacade con una sesión mockeada."""
    return EmployeeRepositoryFacade(session=mock_session)