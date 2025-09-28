# src/planificador/tests/unit/test_repositories/workload/test_workload_repository_facade.py

"""Tests para WorkloadRepositoryFacade."""

import pytest
from unittest.mock import MagicMock, AsyncMock, patch
from datetime import date, datetime
from typing import List, Optional
import pendulum
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import IntegrityError, NoResultFound
from pydantic import ValidationError

from planificador.repositories.workload.workload_repository_facade import (
    WorkloadRepositoryFacade,
)
from planificador.repositories.workload.interfaces.crud_interface import (
    IWorkloadCrudOperations,
)
from planificador.repositories.workload.interfaces.query_interface import (
    IWorkloadQueryOperations,
)
from planificador.repositories.workload.interfaces.relationship_interface import (
    IWorkloadRelationshipOperations,
)
from planificador.repositories.workload.interfaces.statistics_interface import (
    IWorkloadStatisticsOperations,
)
from planificador.repositories.workload.interfaces.validation_interface import (
    IWorkloadValidationOperations,
)
from planificador.schemas.workload.workload import WorkloadCreate, WorkloadUpdate
from planificador.models.workload import Workload
from planificador.config.config import get_settings
from planificador.exceptions.infrastructure import (
    DatabaseError,
    DatabaseConnectionError,
    DatabaseIntegrityError,
    DatabaseTimeoutError,
)
from planificador.exceptions.repository.workload_repository_exceptions import (
    WorkloadNotFoundError,
    WorkloadRepositoryError,
)
from planificador.exceptions.repository.base_repository_exceptions import (
    RepositoryIntegrityError,
)


from .fixtures import db_session, sample_workload_data


@pytest.fixture
def mock_crud_module():
    """Mock para WorkloadCrudModule con todos los métodos necesarios."""
    mock = MagicMock()
    # Configurar métodos async como AsyncMock
    mock.create_workload = AsyncMock()
    mock.get_workload_by_id = AsyncMock()
    mock.update_workload = AsyncMock()
    mock.delete_workload = AsyncMock()
    mock.get_all_workloads = AsyncMock()
    mock.exists_by_id = AsyncMock()
    mock.count_all = AsyncMock()
    return mock


@pytest.fixture
def mock_query_module():
    """Mock para WorkloadQueryModule con todos los métodos necesarios."""
    mock = MagicMock()
    # Configurar todos los métodos async de la interfaz
    mock.get_by_employee = AsyncMock()
    mock.get_by_employee_and_date = AsyncMock()
    mock.get_by_employee_date_range = AsyncMock()
    mock.get_by_project_and_date = AsyncMock()
    mock.get_by_date_range = AsyncMock()
    mock.get_by_project = AsyncMock()
    mock.get_by_project_date_range = AsyncMock()
    mock.get_overloaded_employees = AsyncMock()
    mock.get_underutilized_employees = AsyncMock()
    mock.get_with_relations = AsyncMock()
    mock.get_team_workload = AsyncMock()
    mock.get_workloads_by_employee = AsyncMock()
    mock.get_workloads_by_date_range = AsyncMock()
    mock.get_workloads_by_project = AsyncMock()
    mock.get_overloaded_employees_summary = AsyncMock()
    mock.get_underutilized_employees_summary = AsyncMock()
    mock.get_team_workloads = AsyncMock()
    mock.get_team_workload_summary = AsyncMock()
    mock.get_weekly_workload = AsyncMock()
    return mock


@pytest.fixture
def mock_validation_module():
    """Mock para WorkloadValidationModule con todos los métodos necesarios."""
    mock = MagicMock()
    # Configurar métodos async comunes de validación
    mock.validate_create_data = AsyncMock()
    mock.validate_update_data = AsyncMock()
    mock.validate_date_range = AsyncMock()
    mock.validate_threshold_hours = AsyncMock()
    mock.validate_team_id = AsyncMock()
    mock.validate_workload_id = AsyncMock()
    mock.check_employee_project_consistency = AsyncMock()
    return mock


@pytest.fixture
def mock_relationship_module():
    """Mock para WorkloadRelationshipModule con todos los métodos necesarios."""
    mock = MagicMock()
    # Configurar métodos async de relaciones
    mock.get_employee_workloads = AsyncMock()
    mock.get_employee_projects = AsyncMock()
    mock.get_project_employees = AsyncMock()
    mock.get_related_workloads = AsyncMock()
    return mock


