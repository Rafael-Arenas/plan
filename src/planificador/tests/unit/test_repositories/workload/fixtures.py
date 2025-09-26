# src/planificador/tests/unit/test_repositories/workload/fixtures.py

"""
Fixtures para tests del repositorio Workload.

Este módulo contiene las fixtures reutilizables para los tests
del repositorio de cargas de trabajo, incluyendo datos de prueba
y objetos mock necesarios.

Principios:
    - Reutilización: Fixtures compartidas entre tests
    - Realismo: Datos que reflejan casos reales
    - Flexibilidad: Fixtures parametrizables cuando sea necesario
"""

import pytest
from datetime import date, datetime
from decimal import Decimal
from unittest.mock import AsyncMock

from planificador.models.workload import Workload
from planificador.schemas.workload.workload import WorkloadCreate


@pytest.fixture
def sample_workload_data():
    """Datos de ejemplo para crear una carga de trabajo."""
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": date(2024, 1, 15),
        "week_number": 3,
        "month": 1,
        "year": 2024,
        "planned_hours": Decimal("8.0"),
        "actual_hours": Decimal("7.5"),
        "utilization_percentage": Decimal("93.75"),
        "efficiency_score": Decimal("106.67"),
        "productivity_index": Decimal("95.0"),
        "is_billable": True,
        "notes": "Trabajo en desarrollo de funcionalidad principal"
    }


@pytest.fixture
def sample_workload_create(sample_workload_data):
    """Schema WorkloadCreate de ejemplo."""
    return WorkloadCreate(**sample_workload_data)


@pytest.fixture
def sample_workload_model():
    """Modelo Workload de ejemplo."""
    return Workload(
        id=1,
        employee_id=1,
        project_id=1,
        date=date(2024, 1, 15),
        week_number=3,
        month=1,
        year=2024,
        planned_hours=Decimal("8.0"),
        actual_hours=Decimal("7.5"),
        utilization_percentage=Decimal("93.75"),
        efficiency_score=Decimal("106.67"),
        productivity_index=Decimal("95.0"),
        is_billable=True,
        notes="Trabajo en desarrollo de funcionalidad principal",
        created_at=datetime(2024, 1, 15, 10, 0, 0),
        updated_at=datetime(2024, 1, 15, 10, 0, 0)
    )


@pytest.fixture
def sample_workload_update_data():
    """Datos de ejemplo para actualizar una carga de trabajo."""
    return {
        "actual_hours": Decimal("8.0"),
        "utilization_percentage": Decimal("100.0"),
        "efficiency_score": Decimal("100.0"),
        "productivity_index": Decimal("100.0"),
        "notes": "Trabajo completado según planificación"
    }


@pytest.fixture
def invalid_workload_data():
    """Datos inválidos para tests de error."""
    return {
        "employee_id": -1,  # ID inválido
        "project_id": None,
        "date": date(2024, 1, 15),
        "week_number": 55,  # Semana inválida
        "month": 13,  # Mes inválido
        "year": 2019,  # Año inválido
        "planned_hours": Decimal("25.0"),  # Más de 24 horas
        "actual_hours": Decimal("50.0"),  # Más del doble de las planificadas
        "utilization_percentage": Decimal("150.0"),  # Más del 100%
        "efficiency_score": Decimal("-10.0"),  # Negativo
        "productivity_index": Decimal("200.0"),  # Más del 100%
        "is_billable": True
    }


@pytest.fixture
def mock_crud_operations():
    """Mock para WorkloadCrudModule."""
    mock = AsyncMock()
    mock.create_workload = AsyncMock()
    mock.update_workload = AsyncMock()
    mock.get_workload_by_id = AsyncMock()
    mock.delete_workload = AsyncMock()
    return mock


@pytest.fixture
def mock_query_operations():
    """Mock para WorkloadQueryModule."""
    mock = AsyncMock()
    mock.get_workloads_by_employee = AsyncMock()
    mock.get_workloads_by_project = AsyncMock()
    mock.get_workloads_by_date_range = AsyncMock()
    return mock


@pytest.fixture
def mock_validation_operations():
    """Mock para WorkloadValidationModule."""
    mock = AsyncMock()
    mock.validate_create_data = AsyncMock()
    mock.validate_update_data = AsyncMock()
    mock.validate_workload_conflicts = AsyncMock()
    return mock


@pytest.fixture
def mock_statistics_operations():
    """Mock para WorkloadStatisticsModule."""
    mock = AsyncMock()
    mock.get_employee_total_hours = AsyncMock()
    mock.get_project_total_hours = AsyncMock()
    mock.calculate_utilization_metrics = AsyncMock()
    return mock


@pytest.fixture
def mock_relationship_operations():
    """Mock para WorkloadRelationshipModule."""
    mock = AsyncMock()
    mock.get_employee_workloads = AsyncMock()
    mock.get_project_workloads = AsyncMock()
    mock.analyze_workload_dependencies = AsyncMock()
    return mock