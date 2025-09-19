"""Configuración de fixtures para tests del repositorio de códigos de estado."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from typing import Dict, Any, List
import pendulum

from planificador.repositories.status_code.status_code_repository_facade import (
    StatusCodeRepositoryFacade,
)
from planificador.models.status_code import StatusCode


@pytest.fixture
def mock_session():
    """Mock de sesión de base de datos."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_crud_module():
    """Mock del módulo CRUD."""
    crud_module = AsyncMock()
    crud_module.create_status_code = AsyncMock()
    crud_module.get_status_code_by_id = AsyncMock()
    crud_module.get_all_status_codes = AsyncMock()
    crud_module.update_status_code = AsyncMock()
    crud_module.delete_status_code = AsyncMock()
    return crud_module


@pytest.fixture
def mock_query_module():
    """Mock del módulo de consultas."""
    query_module = AsyncMock()
    query_module.find_by_code = AsyncMock()
    query_module.find_by_name = AsyncMock()
    query_module.find_by_text_search = AsyncMock()
    query_module.find_active_status_codes = AsyncMock()
    query_module.find_inactive_status_codes = AsyncMock()
    query_module.find_default_status_codes = AsyncMock()
    query_module.find_by_display_order_range = AsyncMock()
    query_module.find_with_advanced_filters = AsyncMock()
    query_module.get_status_codes_paginated = AsyncMock()
    query_module.get_ordered_status_codes = AsyncMock()
    return query_module


@pytest.fixture
def mock_validation_module():
    """Mock del módulo de validación."""
    validation_module = AsyncMock()
    validation_module.validate_unique_code = AsyncMock()
    validation_module.validate_unique_name = AsyncMock()
    validation_module.validate_status_code_data = AsyncMock()
    validation_module.validate_display_order_conflicts = AsyncMock()
    validation_module.validate_default_status_rules = AsyncMock()
    return validation_module


@pytest.fixture
def mock_statistics_module():
    """Mock del módulo de estadísticas."""
    statistics_module = AsyncMock()
    statistics_module.get_status_code_statistics = AsyncMock()
    statistics_module.get_status_distribution_analysis = AsyncMock()
    statistics_module.get_display_order_metrics = AsyncMock()
    statistics_module.get_usage_performance_metrics = AsyncMock()
    statistics_module.get_data_integrity_report = AsyncMock()
    statistics_module.get_status_code_health_check = AsyncMock()
    return statistics_module


@pytest.fixture
def status_code_repository_facade(
    mock_session,
    mock_crud_module,
    mock_query_module,
    mock_validation_module,
    mock_statistics_module,
):
    """Fixture del facade del repositorio StatusCode con mocks."""
    facade = StatusCodeRepositoryFacade(mock_session)
    
    # Inyectar los mocks
    facade._crud_module = mock_crud_module
    facade._query_module = mock_query_module
    facade._validation_module = mock_validation_module
    facade._statistics_module = mock_statistics_module
    
    return facade


@pytest.fixture
def sample_status_code():
    """Fixture de un código de estado de ejemplo."""
    return StatusCode(
        id=1,
        code="WORK",
        name="Trabajo",
        description="Tiempo de trabajo productivo",
        color="#4CAF50",
        icon="work",
        is_billable=True,
        is_productive=True,
        requires_approval=False,
        is_active=True,
        sort_order=1,
        created_at=pendulum.now(),
        updated_at=pendulum.now()
    )


@pytest.fixture
def sample_status_code_data():
    """Fixture de datos para crear un código de estado."""
    return {
        "code": "MEET",
        "name": "Reunión",
        "description": "Tiempo en reuniones",
        "color": "#2196F3",
        "icon": "meeting_room",
        "is_billable": True,
        "is_productive": True,
        "requires_approval": False,
        "is_active": True,
        "sort_order": 2
    }


@pytest.fixture
def sample_status_codes_list():
    """Fixture de lista de códigos de estado."""
    return [
        StatusCode(
            id=1,
            code="WORK",
            name="Trabajo",
            description="Tiempo de trabajo productivo",
            color="#4CAF50",
            icon="work",
            is_billable=True,
            is_productive=True,
            requires_approval=False,
            is_active=True,
            sort_order=1,
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        ),
        StatusCode(
            id=2,
            code="MEET",
            name="Reunión",
            description="Tiempo en reuniones",
            color="#2196F3",
            icon="meeting_room",
            is_billable=True,
            is_productive=True,
            requires_approval=False,
            is_active=True,
            sort_order=2,
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        ),
        StatusCode(
            id=3,
            code="BREAK",
            name="Descanso",
            description="Tiempo de descanso",
            color="#FF9800",
            icon="coffee",
            is_billable=False,
            is_productive=False,
            requires_approval=False,
            is_active=True,
            sort_order=3,
            created_at=pendulum.now(),
            updated_at=pendulum.now()
        )
    ]


@pytest.fixture
def sample_update_data():
    """Fixture de datos para actualizar un código de estado."""
    return {
        "name": "Trabajo Actualizado",
        "description": "Descripción actualizada",
        "color": "#FF5722",
        "is_billable": False
    }


@pytest.fixture
def sample_advanced_filters():
    """Fixture de filtros avanzados."""
    return {
        "is_active": True,
        "is_billable": True,
        "is_productive": True,
        "requires_approval": False
    }


@pytest.fixture
def sample_statistics():
    """Fixture de estadísticas de códigos de estado."""
    return {
        "total_count": 10,
        "active_count": 8,
        "inactive_count": 2,
        "billable_count": 6,
        "productive_count": 7,
        "requires_approval_count": 2,
        "distribution": {
            "billable_productive": 5,
            "billable_non_productive": 1,
            "non_billable_productive": 2,
            "non_billable_non_productive": 2
        }
    }


@pytest.fixture
def sample_validation_errors():
    """Fixture de errores de validación."""
    return {
        "code": ["El código ya existe"],
        "name": ["El nombre es requerido"],
        "sort_order": ["El orden debe ser único"]
    }


@pytest.fixture
def sample_health_check_result():
    """Fixture de resultado de health check."""
    return {
        "facade": "healthy",
        "session": "connected",
        "modules": {
            "crud": "healthy",
            "query": "healthy",
            "validation": "healthy",
            "statistics": "healthy"
        }
    }