@pytest.fixture
def mock_statistics_module():
    """Mock para WorkloadStatisticsModule con todos los métodos necesarios."""
    mock = MagicMock()
    # Configurar métodos async de estadísticas
    mock.get_employee_total_hours = AsyncMock()
    mock.get_project_total_hours = AsyncMock()
    mock.get_average_daily_hours = AsyncMock()
    mock.get_workload_distribution = AsyncMock()
    mock.get_employee_workload_distribution = AsyncMock()
    mock.get_project_employee_distribution = AsyncMock()
    mock.get_team_average_hours = AsyncMock()
    mock.get_team_workload_distribution = AsyncMock()
    mock.get_workload_trends = AsyncMock()
    mock.get_capacity_utilization = AsyncMock()
    mock.get_peak_workload_periods = AsyncMock()
    return mock


@pytest.fixture
def workload_repository_facade(
    mock_crud_module,
    mock_query_module,
    mock_validation_module,
    mock_relationship_module,
    mock_statistics_module,
):
    with patch(
        "planificador.repositories.workload.workload_repository_facade.WorkloadCrudModule",
        return_value=mock_crud_module,
    ), patch(
        "planificador.repositories.workload.workload_repository_facade.WorkloadQueryModule",
        return_value=mock_query_module,
    ), patch(
        "planificador.repositories.workload.workload_repository_facade.WorkloadValidationModule",
        return_value=mock_validation_module,
    ), patch(
        "planificador.repositories.workload.workload_repository_facade.WorkloadRelationshipModule",
        return_value=mock_relationship_module,
    ), patch(
        "planificador.repositories.workload.workload_repository_facade.WorkloadStatisticsModule",
        return_value=mock_statistics_module,
    ):
        session = AsyncMock(spec=AsyncSession)
        return ConcreteWorkloadRepositoryFacade(session)


