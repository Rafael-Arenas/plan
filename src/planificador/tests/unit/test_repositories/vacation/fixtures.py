# src/planificador/tests/unit/test_repositories/vacation/fixtures.py
"""
Fixtures para tests del repositorio de vacaciones.

Este módulo proporciona fixtures reutilizables para crear datos de prueba
consistentes y realistas para el testing del VacationRepositoryFacade.
"""

import pytest
from datetime import date, datetime
from typing import Dict, Any, List
from unittest.mock import AsyncMock, MagicMock
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.vacation import Vacation, VacationType, VacationStatus
from planificador.repositories.vacation.vacation_repository_facade import VacationRepositoryFacade


@pytest.fixture
def mock_vacation_session() -> AsyncMock:
    """Fixture que crea un mock para la sesión asíncrona de SQLAlchemy."""
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def vacation_facade(mock_vacation_session: AsyncMock) -> VacationRepositoryFacade:
    """Fixture que crea una instancia del VacationRepositoryFacade con una sesión mockeada."""
    return VacationRepositoryFacade(session=mock_vacation_session)


# Fixtures de datos base para vacaciones
@pytest.fixture
def base_vacation_data() -> Dict[str, Any]:
    """Datos base para crear una vacación de prueba."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 7, 1),
        "end_date": date(2024, 7, 15),
        "vacation_type": VacationType.ANNUAL,
        "status": VacationStatus.PENDING,
        "requested_date": date(2024, 6, 1),
        "approved_date": None,
        "approved_by": None,
        "reason": "Vacaciones de verano",
        "notes": "Vacaciones planificadas con anticipación",
        "total_days": 15,
        "business_days": 11
    }


@pytest.fixture
def vacation_create_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para crear una nueva vacación."""
    return base_vacation_data.copy()


@pytest.fixture
def vacation_update_data() -> Dict[str, Any]:
    """Datos para actualizar una vacación existente."""
    return {
        "status": VacationStatus.APPROVED,
        "approved_date": date(2024, 6, 15),
        "approved_by": "Manager Test",
        "notes": "Vacaciones aprobadas - Actualizado"
    }


@pytest.fixture
def sample_vacation_instance(base_vacation_data: Dict[str, Any]) -> Vacation:
    """Instancia de vacación de ejemplo para tests."""
    vacation = Vacation(**base_vacation_data)
    vacation.id = 1
    vacation.created_at = datetime(2024, 6, 1, 10, 0, 0)
    vacation.updated_at = datetime(2024, 6, 1, 10, 0, 0)
    return vacation


# Fixtures para diferentes tipos de vacaciones
@pytest.fixture
def annual_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación anual."""
    data = base_vacation_data.copy()
    data.update({
        "vacation_type": VacationType.ANNUAL,
        "reason": "Vacaciones anuales programadas",
        "total_days": 15,
        "business_days": 11
    })
    return data


@pytest.fixture
def sick_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación por enfermedad."""
    data = base_vacation_data.copy()
    data.update({
        "vacation_type": VacationType.SICK,
        "start_date": date(2024, 8, 1),
        "end_date": date(2024, 8, 3),
        "reason": "Licencia médica",
        "total_days": 3,
        "business_days": 3
    })
    return data


@pytest.fixture
def personal_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación personal."""
    data = base_vacation_data.copy()
    data.update({
        "vacation_type": VacationType.PERSONAL,
        "start_date": date(2024, 9, 15),
        "end_date": date(2024, 9, 16),
        "reason": "Asuntos personales",
        "total_days": 2,
        "business_days": 2
    })
    return data


# Fixtures para diferentes estados de vacaciones
@pytest.fixture
def pending_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación pendiente."""
    data = base_vacation_data.copy()
    data.update({
        "status": VacationStatus.PENDING,
        "approved_date": None,
        "approved_by": None
    })
    return data


@pytest.fixture
def approved_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación aprobada."""
    data = base_vacation_data.copy()
    data.update({
        "status": VacationStatus.APPROVED,
        "approved_date": date(2024, 6, 15),
        "approved_by": "Manager Test"
    })
    return data


@pytest.fixture
def rejected_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación rechazada."""
    data = base_vacation_data.copy()
    data.update({
        "status": VacationStatus.REJECTED,
        "approved_date": date(2024, 6, 15),
        "approved_by": "Manager Test",
        "notes": "Rechazada por conflicto de fechas"
    })
    return data


