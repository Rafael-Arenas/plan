"""
Configuración y fixtures para tests de los servicios de dominio de project assignment.

Este módulo proporciona fixtures reutilizables para las pruebas unitarias
de los servicios de dominio de asignaciones de proyecto, incluyendo mocks
de dependencias y datos de prueba.
"""

import pytest
import pendulum
from typing import Generator, Dict, Any, List
from unittest.mock import AsyncMock, MagicMock, Mock
from uuid import UUID

from sqlalchemy.ext.asyncio import AsyncSession
from planificador.repositories.project_assignment.project_assignment_repository_facade import ProjectAssignmentRepositoryFacade

from planificador.schemas.assignment.assignment import (
    ProjectAssignment, ProjectAssignmentCreate, ProjectAssignmentUpdate
)
from planificador.schemas.assignment.advanced_schemas import (
    ProjectTeamSummarySchema, ProjectResourceAllocationSchema,
    ProjectTimelineSchema, AssignmentAdvancedFilters,
    EmployeeWorkloadSummarySchema, EmployeeAllocationSummarySchema,
    AssignmentDurationAnalyticsSchema, WorkloadDistributionAnalyticsSchema
)
from planificador.models.project_assignment import ProjectAssignment as ProjectAssignmentModel


@pytest.fixture
def mock_session() -> AsyncMock:
    """
    Fixture que mockea una sesión de base de datos asíncrona.
    
    Returns:
        AsyncMock: Mock de AsyncSession
    """
    return AsyncMock(spec=AsyncSession)


@pytest.fixture
def mock_repository_facade():
    """Mock del ProjectAssignmentRepositoryFacade con todos los métodos necesarios."""
    mock = Mock(spec=ProjectAssignmentRepositoryFacade)
    
    # Configurar métodos como AsyncMock con return_value
    mock.get_assignments_by_project = AsyncMock(return_value=[])
    mock.project_exists = AsyncMock(return_value=True)
    mock.get_project_basic_info = AsyncMock(return_value={"name": "Test Project"})
    mock.get_employee_basic_info = AsyncMock(return_value={"name": "Test Employee"})
    mock.get_project_team_summary = AsyncMock(return_value={
        "project_id": 1,
        "total_members": 5,
        "team_composition": [{"employee_id": 1, "role": "Developer"}]
    })
    mock.get_all_assignments = AsyncMock(return_value=[])
    mock.get_assignments_by_employee = AsyncMock(return_value=[])
    mock.get_assignments_by_date_range = AsyncMock(return_value=[])
    mock.get_assignment_by_id = AsyncMock(return_value=None)
    mock.get_project_by_id = AsyncMock(return_value=None)
    
    # Agregar el atributo queries que necesita SearchOperations
    mock.queries = Mock()
    mock.queries.get_all_assignments = AsyncMock(return_value=[])
    mock.queries.get_employee_basic_info = AsyncMock(return_value={"name": "Test Employee"})
    mock.queries.get_project_basic_info = AsyncMock(return_value={"name": "Test Project"})
    mock.queries.get_assignments_by_employee = AsyncMock(return_value=[])
    mock.queries.get_assignments_by_project = AsyncMock(return_value=[])
    
    return mock


@pytest.fixture
def sample_assignment_id() -> int:
    """
    Fixture que proporciona un ID de asignación de ejemplo.
    
    Returns:
        int: ID de asignación de ejemplo
    """
    return 1


@pytest.fixture
def sample_project_id() -> int:
    """
    Fixture que proporciona un ID de proyecto de ejemplo.
    
    Returns:
        int: ID de proyecto de ejemplo
    """
    return 1


@pytest.fixture
def sample_employee_id() -> int:
    """
    Fixture que proporciona un ID de empleado de ejemplo.
    
    Returns:
        int: ID de empleado de ejemplo
    """
    return 1


@pytest.fixture
def sample_assignment_create_data(
    sample_project_id: int,
    sample_employee_id: int
) -> ProjectAssignmentCreate:
    """
    Fixture que proporciona datos válidos para crear una asignación.
    
    Returns:
        ProjectAssignmentCreate: Datos de creación de asignación
    """
    return ProjectAssignmentCreate(
        project_id=sample_project_id,
        employee_id=sample_employee_id,
        start_date=pendulum.now().date(),
        end_date=pendulum.now().add(months=3).date(),
        percentage_allocation=80.0,
        allocated_hours_per_day=6.4,
        role_in_project="Developer",
        notes="Asignación de prueba"
    )


@pytest.fixture
def sample_assignment_response(
    sample_assignment_id: int,
    sample_project_id: int,
    sample_employee_id: int
) -> ProjectAssignment:
    """
    Fixture que proporciona una respuesta de asignación válida.
    
    Returns:
        ProjectAssignment: Respuesta de asignación
    """
    return ProjectAssignment(
        id=sample_assignment_id,
        project_id=sample_project_id,
        employee_id=sample_employee_id,
        start_date=pendulum.now().date(),
        end_date=pendulum.now().add(months=3).date(),
        percentage_allocation=80.0,
        allocated_hours_per_day=6.4,
        role_in_project="Developer",
        notes="Asignación de prueba",
        is_active=True,
        created_at=pendulum.now(),
        updated_at=pendulum.now()
    )