# Concrete implementation for testing
class ConcreteWorkloadRepositoryFacade(WorkloadRepositoryFacade):
    async def create(self, workload: WorkloadCreate):
        return await self.crud_module.create_workload(workload)

    async def get_workload_by_id(self, workload_id: int):
        return await self.crud_module.get_workload_by_id(workload_id)

    async def update(self, workload_id: int, workload: WorkloadUpdate):
        return await self.crud_module.update_workload(workload_id, workload)

    async def delete(self, workload_id: int):
        return await self.crud_module.delete_workload(workload_id)

    async def get_all_workloads(self):
        return await self.crud_module.get_all_workloads()

    async def get_by_employee(self, employee_id: int):
        return await self.query_module.get_workloads_by_employee(employee_id)

    async def get_by_project(self, project_id: int):
        return await self.query_module.get_workloads_by_project(project_id)

    async def get_by_date_range(self, start_date, end_date):
        return await self.query_module.get_workloads_by_date_range(
            start_date, end_date
        )

    async def validate_create_data(self, data: dict):
        return await self.validation_module.validate_create_data(data)

    async def validate_update_data(self, data: dict, workload_id=None):
        return await self.validation_module.validate_update_data(data, workload_id)

    async def validate_date_range(self, start_date, end_date):
        return await self.validation_module.validate_date_range(start_date, end_date)

    async def get_employee_workloads(
        self, employee_id: int, start_date=None, end_date=None
    ):
        return await self.relationship_module.get_employee_workloads(
            employee_id, start_date, end_date
        )

    async def get_employee_projects(
        self, employee_id: int, start_date=None, end_date=None
    ):
        return await self.relationship_module.get_employee_projects(
            employee_id, start_date, end_date
        )

    async def get_project_workloads(
        self, project_id: int, start_date=None, end_date=None
    ):
        return await self.relationship_module.get_project_workloads(
            project_id, start_date, end_date
        )

    async def get_project_employees(
        self, project_id: int, start_date=None, end_date=None
    ):
        return await self.relationship_module.get_project_employees(
            project_id, start_date, end_date
        )

    async def get_team_workloads(self, team_id: int, start_date=None, end_date=None):
        return await self.relationship_module.get_team_workloads(
            team_id, start_date, end_date
        )

    async def get_team_projects(self, team_id: int, start_date=None, end_date=None):
        return await self.relationship_module.get_team_projects(
            team_id, start_date, end_date
        )

    async def get_employee_total_hours(self, employee_id: int, start_date, end_date):
        return await self.statistics_module.get_employee_total_hours(
            employee_id, start_date, end_date
        )

    async def get_project_total_hours(self, project_id: int, start_date, end_date):
        return await self.statistics_module.get_project_total_hours(
            project_id, start_date, end_date
        )

    async def get_team_total_hours(self, team_id: int, start_date, end_date):
        return await self.statistics_module.get_team_total_hours(
            team_id, start_date, end_date
        )

    async def get_team_workload(self, team_id: int, start_date, end_date):
        return await self.query_module.get_team_workload(team_id, start_date, end_date)

    async def get_paginated_workloads(self, page: int, page_size: int):
        return await self.query_module.get_paginated_workloads(page, page_size)

    async def get_active_workloads(self):
        return await self.query_module.get_active_workloads()

    async def get_completed_workloads(self):
        return await self.query_module.get_completed_workloads()

    async def get_workloads_by_status(self, status: str):
        return await self.query_module.get_workloads_by_status(status)

    async def get_workloads_by_priority_and_status(self, priority: str, status: str):
        return await self.query_module.get_workloads_by_priority_and_status(
            priority, status
        )

    async def get_workloads_with_notes_containing(self, keyword: str):
        return await self.query_module.get_workloads_with_notes_containing(keyword)

    async def get_workloads_by_creation_date(self, date):
        return await self.query_module.get_workloads_by_creation_date(date)

    async def get_workloads_by_update_date(self, date):
        return await self.query_module.get_workloads_by_update_date(date)

    async def get_workloads_with_dependencies(self):
        return await self.relationship_module.get_workloads_with_dependencies()

    async def get_workloads_without_dependencies(self):
        return await self.relationship_module.get_workloads_without_dependencies()

    async def get_workloads_with_planned_hours_in_range(
        self, min_hours: float, max_hours: float
    ):
        return await self.query_module.get_workloads_with_planned_hours_in_range(
            min_hours, max_hours
        )

    async def get_overloaded_employees(
        self, threshold_hours: float, start_date, end_date
    ):
        return await self.statistics_module.get_overloaded_employees(
            threshold_hours, start_date, end_date
        )

    async def get_underutilized_employees(
        self, threshold_hours: float, start_date, end_date
    ):
        return await self.statistics_module.get_underutilized_employees(
            threshold_hours, start_date, end_date
        )

    async def get_employee_workload_for_date(self, employee_id: int, date):
        return await self.query_module.get_employee_workload_for_date(employee_id, date)

    async def get_project_workload_for_date(self, project_id: int, date):
        return await self.query_module.get_project_workload_for_date(project_id, date)

    async def find_workloads_by_criteria(self, criteria: dict):
        return await self.query_module.find_workloads_by_criteria(criteria)

    async def get_workloads_by_employee_and_project(
        self, employee_id: int, project_id: int
    ):
        return await self.query_module.get_workloads_by_employee_and_project(
            employee_id, project_id
        )

    async def get_workloads_with_high_priority(self):
        return await self.query_module.get_workloads_with_high_priority()

    async def get_recent_workloads(self, days: int):
        return await self.query_module.get_recent_workloads(days)

    async def validate_employee_project_assignment(
        self, employee_id: int, project_id: int
    ):
        return await self.validation_module.validate_employee_project_assignment(
            employee_id, project_id
        )

    async def check_workload_conflicts(
        self, employee_id: int, workload_date, hours: float, exclude_workload_id=None
    ):
        return await self.validation_module.check_workload_conflicts(
            employee_id, workload_date, hours, exclude_workload_id
        )

    async def get_cross_project_employees(self, start_date, end_date):
        return await self.relationship_module.get_cross_project_employees(
            start_date, end_date
        )

    async def get_project_dependencies(self, project_id: int):
        return await self.relationship_module.get_project_dependencies(project_id)

    async def get_employee_average_hours(self, employee_id: int, start_date, end_date):
        return await self.statistics_module.get_employee_average_hours(
            employee_id, start_date, end_date
        )

    async def get_employee_workload_distribution(
        self, employee_id: int, start_date, end_date
    ):
        return await self.statistics_module.get_employee_workload_distribution(
            employee_id, start_date, end_date
        )

    async def get_project_employee_distribution(
        self, project_id: int, start_date, end_date
    ):
        return await self.statistics_module.get_project_employee_distribution(
            project_id, start_date, end_date
        )

    async def get_team_average_hours(self, team_id: int, start_date, end_date):
        return await self.statistics_module.get_team_average_hours(
            team_id, start_date, end_date
        )

    async def get_team_workload_distribution(self, team_id: int, start_date, end_date):
        return await self.statistics_module.get_team_workload_distribution(
            team_id, start_date, end_date
        )

    async def get_workload_trends(self, start_date, end_date, granularity="daily"):
        return await self.statistics_module.get_workload_trends(
            start_date, end_date, granularity
        )

    async def get_capacity_utilization(self, team_id: int, start_date, end_date):
        return await self.statistics_module.get_capacity_utilization(
            team_id, start_date, end_date
        )

    async def get_peak_workload_periods(self, team_id: int, start_date, end_date):
        return await self.statistics_module.get_peak_workload_periods(
            team_id, start_date, end_date
        )

    async def validate_threshold_hours(self, threshold_hours: float):
        return await self.validation_module.validate_threshold_hours(threshold_hours)

    async def validate_team_id(self, team_id: int):
        return await self.validation_module.validate_team_id(team_id)

    async def validate_workload_id(self, workload_id: int):
        return await self.validation_module.validate_workload_id(workload_id)

    async def check_employee_project_consistency(
        self, workload_id: int, employee_id: int, project_id: int
    ):
        return await self.validation_module.check_employee_project_consistency(
            workload_id, employee_id, project_id
        )

    # Métodos faltantes de IWorkloadQueryOperations
    async def get_by_employee_and_date(self, employee_id: int, workload_date):
        return await self.query_module.get_by_employee_and_date(employee_id, workload_date)

    async def get_by_employee_date_range(self, employee_id: int, start_date, end_date):
        return await self.query_module.get_by_employee_date_range(employee_id, start_date, end_date)

    async def get_by_project_and_date(self, project_id: int, workload_date):
        return await self.query_module.get_by_project_and_date(project_id, workload_date)

    async def get_by_project_date_range(self, project_id: int, start_date, end_date):
        return await self.query_module.get_by_project_date_range(project_id, start_date, end_date)

    async def get_overloaded_employees(self, target_date, threshold_hours: float = 8.0):
        return await self.query_module.get_overloaded_employees(target_date, threshold_hours)

    async def get_underutilized_employees(self, target_date, threshold_hours: float = 4.0):
        return await self.query_module.get_underutilized_employees(target_date, threshold_hours)

    async def get_with_relations(self, workload_id: int):
        return await self.query_module.get_with_relations(workload_id)

    async def get_workloads_by_employee(self, employee_id: int, start_date=None, end_date=None):
        return await self.query_module.get_workloads_by_employee(employee_id, start_date, end_date)

    async def get_workloads_by_date_range(self, start_date, end_date):
        return await self.query_module.get_workloads_by_date_range(start_date, end_date)

    async def get_workloads_by_project(self, project_id: int, start_date=None, end_date=None):
        return await self.query_module.get_workloads_by_project(project_id, start_date, end_date)

    async def get_overloaded_employees_summary(self, target_date, threshold_hours: float = 8.0):
        return await self.query_module.get_overloaded_employees_summary(target_date, threshold_hours)

    async def get_underutilized_employees_summary(self, target_date, threshold_hours: float = 4.0):
        return await self.query_module.get_underutilized_employees_summary(target_date, threshold_hours)

    async def get_team_workloads(self, team_id: int, start_date, end_date):
        return await self.query_module.get_team_workloads(team_id, start_date, end_date)

    async def get_team_workload_summary(self, team_id: int, target_date):
        return await self.query_module.get_team_workload_summary(team_id, target_date)

    async def get_weekly_workload(self, employee_id: int, week_start):
        return await self.query_module.get_weekly_workload(employee_id, week_start)

    # Métodos faltantes de IWorkloadCrudOperations
    async def create_workload(self, workload_data):
        return await self.crud_module.create_workload(workload_data)

    async def get_workload_by_id(self, workload_id: int):
        return await self.crud_module.get_workload_by_id(workload_id)

    async def update_workload(self, workload_id: int, workload_data):
        return await self.crud_module.update_workload(workload_id, workload_data)

    async def delete_workload(self, workload_id: int):
        return await self.crud_module.delete_workload(workload_id)

    async def get_all_workloads(self):
        return await self.crud_module.get_all_workloads()

    async def exists_by_id(self, workload_id: int):
        return await self.crud_module.exists_by_id(workload_id)

    async def count_all(self):
        return await self.crud_module.count_all()

    # Métodos faltantes de IWorkloadValidationOperations
    async def validate_employee_project_assignment(self, employee_id: int, project_id: int):
        return await self.validation_module.validate_employee_project_assignment(employee_id, project_id)

    # Métodos faltantes de IWorkloadRelationshipOperations
    async def get_workloads_with_dependencies(self):
        return await self.relationship_module.get_workloads_with_dependencies()

    async def get_workloads_without_dependencies(self):
        return await self.relationship_module.get_workloads_without_dependencies()

    # Métodos faltantes de IWorkloadStatisticsOperations
    async def get_overloaded_employees(self, threshold_hours: float, start_date, end_date):
        return await self.statistics_module.get_overloaded_employees(threshold_hours, start_date, end_date)

    async def get_underutilized_employees(self, threshold_hours: float, start_date, end_date):
        return await self.statistics_module.get_underutilized_employees(threshold_hours, start_date, end_date)