# Fixtures para listas de vacaciones
@pytest.fixture
def multiple_vacations_data() -> List[Dict[str, Any]]:
    """Lista de datos para múltiples vacaciones."""
    return [
        {
            "employee_id": 1,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 15),
            "vacation_type": VacationType.ANNUAL,
            "status": VacationStatus.APPROVED,
            "requested_date": date(2024, 6, 1),
            "approved_date": date(2024, 6, 15),
            "approved_by": "Manager Test",
            "reason": "Vacaciones de verano",
            "total_days": 15,
            "business_days": 11
        },
        {
            "employee_id": 2,
            "start_date": date(2024, 8, 1),
            "end_date": date(2024, 8, 5),
            "vacation_type": VacationType.SICK,
            "status": VacationStatus.PENDING,
            "requested_date": date(2024, 7, 25),
            "reason": "Licencia médica",
            "total_days": 5,
            "business_days": 5
        },
        {
            "employee_id": 1,
            "start_date": date(2024, 12, 20),
            "end_date": date(2024, 12, 31),
            "vacation_type": VacationType.PERSONAL,
            "status": VacationStatus.PENDING,
            "requested_date": date(2024, 11, 1),
            "reason": "Vacaciones de fin de año",
            "total_days": 12,
            "business_days": 8
        }
    ]


@pytest.fixture
def vacation_instances_list(multiple_vacations_data: List[Dict[str, Any]]) -> List[Vacation]:
    """Lista de instancias de vacaciones para tests."""
    vacations = []
    for i, data in enumerate(multiple_vacations_data, 1):
        vacation = Vacation(**data)
        vacation.id = i
        vacation.created_at = datetime(2024, 6, 1, 10, 0, 0)
        vacation.updated_at = datetime(2024, 6, 1, 10, 0, 0)
        vacations.append(vacation)
    return vacations


# Fixtures para casos de error y validación
@pytest.fixture
def invalid_vacation_data() -> Dict[str, Any]:
    """Datos inválidos para tests de validación."""
    return {
        "employee_id": -1,  # ID inválido
        "start_date": date(2024, 7, 15),  # Fecha de inicio posterior a fecha de fin
        "end_date": date(2024, 7, 1),
        "vacation_type": "invalid_type",  # Tipo inválido
        "requested_date": date(2024, 8, 1),  # Fecha de solicitud posterior a inicio
        "total_days": -5,  # Días negativos
        "business_days": -3
    }


@pytest.fixture
def overlapping_vacation_data(base_vacation_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos para vacación que se solapa con otra existente."""
    data = base_vacation_data.copy()
    data.update({
        "start_date": date(2024, 7, 10),  # Se solapa con la vacación base
        "end_date": date(2024, 7, 20),
        "reason": "Vacación que se solapa"
    })
    return data


# Fixtures para filtros de búsqueda
@pytest.fixture
def vacation_search_filters() -> Dict[str, Any]:
    """Filtros de búsqueda para vacaciones."""
    return {
        "employee_id": 1,
        "status": VacationStatus.APPROVED,
        "vacation_type": VacationType.ANNUAL,
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 12, 31),
        "limit": 100,
        "offset": 0
    }


@pytest.fixture
def date_range_filter() -> Dict[str, Any]:
    """Filtro por rango de fechas."""
    return {
        "start_date": date(2024, 7, 1),
        "end_date": date(2024, 7, 31)
    }


# Fixtures para estadísticas y análisis
@pytest.fixture
def vacation_statistics_data() -> Dict[str, Any]:
    """Datos de estadísticas de vacaciones."""
    return {
        "total_vacations": 15,
        "approved_vacations": 12,
        "pending_vacations": 2,
        "rejected_vacations": 1,
        "total_days_taken": 180,
        "average_vacation_length": 12.0,
        "most_common_type": VacationType.ANNUAL.value,
        "busiest_month": "July"
    }


@pytest.fixture
def employee_vacation_summary() -> Dict[str, Any]:
    """Resumen de vacaciones por empleado."""
    return {
        "employee_id": 1,
        "total_vacations": 5,
        "total_days": 60,
        "days_by_type": {
            VacationType.ANNUAL.value: 45,
            VacationType.SICK.value: 10,
            VacationType.PERSONAL.value: 5
        },
        "remaining_days": 15,
        "next_vacation": date(2024, 12, 20)
    }


# Fixtures para mocks de módulos especializados
@pytest.fixture
def mock_crud_operations() -> AsyncMock:
    """Mock para operaciones CRUD."""
    return AsyncMock()


@pytest.fixture
def mock_query_operations() -> AsyncMock:
    """Mock para operaciones de consulta."""
    return AsyncMock()


@pytest.fixture
def mock_validation_operations() -> AsyncMock:
    """Mock para operaciones de validación."""
    return AsyncMock()


@pytest.fixture
def mock_statistics_operations() -> AsyncMock:
    """Mock para operaciones de estadísticas."""
    return AsyncMock()


@pytest.fixture
def mock_relationship_operations() -> AsyncMock:
    """Mock para operaciones de relaciones."""
    return AsyncMock()