@pytest.fixture
def sample_assignment_list():
    """Lista de asignaciones de prueba."""
    from planificador.models.project_assignment import ProjectAssignment
    from datetime import date
    from decimal import Decimal
    import pendulum
    
    assignments = []
    
    # Asignación 1
    assignment1 = ProjectAssignment()
    assignment1.id = 1
    assignment1.employee_id = 1
    assignment1.project_id = 1
    assignment1.start_date = date(2024, 1, 1)
    assignment1.end_date = date(2024, 1, 31)
    assignment1.percentage_allocation = Decimal('80.0')
    assignment1.allocated_hours_per_day = Decimal('6.4')
    assignment1.role_in_project = "Developer"
    assignment1.is_active = True
    assignment1.notes = "Test assignment 1"
    assignment1.created_at = pendulum.now()
    assignment1.updated_at = pendulum.now()
    assignments.append(assignment1)
    
    # Asignación 2
    assignment2 = ProjectAssignment()
    assignment2.id = 2
    assignment2.employee_id = 2
    assignment2.project_id = 2
    assignment2.start_date = date(2024, 2, 1)
    assignment2.end_date = date(2024, 2, 28)
    assignment2.percentage_allocation = Decimal('50.0')
    assignment2.allocated_hours_per_day = Decimal('4.0')
    assignment2.role_in_project = "Tester"
    assignment2.is_active = True
    assignment2.notes = "Test assignment 2"
    assignment2.created_at = pendulum.now()
    assignment2.updated_at = pendulum.now()
    assignments.append(assignment2)
    
    # Asignación 3 - Para solapamiento
    assignment3 = ProjectAssignment()
    assignment3.id = 3
    assignment3.employee_id = 1
    assignment3.project_id = 2
    assignment3.start_date = date(2024, 1, 15)
    assignment3.end_date = date(2024, 2, 15)
    assignment3.percentage_allocation = Decimal('50.0')
    assignment3.allocated_hours_per_day = Decimal('4.0')
    assignment3.role_in_project = "Analyst"
    assignment3.is_active = True
    assignment3.notes = "Overlapping assignment"
    assignment3.created_at = pendulum.now()
    assignment3.updated_at = pendulum.now()
    assignments.append(assignment3)
    
    return assignments


@pytest.fixture
def sample_project_team_summary() -> ProjectTeamSummarySchema:
    """
    Fixture que proporciona un resumen de equipo de proyecto de ejemplo.
    
    Returns:
        ProjectTeamSummarySchema: Resumen de equipo
    """
    return ProjectTeamSummarySchema(
        project_id=1,
        project_name="Test Project",
        total_members=5,
        active_assignments=4,
        total_allocation=320.0,
        average_allocation=80.0,
        roles_distribution={"Developer": 3, "Designer": 1, "Manager": 1},
        team_members=[
            EmployeeWorkloadSummarySchema(
                employee_id=1,
                employee_name="John Doe",
                role="Developer",
                allocation_percentage=80.0,
                daily_hours=6.4,
                start_date=pendulum.now().date(),
                end_date=pendulum.now().add(months=3).date()
            )
        ]
    )


@pytest.fixture
def sample_advanced_filters() -> AssignmentAdvancedFilters:
    """
    Fixture que proporciona filtros avanzados de ejemplo.
    
    Returns:
        AssignmentAdvancedFilters: Filtros avanzados
    """
    return AssignmentAdvancedFilters(
        project_ids=[1, 2],
        employee_ids=[1, 2, 3],
        roles=["Developer", "Designer"],
        min_allocation=50.0,
        max_allocation=100.0,
        is_active=True,
        start_date_from=pendulum.now().date(),
        start_date_to=pendulum.now().add(months=6).date(),
        end_date_from=pendulum.now().add(months=1).date(),
        end_date_to=pendulum.now().add(months=12).date()
    )


@pytest.fixture
def sample_duration_analytics() -> AssignmentDurationAnalyticsSchema:
    """
    Fixture que proporciona analíticas de duración de ejemplo.
    
    Returns:
        AssignmentDurationAnalyticsSchema: Analíticas de duración
    """
    return AssignmentDurationAnalyticsSchema(
        total_assignments=100,
        average_duration_days=90.5,
        median_duration_days=85.0,
        min_duration_days=30,
        max_duration_days=365,
        duration_distribution={
            "short_term": 25,  # < 60 días
            "medium_term": 50,  # 60-180 días
            "long_term": 25   # > 180 días
        },
        role_duration_stats={
            "Developer": {"avg": 95.0, "median": 90.0},
            "Designer": {"avg": 75.0, "median": 70.0},
            "Manager": {"avg": 120.0, "median": 110.0}
        }
    )


@pytest.fixture
def sample_workload_distribution() -> WorkloadDistributionAnalyticsSchema:
    """
    Fixture que proporciona distribución de carga de trabajo de ejemplo.
    
    Returns:
        WorkloadDistributionAnalyticsSchema: Distribución de carga
    """
    return WorkloadDistributionAnalyticsSchema(
        total_employees=50,
        total_assignments=120,
        average_allocation=75.5,
        allocation_distribution={
            "underutilized": 10,  # < 60%
            "optimal": 30,        # 60-90%
            "overutilized": 10    # > 90%
        },
        role_workload_stats={
            "Developer": {
                "count": 30,
                "avg_allocation": 80.0,
                "total_hours": 1920.0
            },
            "Designer": {
                "count": 15,
                "avg_allocation": 70.0,
                "total_hours": 840.0
            }
        },
        department_distribution={
            "Engineering": 35,
            "Design": 15
        }
    )