@pytest.fixture
def sample_workload_data():
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": pendulum.now().date(),
        "actual_hours": 8.0,
        "notes": "Test notes",
    }


@pytest.fixture
def workload_repository_facade_direct(
    db_session: AsyncSession,
) -> ConcreteWorkloadRepositoryFacade:
    """Fixture para inyectar un mock de WorkloadRepositoryFacade."""
    return ConcreteWorkloadRepositoryFacade(session=db_session)


@pytest.mark.asyncio
class TestWorkloadCrudOperations:
    async def test_create_workload_success(self, workload_repository_facade, mock_crud_module):
        workload_data = WorkloadCreate(
            employee_id=1,
            project_id=1,
            actual_hours=8,
            date="2023-10-27",
            week_number=43,
            month=10,
            year=2023,
            notes="Test workload",
        )
        mock_crud_module.create_workload.return_value = Workload(**workload_data.model_dump(), id=1)

        result = await workload_repository_facade.create(workload_data)

        mock_crud_module.create_workload.assert_called_once_with(workload_data)
        assert result.id is not None
        assert result.employee_id == workload_data.employee_id

    async def test_create_workload_sqlalchemy_error(self, workload_repository_facade, mock_crud_module):
        workload_data = WorkloadCreate(
            employee_id=1,
            project_id=1,
            actual_hours=8,
            date="2023-10-27",
            week_number=43,
            month=10,
            year=2023,
            notes="Test workload",
        )
        mock_crud_module.create_workload.side_effect = RepositoryIntegrityError(
            "DB integrity error"
        )

        with pytest.raises(RepositoryIntegrityError):
            await workload_repository_facade.create(workload_data)

    async def test_get_workload_by_id_success(self, workload_repository_facade, mock_crud_module):
        mock_crud_module.get_workload_by_id.return_value = Workload(
            id=1,
            employee_id=1,
            project_id=1,
            actual_hours=8,
            date="2023-10-27",
            notes="Test workload",
            week_number=43,
            month=10,
            year=2023,
        )

        result = await workload_repository_facade.get_workload_by_id(1)

        mock_crud_module.get_workload_by_id.assert_called_once_with(1)
        assert result.id == 1

    async def test_get_workload_by_id_not_found(self, workload_repository_facade, mock_crud_module):
        mock_crud_module.get_workload_by_id.side_effect = WorkloadNotFoundError(
            message="Workload not found",
            workload_id=999
        )

        with pytest.raises(WorkloadNotFoundError):
            await workload_repository_facade.get_workload_by_id(999)

    async def test_get_all_workloads_success(self, workload_repository_facade, mock_crud_module):
        mock_crud_module.get_all_workloads.return_value = [
            Workload(id=1, employee_id=1, project_id=1, actual_hours=8, date="2023-10-27", notes="Test", week_number=43, month=10, year=2023),
            Workload(id=2, employee_id=2, project_id=1, actual_hours=4, date="2023-10-27", notes="Test 2", week_number=43, month=10, year=2023),
        ]

        result = await workload_repository_facade.get_all_workloads()

        mock_crud_module.get_all_workloads.assert_called_once()
        assert len(result) == 2

    async def test_update_workload_success(self, workload_repository_facade, mock_crud_module):
        update_data = WorkloadUpdate(actual_hours=10)
        mock_crud_module.update_workload.return_value = Workload(
            id=1,
            employee_id=1,
            project_id=1,
            actual_hours=10,
            date="2023-10-27",
            notes="Updated workload",
            week_number=43,
            month=10,
            year=2023,
        )

        result = await workload_repository_facade.update(1, update_data)

        mock_crud_module.update_workload.assert_called_once_with(1, update_data)
        assert result.actual_hours == 10

    async def test_update_workload_not_found(self, workload_repository_facade, mock_crud_module):
        update_data = WorkloadUpdate(actual_hours=10)
        mock_crud_module.update_workload.side_effect = WorkloadNotFoundError(
            message="Workload not found",
            workload_id=999
        )

        with pytest.raises(WorkloadNotFoundError):
            await workload_repository_facade.update(999, update_data)

    async def test_delete_workload_success(self, workload_repository_facade, mock_crud_module):
        mock_crud_module.delete_workload.return_value = None

        await workload_repository_facade.delete(1)

        mock_crud_module.delete_workload.assert_called_once_with(1)

    async def test_delete_workload_not_found(self, workload_repository_facade, mock_crud_module):
        mock_crud_module.delete_workload.side_effect = WorkloadNotFoundError(
            message="Workload not found",
            workload_id=999
        )

        with pytest.raises(WorkloadNotFoundError):
            await workload_repository_facade.delete(999)


