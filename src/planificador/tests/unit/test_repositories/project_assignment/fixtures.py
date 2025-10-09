"""Fixtures para las pruebas del repositorio de asignaciones de proyecto."""

from datetime import date
from unittest.mock import AsyncMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.schemas.assignment.assignment import ProjectAssignmentCreate, ProjectAssignmentUpdate


@pytest.fixture
def mock_session() -> AsyncMock:
    """Fixture que proporciona una sesión de base de datos mockeada."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def project_assignment_repository(mock_session: AsyncMock) -> ProjectAssignmentRepositoryFacade:
    """Fixture que proporciona una instancia real del facade con dependencias mockeadas."""
    facade = ProjectAssignmentRepositoryFacade(mock_session)
    
    # Mockear solo las operaciones internas para que los métodos del facade funcionen
    facade._crud_operations = AsyncMock()
    facade._query_operations = AsyncMock()
    facade._relationship_operations = AsyncMock()
    facade._search_operations = AsyncMock()
    facade._statistics_operations = AsyncMock()
    facade._validation_operations = AsyncMock()
    
    return facade


@pytest.fixture
def sample_assignment_create() -> ProjectAssignmentCreate:
    """Fixture que proporciona datos de ejemplo para crear una asignación."""
    return ProjectAssignmentCreate(
        employee_id=1,
        project_id=1,
        role="Developer",
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        allocation_percentage=80.0,
        hours_per_day=6.4,
        status="active",
        allocation_category="full_time"
    )


@pytest.fixture
def sample_assignment_update() -> ProjectAssignmentUpdate:
    """Fixture que proporciona datos de ejemplo para actualizar una asignación."""
    return ProjectAssignmentUpdate(
        allocation_percentage=90.0,
        hours_per_day=7.2,
        status="active"
    )


@pytest.fixture
def sample_assignment_data() -> dict:
    """Fixture que proporciona datos de asignación en formato diccionario."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "role": "Developer",
        "start_date": date(2024, 1, 1),
        "end_date": date(2024, 12, 31),
        "allocation_percentage": 80.0,
        "hours_per_day": 6.4,
        "status": "active",
        "allocation_category": "full_time"
    }


@pytest.fixture
def sample_date_range() -> tuple[date, date]:
    """Fixture que proporciona un rango de fechas de ejemplo."""
    return date(2024, 1, 1), date(2024, 12, 31)