# src/planificador/tests/unit/test_repositories/workload/fixtures.py

import pytest
from unittest.mock import AsyncMock, MagicMock
import pendulum
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.database.database import DatabaseManager
from planificador.config.config import settings


@pytest.fixture
async def db_session() -> AsyncSession:
    """
    Fixture para proporcionar una sesión de base de datos de prueba.
    """
    db_manager = DatabaseManager()
    async with db_manager.get_session() as session:
        yield session


from planificador.repositories.workload.workload_repository_facade import WorkloadRepositoryFacade
from planificador.schemas.workload.workload import WorkloadCreate, WorkloadUpdate
from planificador.models.workload import Workload

@pytest.fixture
def sample_workload_data():
    """
    Proporciona datos de muestra para una carga de trabajo que coinciden con el modelo Workload.
    """
    now = pendulum.now()
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": now.date(),
        "week_number": now.week_of_year,
        "month": now.month,
        "year": now.year,
        "planned_hours": 8.0,
        "actual_hours": 7.5,
        "notes": "Desarrollo de nueva funcionalidad",
        "is_billable": True,
        "utilization_percentage": 93.75,
        "efficiency_score": 93.75,
        "productivity_index": 95.0,
    }

@pytest.fixture
def workload_repository_facade(sample_workload_data) -> WorkloadRepositoryFacade:
    """
    Crea una instancia de WorkloadRepositoryFacade con una sesión de base de datos mockeada.
    """
    mock_session = AsyncMock(spec=AsyncSession)
    facade = WorkloadRepositoryFacade(mock_session)

    # Mockear los módulos internos de la fachada
    facade.crud_module = MagicMock()
    facade.query_module = MagicMock()
    facade.validation_module = MagicMock()
    facade.relationship_module = MagicMock()
    facade.statistics_module = MagicMock()

    # Configurar los mocks para las operaciones CRUD
    facade.crud_module.create_workload = AsyncMock(return_value=Workload(id=1, **sample_workload_data))
    facade.crud_module.get_workload_by_id = AsyncMock(return_value=Workload(id=1, **sample_workload_data))
    facade.crud_module.update_workload = AsyncMock(return_value=Workload(id=1, **sample_workload_data))
    facade.crud_module.delete_workload = AsyncMock(return_value=True)

    return facade