@pytest.mark.asyncio
async def test_create_workload_invalid_data(workload_repository_facade, mock_crud_module):
    """
    Test that creating a workload with invalid data raises ValidationError.
    """
    invalid_data = {
        "employee_id": 1,
        "project_id": 1,
        "date": "2023-10-26",
        "planned_hours": -10,  # Invalid
        "notes": "Invalid hours",
    }
    with pytest.raises(ValidationError):
        WorkloadCreate(**invalid_data)


@pytest.mark.asyncio
async def test_update_workload_invalid_data():
    """
    Test that updating a workload with invalid data raises ValidationError.
    """
    invalid_data = {"planned_hours": -5}  # Invalid
    with pytest.raises(ValidationError):
        WorkloadUpdate(**invalid_data)


@pytest.mark.asyncio
class TestWorkloadQueryOperations:
    async def test_get_workloads_by_employee_success(
        self, workload_repository_facade, mock_query_module
    ):
        mock_query_module.get_workloads_by_employee.return_value = [
            Workload(id=1, employee_id=1, project_id=1, actual_hours=8, date="2023-10-27", notes="Test", week_number=43, month=10, year=2023)
        ]

        result = await workload_repository_facade.get_by_employee(1)

        mock_query_module.get_workloads_by_employee.assert_called_once_with(1)
        assert len(result) == 1

    async def test_get_workloads_by_employee_not_found(
        self, workload_repository_facade, mock_query_module
    ):
        mock_query_module.get_workloads_by_employee.return_value = []

        result = await workload_repository_facade.get_by_employee(999)

        mock_query_module.get_workloads_by_employee.assert_called_once_with(999)
        assert result == []

    async def test_get_workloads_by_project_success(
        self, workload_repository_facade, mock_query_module
    ):
        mock_query_module.get_workloads_by_project.return_value = [
            Workload(id=1, employee_id=1, project_id=1, actual_hours=8, date="2023-10-27", notes="Test", week_number=43, month=10, year=2023)
        ]

        result = await workload_repository_facade.get_by_project(1)

        mock_query_module.get_workloads_by_project.assert_called_once_with(1)
        assert len(result) == 1

    async def test_get_workloads_by_date_range_success(
        self, workload_repository_facade, mock_query_module
    ):
        start_date = pendulum.now().subtract(days=7).date()
        end_date = pendulum.now().date()
        mock_query_module.get_workloads_by_date_range.return_value = [
            Workload(id=1, employee_id=1, project_id=1, actual_hours=8, date="2023-10-27", notes="Test", week_number=43, month=10, year=2023)
        ]

        result = await workload_repository_facade.get_by_date_range(start_date, end_date)

        mock_query_module.get_workloads_by_date_range.assert_called_once_with(
            start_date, end_date
        )
        assert len(result) == 1


