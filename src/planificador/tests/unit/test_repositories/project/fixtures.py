"""Fixtures para tests de ProjectRepositoryFacade."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.project.project_repository_facade import (
    ProjectRepositoryFacade,
)
from planificador.models.project import Project


@pytest.fixture
def mock_session():
    """Mock de AsyncSession para tests."""
    session = AsyncMock(spec=AsyncSession)
    session.rollback = AsyncMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def project_repository(mock_session):
    """Fixture que proporciona una instancia de ProjectRepositoryFacade con mocks."""
    # Crear mocks para todas las operaciones
    mock_crud = AsyncMock()
    
    # Mock especial para query_operations que tiene métodos sync y async
    mock_query = AsyncMock()
    # Configurar métodos síncronos específicos
    mock_query._base_query = MagicMock()
    mock_query.filter_by_status = MagicMock()
    mock_query.filter_by_priority = MagicMock()
    mock_query.filter_by_date_range = MagicMock()
    mock_query.filter_by_reference = MagicMock()
    mock_query.filter_by_trigram = MagicMock()
    mock_query.filter_by_name = MagicMock()
    mock_query.filter_by_client = MagicMock()
    mock_query.with_client = MagicMock()
    mock_query.with_assignments = MagicMock()
    mock_query.with_full_details = MagicMock()
    mock_query.format_project_dates = MagicMock()
    
    mock_relationship = AsyncMock()
    mock_statistics = AsyncMock()
    mock_validation = AsyncMock()
    
    # Crear facade con dependencias inyectadas
    facade = ProjectRepositoryFacade(
        session=mock_session,
        query_operations=mock_query,
        validation_operations=mock_validation,
        relationship_operations=mock_relationship,
        crud_operations=mock_crud,
        statistics_operations=mock_statistics,
    )
    
    return facade


@pytest.fixture
def sample_project():
    """Fixture que proporciona datos de ejemplo para un proyecto."""
    return Project(
        id=1,
        reference="PROJ-001",
        trigram="P01",
        name="Proyecto de Ejemplo",
        details="Detalles del proyecto de ejemplo",
        client_id=1,
    )


@pytest.fixture
def sample_project_data():
    """Fixture que proporciona datos de ejemplo para crear un proyecto."""
    return {
        "reference": "PROJ-002",
        "trigram": "P02",
        "name": "Nuevo Proyecto",
        "details": "Detalles del nuevo proyecto",
        "client_id": 2,
    }