@pytest.mark.asyncio
class TestWorkloadValidationOperations:
    async def test_validate_create_data_success(
        self, workload_repository_facade, mock_validation_module
    ):
        valid_data = {
            "employee_id": 1, 
            "project_id": 1, 
            "actual_hours": 8,
            "date": date(2023, 10, 27),
            "week_number": 43,
            "month": 10,
            "year": 2023
        }
        mock_validation_module.validate_create_data.return_value = WorkloadCreate(
            **valid_data
        )

        result = await workload_repository_facade.validate_create_data(valid_data)

        mock_validation_module.validate_create_data.assert_called_once_with(
            valid_data
        )
        assert isinstance(result, WorkloadCreate)

    async def test_validate_create_data_invalid(
        self, workload_repository_facade, mock_validation_module
    ):
        invalid_data = {"employee_id": 1}
        mock_validation_module.validate_create_data.side_effect = ValidationError.from_exception_data(
            title="error", line_errors=[]
        )

        with pytest.raises(ValidationError):
            await workload_repository_facade.validate_create_data(invalid_data)

    async def test_validate_date_range_success(
        self, workload_repository_facade, mock_validation_module
    ):
        start_date = pendulum.now().subtract(days=1).date()
        end_date = pendulum.now().date()
        mock_validation_module.validate_date_range.return_value = None

        await workload_repository_facade.validate_date_range(start_date, end_date)

        mock_validation_module.validate_date_range.assert_called_once_with(
            start_date, end_date
        )

    async def test_validate_date_range_invalid(
        self, workload_repository_facade, mock_validation_module
    ):
        start_date = pendulum.now().date()
        end_date = pendulum.now().subtract(days=1).date()
        mock_validation_module.validate_date_range.side_effect = ValueError

        with pytest.raises(ValueError):
            await workload_repository_facade.validate_date_range(start_date, end_date)


@pytest.mark.asyncio
class TestWorkloadRelationshipOperations:
    async def test_get_employee_workloads_success(
        self, workload_repository_facade, mock_relationship_module
    ):
        mock_relationship_module.get_employee_workloads.return_value = [
            Workload(id=1, employee_id=1, project_id=1, actual_hours=8, date="2023-10-27", notes="Test", week_number=43, month=10, year=2023)
        ]

        result = await workload_repository_facade.get_employee_workloads(1)

        mock_relationship_module.get_employee_workloads.assert_called_once_with(
            1, None, None
        )
        assert len(result) == 1

    async def test_get_project_employees_success(
        self, workload_repository_facade, mock_relationship_module
    ):
        mock_relationship_module.get_project_employees.return_value = [MagicMock()]

        result = await workload_repository_facade.get_project_employees(1)

        mock_relationship_module.get_project_employees.assert_called_once_with(
            1, None, None
        )
        assert len(result) == 1


@pytest.mark.asyncio
class TestWorkloadStatisticsOperations:
    async def test_get_employee_total_hours_success(
        self, workload_repository_facade, mock_statistics_module
    ):
        start_date = pendulum.now().subtract(days=7).date()
        end_date = pendulum.now().date()
        mock_statistics_module.get_employee_total_hours.return_value = 40.0

        result = await workload_repository_facade.get_employee_total_hours(
            1, start_date, end_date
        )

        mock_statistics_module.get_employee_total_hours.assert_called_once_with(
            1, start_date, end_date
        )
        assert result == 40.0

    async def test_get_project_total_hours_success(
        self, workload_repository_facade, mock_statistics_module
    ):
        start_date = pendulum.now().subtract(days=30).date()
        end_date = pendulum.now().date()
        mock_statistics_module.get_project_total_hours.return_value = 200.0

        result = await workload_repository_facade.get_project_total_hours(
            1, start_date, end_date
        )

        mock_statistics_module.get_project_total_hours.assert_called_once_with(
            1, start_date, end_date
        )
        assert result == 200.0