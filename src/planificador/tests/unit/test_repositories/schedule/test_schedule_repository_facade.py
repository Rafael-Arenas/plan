# src/planificador/tests/unit/test_repositories/schedule/test_schedule_repository_facade.py
import pytest
from unittest.mock import AsyncMock
from datetime import date, time
from planificador.repositories.schedule.schedule_repository_facade import ScheduleRepositoryFacade
from planificador.tests.unit.test_repositories.schedule.fixtures import schedule_repository, mock_session
from planificador.exceptions.repository import (
    ScheduleRepositoryError,
    ScheduleQueryError
)


# =============================================================================
# TESTS PARA OPERACIONES CRUD
# =============================================================================

@pytest.mark.asyncio
async def test_create_schedule_delegates_to_crud_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método create_schedule delega la llamada a CrudModule."""
    # Mock para la operación subyacente
    schedule_repository.crud_module.create_schedule = AsyncMock()

    # Datos de prueba
    schedule_data = {
        "employee_id": 1,
        "project_id": 1,
        "schedule_date": date(2024, 1, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours": 8.0,
        "is_confirmed": False
    }

    # Llamada al método del facade
    await schedule_repository.create_schedule(schedule_data)

    # Verificación
    schedule_repository.crud_module.create_schedule.assert_awaited_once_with(schedule_data)


@pytest.mark.asyncio
async def test_update_schedule_delegates_to_crud_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método update_schedule delega la llamada a CrudModule."""
    # Mock para la operación subyacente
    schedule_repository.crud_module.update_schedule = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    update_data = {
        "hours": 7.5,
        "is_confirmed": True
    }
    
    # Llamada al método del facade
    await schedule_repository.update_schedule(schedule_id, update_data)
    
    # Verificación
    schedule_repository.crud_module.update_schedule.assert_awaited_once_with(schedule_id, update_data)


@pytest.mark.asyncio
async def test_delete_schedule_delegates_to_crud_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método delete_schedule delega la llamada a CrudModule."""
    # Mock para la operación subyacente
    schedule_repository.crud_module.delete_schedule = AsyncMock(return_value=True)
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    result = await schedule_repository.delete_schedule(schedule_id)
    
    # Verificación
    schedule_repository.crud_module.delete_schedule.assert_awaited_once_with(schedule_id)
    assert result is True


@pytest.mark.asyncio
async def test_create_schedule_with_validation_delegates_correctly(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que create_schedule_with_validation realiza validación y delegación correcta."""
    # Mocks para las operaciones subyacentes
    schedule_repository.validate_schedule_data = AsyncMock(
        return_value={'is_valid': True, 'errors': []}
    )
    schedule_repository.validate_schedule_conflicts = AsyncMock(return_value=[])
    schedule_repository.create_schedule = AsyncMock()
    
    # Datos de prueba con campos requeridos para validación
    schedule_data = {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 1, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours": 8.0,
        "is_confirmed": False
    }
    
    # Llamada al método del facade
    await schedule_repository.create_schedule_with_validation(schedule_data)
    
    # Verificaciones
    schedule_repository.validate_schedule_data.assert_awaited_once_with(schedule_data)
    schedule_repository.validate_schedule_conflicts.assert_awaited_once_with(
        schedule_data['employee_id'],
        schedule_data['start_date'],
        schedule_data['end_date'],
        schedule_data.get('start_time'),
        schedule_data.get('end_time')
    )
    schedule_repository.create_schedule.assert_awaited_once_with(schedule_data)


@pytest.mark.asyncio
async def test_update_schedule_with_validation_delegates_correctly(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que update_schedule_with_validation realiza validación y delegación correcta."""
    # Mock del horario actual
    current_schedule = {
        "id": 1,
        "employee_id": 1,
        "project_id": 1,
        "schedule_date": date(2024, 1, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours": 8.0,
        "is_confirmed": False
    }
    
    # Mocks para las operaciones subyacentes
    schedule_repository.get_schedule_by_id = AsyncMock(return_value=current_schedule)
    schedule_repository.validate_schedule_data = AsyncMock(
        return_value={'is_valid': True, 'errors': []}
    )
    schedule_repository.validate_schedule_conflicts = AsyncMock(return_value=[])
    schedule_repository.update_schedule = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    update_data = {
        "hours": 7.5,
        "is_confirmed": True
    }
    
    # Llamada al método del facade
    await schedule_repository.update_schedule_with_validation(schedule_id, update_data)
    
    # Verificaciones
    schedule_repository.get_schedule_by_id.assert_awaited_once_with(schedule_id)
    schedule_repository.update_schedule.assert_awaited_once_with(schedule_id, update_data)


@pytest.mark.asyncio
async def test_create_validated_schedule_delegates_to_create_schedule(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que create_validated_schedule delega la llamada a create_schedule."""
    # Mocks para las operaciones de validación
    schedule_repository.validate_schedule_data = AsyncMock(
        return_value={'is_valid': True, 'errors': []}
    )
    schedule_repository.validate_date_range = AsyncMock(
        return_value={'is_valid': True, 'errors': []}
    )
    schedule_repository.validate_schedule_conflicts = AsyncMock(return_value=[])
    schedule_repository.create_schedule = AsyncMock()
    
    # Datos de prueba con campos requeridos
    schedule_data = {
        "employee_id": 1,
        "project_id": 1,
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 1, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours": 8.0,
        "is_confirmed": False
    }
    
    # Llamada al método del facade
    await schedule_repository.create_validated_schedule(schedule_data)
    
    # Verificaciones
    schedule_repository.validate_schedule_data.assert_awaited_once_with(schedule_data)
    schedule_repository.validate_date_range.assert_awaited_once_with(
        schedule_data['start_date'],
        schedule_data['end_date']
    )
    schedule_repository.validate_schedule_conflicts.assert_awaited_once_with(
        schedule_data['employee_id'],
        schedule_data['start_date'],
        schedule_data['end_date'],
        schedule_data.get('start_time'),
        schedule_data.get('end_time')
    )
    schedule_repository.create_schedule.assert_awaited_once_with(schedule_data)


@pytest.mark.asyncio
async def test_get_complete_schedule_info_delegates_correctly(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que get_complete_schedule_info obtiene información completa del horario."""
    # Mock del horario básico
    basic_schedule = {
        "id": 1,
        "employee_id": 1,
        "start_date": date(2024, 1, 15),
        "end_date": date(2024, 1, 15)
    }
    
    # Mock del horario con detalles
    detailed_schedule = {
        "id": 1,
        "employee_id": 1,
        "project_name": "Proyecto Test",
        "team_name": "Equipo Test"
    }
    
    # Mocks para las operaciones subyacentes
    schedule_repository.get_schedule_by_id = AsyncMock(return_value=basic_schedule)
    schedule_repository.get_employee_schedules_with_details = AsyncMock(
        return_value=[detailed_schedule]
    )
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    result = await schedule_repository.get_complete_schedule_info(schedule_id)
    
    # Verificaciones
    schedule_repository.get_schedule_by_id.assert_awaited_once_with(schedule_id)
    schedule_repository.get_employee_schedules_with_details.assert_awaited_once()
    assert result == detailed_schedule


@pytest.mark.asyncio
async def test_bulk_schedule_operation_handles_create_operation(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que bulk_schedule_operation maneja correctamente la operación create."""
    # Mock para la operación subyacente
    schedule_repository.create_schedule_with_validation = AsyncMock(
        side_effect=lambda data: {"id": data.get("employee_id", 1), **data}
    )
    
    # Datos de prueba
    schedule_data_list = [
        {
            "employee_id": 1,
            "project_id": 1,
            "start_date": date(2024, 1, 15),
            "end_date": date(2024, 1, 15),
            "start_time": time(9, 0),
            "end_time": time(17, 0),
            "hours": 8.0
        },
        {
            "employee_id": 2,
            "project_id": 1,
            "start_date": date(2024, 1, 15),
            "end_date": date(2024, 1, 15),
            "start_time": time(10, 0),
            "end_time": time(17, 30),
            "hours": 7.5
        }
    ]
    
    # Llamada al método del facade
    results = await schedule_repository.bulk_schedule_operation("create", schedule_data_list)
    
    # Verificaciones
    assert len(results) == 2
    assert schedule_repository.create_schedule_with_validation.call_count == 2


@pytest.mark.asyncio
async def test_bulk_schedule_operation_handles_update_operation(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que bulk_schedule_operation maneja correctamente la operación update."""
    # Mock para la operación subyacente
    schedule_repository.update_schedule_with_validation = AsyncMock(
        side_effect=lambda schedule_id, data: {"id": schedule_id, **data}
    )
    
    # Datos de prueba
    schedule_data_list = [
        {
            "id": 1,
            "hours": 8.5,
            "is_confirmed": True
        },
        {
            "id": 2,
            "hours": 7.0,
            "is_confirmed": False
        }
    ]
    
    # Llamada al método del facade
    results = await schedule_repository.bulk_schedule_operation("update", schedule_data_list)
    
    # Verificaciones
    assert len(results) == 2
    assert schedule_repository.update_schedule_with_validation.call_count == 2


@pytest.mark.asyncio
async def test_bulk_schedule_operation_handles_delete_operation(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que bulk_schedule_operation maneja correctamente la operación delete."""
    # Mock para la operación subyacente
    schedule_repository.delete_schedule = AsyncMock(return_value=True)
    
    # Datos de prueba
    schedule_data_list = [
        {"id": 1},
        {"id": 2}
    ]
    
    # Llamada al método del facade
    results = await schedule_repository.bulk_schedule_operation("delete", schedule_data_list)
    
    # Verificaciones
    assert len(results) == 2
    assert all(result["success"] for result in results)
    assert schedule_repository.delete_schedule.call_count == 2


@pytest.mark.asyncio
async def test_get_employee_schedule_summary_delegates_correctly(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que get_employee_schedule_summary delega correctamente a los módulos correspondientes."""
    # Datos de prueba
    employee_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Mocks para los datos de retorno
    mock_schedules = [
        {"id": 1, "employee_id": 1, "project_name": "Proyecto A"},
        {"id": 2, "employee_id": 1, "project_name": "Proyecto B"}
    ]
    mock_hours_summary = {
        "total_hours": 160.0,
        "billable_hours": 120.0,
        "non_billable_hours": 40.0
    }
    mock_status_counts = {
        "active": 2,
        "completed": 0,
        "cancelled": 0
    }
    
    # Mocks para las operaciones subyacentes
    schedule_repository.get_employee_schedules_with_details = AsyncMock(
        return_value=mock_schedules
    )
    schedule_repository.get_employee_hours_summary = AsyncMock(
        return_value=mock_hours_summary
    )
    schedule_repository.get_schedule_counts_by_status = AsyncMock(
        return_value=mock_status_counts
    )
    
    # Llamada al método del facade
    result = await schedule_repository.get_employee_schedule_summary(
        employee_id, start_date, end_date
    )
    
    # Verificaciones de delegación
    schedule_repository.get_employee_schedules_with_details.assert_awaited_once_with(
        employee_id, start_date, end_date
    )
    schedule_repository.get_employee_hours_summary.assert_awaited_once_with(
        employee_id, start_date, end_date
    )
    schedule_repository.get_schedule_counts_by_status.assert_awaited_once_with(
        start_date, end_date, employee_id
    )
    
    # Verificaciones del resultado
    assert result["employee_id"] == employee_id
    assert result["period"]["start_date"] == start_date
    assert result["period"]["end_date"] == end_date
    assert result["schedules"] == mock_schedules
    assert result["hours_summary"] == mock_hours_summary
    assert result["status_counts"] == mock_status_counts
    assert result["total_schedules"] == len(mock_schedules)


# =============================================================================
# TESTS PARA OPERACIONES DE CONSULTA
# =============================================================================

@pytest.mark.asyncio
async def test_get_schedule_by_id_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_schedule_by_id delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_schedule_by_id = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_schedule_by_id(schedule_id)
    
    # Verificación
    schedule_repository.query_module.get_schedule_by_id.assert_awaited_once_with(schedule_id)


@pytest.mark.asyncio
async def test_get_schedules_by_employee_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_schedules_by_employee delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_schedules_by_employee = AsyncMock()
    
    # Datos de prueba
    employee_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_schedules_by_employee(employee_id, start_date, end_date)
    
    # Verificación
    schedule_repository.query_module.get_schedules_by_employee.assert_awaited_once_with(
        employee_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_schedules_by_date_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_schedules_by_date delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_schedules_by_date = AsyncMock()
    
    # Datos de prueba
    target_date = date(2024, 1, 15)
    employee_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_schedules_by_date(target_date, employee_id)
    
    # Verificación
    schedule_repository.query_module.get_schedules_by_date.assert_awaited_once_with(
        target_date, employee_id
    )


@pytest.mark.asyncio
async def test_get_schedules_by_project_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_schedules_by_project delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_schedules_by_project = AsyncMock()
    
    # Datos de prueba
    project_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_schedules_by_project(project_id, start_date, end_date)
    
    # Verificación
    schedule_repository.query_module.get_schedules_by_project.assert_awaited_once_with(
        project_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_schedules_by_team_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_schedules_by_team delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_schedules_by_team = AsyncMock()
    
    # Datos de prueba
    team_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_schedules_by_team(team_id, start_date, end_date)
    
    # Verificación
    schedule_repository.query_module.get_schedules_by_team.assert_awaited_once_with(
        team_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_confirmed_schedules_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método get_confirmed_schedules delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.get_confirmed_schedules = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    employee_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_confirmed_schedules(start_date, end_date, employee_id)
    
    # Verificación
    schedule_repository.query_module.get_confirmed_schedules.assert_awaited_once_with(
        start_date, end_date, employee_id
    )


@pytest.mark.asyncio
async def test_search_schedules_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método search_schedules delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.search_schedules = AsyncMock()
    
    # Datos de prueba
    filters = {
        "employee_id": 1,
        "project_id": 2,
        "is_confirmed": True
    }
    limit = 10
    offset = 0
    
    # Llamada al método del facade
    await schedule_repository.search_schedules(filters, limit, offset)
    
    # Verificación
    schedule_repository.query_module.search_schedules.assert_awaited_once_with(
        filters, limit, offset
    )


@pytest.mark.asyncio
async def test_count_schedules_delegates_to_query_module(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método count_schedules delega la llamada a QueryModule."""
    # Mock para la operación subyacente
    schedule_repository.query_module.count_schedules = AsyncMock(return_value=5)
    
    # Datos de prueba
    filters = {
        "employee_id": 1,
        "is_confirmed": True
    }
    
    # Llamada al método del facade
    result = await schedule_repository.count_schedules(filters)
    
    # Verificación
    schedule_repository.query_module.count_schedules.assert_awaited_once_with(filters)
    assert result == 5


# =============================================================================
# TESTS PARA MÉTODOS DE RELACIONES
# =============================================================================

@pytest.mark.asyncio
async def test_get_employee_schedules_with_details(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_employee_schedules_with_details."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_employee_schedules_with_details = AsyncMock()
    
    # Datos de prueba
    employee_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_employee_schedules_with_details(
        employee_id=employee_id,
        include_projects=True,
        include_teams=True,
        include_status_codes=True
    )
    
    # Verificación
    schedule_repository.relationship_module.get_employee_schedules_with_details.assert_awaited_once_with(
        employee_id, True, True, True
    )


@pytest.mark.asyncio
async def test_get_employees_with_schedules_in_period(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_employees_with_schedules_in_period."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_employees_with_schedules_in_period = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_employees_with_schedules_in_period(
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.relationship_module.get_employees_with_schedules_in_period.assert_awaited_once_with(
        start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_employee_schedules_in_period(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_employee_schedules_in_period."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_employee_schedules_in_period = AsyncMock()
    
    # Datos de prueba
    employee_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_employee_schedules_in_period(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.relationship_module.get_employee_schedules_in_period.assert_awaited_once_with(
        employee_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_project_schedules_with_details(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_project_schedules_with_details."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_project_schedules_with_details = AsyncMock()
    
    # Datos de prueba
    project_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_project_schedules_with_details(
        project_id=project_id,
        include_employees=True,
        include_teams=True,
        include_status_codes=True
    )
    
    # Verificación
    schedule_repository.relationship_module.get_project_schedules_with_details.assert_awaited_once_with(
        project_id, True, True, True
    )


@pytest.mark.asyncio
async def test_get_projects_with_schedules_in_period(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_projects_with_schedules_in_period."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_projects_with_schedules_in_period = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_projects_with_schedules_in_period(
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.relationship_module.get_projects_with_schedules_in_period.assert_awaited_once_with(
        start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_project_schedules_in_period(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_project_schedules_in_period."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_project_schedules_in_period = AsyncMock()
    
    # Datos de prueba
    project_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_project_schedules_in_period(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.relationship_module.get_project_schedules_in_period.assert_awaited_once_with(
        project_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_team_schedules_with_details(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_team_schedules_with_details."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_team_schedules_with_details = AsyncMock()
    
    # Datos de prueba
    team_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_team_schedules_with_details(
        team_id=team_id,
        include_employees=True,
        include_projects=True,
        include_status_codes=True
    )
    
    # Verificación
    schedule_repository.relationship_module.get_team_schedules_with_details.assert_awaited_once_with(
        team_id, True, True, True
    )


@pytest.mark.asyncio
async def test_assign_schedule_to_project(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para assign_schedule_to_project."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.assign_schedule_to_project = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    project_id = 1
    
    # Llamada al método del facade
    await schedule_repository.assign_schedule_to_project(
        schedule_id=schedule_id,
        project_id=project_id
    )
    
    # Verificación
    schedule_repository.relationship_module.assign_schedule_to_project.assert_awaited_once_with(
        schedule_id, project_id
    )


@pytest.mark.asyncio
async def test_assign_schedule_to_team(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para assign_schedule_to_team."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.assign_schedule_to_team = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    team_id = 1
    
    # Llamada al método del facade
    await schedule_repository.assign_schedule_to_team(
        schedule_id=schedule_id,
        team_id=team_id
    )
    
    # Verificación
    schedule_repository.relationship_module.assign_schedule_to_team.assert_awaited_once_with(
        schedule_id, team_id
    )


@pytest.mark.asyncio
async def test_remove_schedule_from_project(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para remove_schedule_from_project."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.remove_schedule_from_project = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    await schedule_repository.remove_schedule_from_project(
        schedule_id=schedule_id
    )
    
    # Verificación
    schedule_repository.relationship_module.remove_schedule_from_project.assert_awaited_once_with(
        schedule_id
    )


@pytest.mark.asyncio
async def test_remove_schedule_from_team(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para remove_schedule_from_team."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.remove_schedule_from_team = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    await schedule_repository.remove_schedule_from_team(
        schedule_id=schedule_id
    )
    
    # Verificación
    schedule_repository.relationship_module.remove_schedule_from_team.assert_awaited_once_with(
        schedule_id
    )


@pytest.mark.asyncio
async def test_get_schedule_relationships_summary(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_schedule_relationships_summary."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.get_schedule_relationships_summary = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_schedule_relationships_summary(
        schedule_id=schedule_id
    )
    
    # Verificación
    schedule_repository.relationship_module.get_schedule_relationships_summary.assert_awaited_once_with(
        schedule_id
    )


@pytest.mark.asyncio
async def test_validate_project_assignment(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para validate_project_assignment."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.validate_project_assignment = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    project_id = 1
    
    # Llamada al método del facade
    await schedule_repository.validate_project_assignment(
        schedule_id,
        project_id
    )
    
    # Verificación
    schedule_repository.relationship_module.validate_project_assignment.assert_awaited_once_with(
        schedule_id, project_id
    )


@pytest.mark.asyncio
async def test_validate_team_assignment(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para validate_team_assignment."""
    # Mock para la operación subyacente
    schedule_repository.relationship_module.validate_team_assignment = AsyncMock()
    
    # Datos de prueba
    schedule_id = 1
    team_id = 1
    
    # Llamada al método del facade
    await schedule_repository.validate_team_assignment(
        schedule_id,
        team_id
    )
    
    # Verificación
    schedule_repository.relationship_module.validate_team_assignment.assert_awaited_once_with(
        schedule_id, team_id
    )


# =============================================================================
# TESTS PARA MÉTODOS DE ESTADÍSTICAS
# =============================================================================

@pytest.mark.asyncio
async def test_get_employee_hours_summary(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_employee_hours_summary."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_employee_hours_summary = AsyncMock()
    
    # Datos de prueba
    employee_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_employee_hours_summary(
        employee_id=employee_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.statistics_module.get_employee_hours_summary.assert_awaited_once_with(
        employee_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_project_hours_summary(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_project_hours_summary."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_project_hours_summary = AsyncMock()
    
    # Datos de prueba
    project_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_project_hours_summary(
        project_id=project_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.statistics_module.get_project_hours_summary.assert_awaited_once_with(
        project_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_team_hours_summary(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_team_hours_summary."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_team_hours_summary = AsyncMock()
    
    # Datos de prueba
    team_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_team_hours_summary(
        team_id=team_id,
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.statistics_module.get_team_hours_summary.assert_awaited_once_with(
        team_id, start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_schedule_counts_by_status(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_schedule_counts_by_status."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_schedule_counts_by_status = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    employee_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_schedule_counts_by_status(
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id
    )
    
    # Verificación
    schedule_repository.statistics_module.get_schedule_counts_by_status.assert_awaited_once_with(
        start_date, end_date, employee_id
    )


@pytest.mark.asyncio
async def test_get_productivity_metrics(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_productivity_metrics."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_productivity_metrics = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    employee_id = 1
    project_id = 2
    
    # Llamada al método del facade
    await schedule_repository.get_productivity_metrics(
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id,
        project_id=project_id
    )
    
    # Verificación
    schedule_repository.statistics_module.get_productivity_metrics.assert_awaited_once_with(
        start_date, end_date, employee_id, project_id
    )


@pytest.mark.asyncio
async def test_get_utilization_report(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_utilization_report."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_utilization_report = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    group_by = "employee"
    
    # Llamada al método del facade
    await schedule_repository.get_utilization_report(
        start_date=start_date,
        end_date=end_date,
        group_by=group_by
    )
    
    # Verificación
    schedule_repository.statistics_module.get_utilization_report.assert_awaited_once_with(
        start_date, end_date, group_by
    )


@pytest.mark.asyncio
async def test_get_confirmation_statistics(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_confirmation_statistics."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_confirmation_statistics = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    # Llamada al método del facade
    await schedule_repository.get_confirmation_statistics(
        start_date=start_date,
        end_date=end_date
    )
    
    # Verificación
    schedule_repository.statistics_module.get_confirmation_statistics.assert_awaited_once_with(
        start_date, end_date
    )


@pytest.mark.asyncio
async def test_get_overtime_analysis(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_overtime_analysis."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_overtime_analysis = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    employee_id = 1
    
    # Llamada al método del facade
    await schedule_repository.get_overtime_analysis(
        start_date=start_date,
        end_date=end_date,
        employee_id=employee_id
    )
    
    # Verificación
    schedule_repository.statistics_module.get_overtime_analysis.assert_awaited_once_with(
        start_date, end_date, employee_id
    )


@pytest.mark.asyncio
async def test_get_schedule_distribution(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_schedule_distribution."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_schedule_distribution = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    distribution_type = "daily"
    
    # Llamada al método del facade
    await schedule_repository.get_schedule_distribution(
        start_date=start_date,
        end_date=end_date,
        distribution_type=distribution_type
    )
    
    # Verificación
    schedule_repository.statistics_module.get_schedule_distribution.assert_awaited_once_with(
        start_date, end_date, distribution_type
    )


@pytest.mark.asyncio
async def test_get_top_performers(
    schedule_repository: ScheduleRepositoryFacade,
) -> None:
    """Test para get_top_performers."""
    # Mock para la operación subyacente
    schedule_repository.statistics_module.get_top_performers = AsyncMock()
    
    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    metric = "hours"
    limit = 10
    
    # Llamada al método del facade
    await schedule_repository.get_top_performers(
        start_date=start_date,
        end_date=end_date,
        metric=metric,
        limit=limit
    )
    
    # Verificación
    schedule_repository.statistics_module.get_top_performers.assert_awaited_once_with(
        start_date, end_date, metric, limit
    )


# =============================================================================
# TESTS PARA OPERACIONES DE VALIDACIÓN
# =============================================================================

@pytest.mark.asyncio
async def test_validate_schedule_data(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_schedule_data delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_schedule_data = AsyncMock(return_value=True)

    # Datos de prueba
    schedule_data = {
        "employee_id": 1,
        "project_id": 1,
        "schedule_date": date(2024, 1, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "hours": 8.0
    }

    # Llamada al método del facade
    result = await schedule_repository.validate_schedule_data(schedule_data)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_schedule_data.assert_awaited_once_with(schedule_data)


@pytest.mark.asyncio
async def test_validate_schedule_id(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_schedule_id delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_schedule_id = AsyncMock(return_value=True)

    # Datos de prueba
    schedule_id = 1

    # Llamada al método del facade
    result = await schedule_repository.validate_schedule_id(schedule_id)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_schedule_id.assert_awaited_once_with(schedule_id)


@pytest.mark.asyncio
async def test_validate_employee_id(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_employee_id delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_employee_id = AsyncMock(return_value=True)

    # Datos de prueba
    employee_id = 1

    # Llamada al método del facade
    result = await schedule_repository.validate_employee_id(employee_id)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_employee_id.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_validate_date_range(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_date_range delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_date_range = AsyncMock(return_value=True)

    # Datos de prueba
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)

    # Llamada al método del facade
    result = await schedule_repository.validate_date_range(start_date, end_date)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_date_range.assert_awaited_once_with(
        start_date, end_date
    )


@pytest.mark.asyncio
async def test_validate_time_range(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_time_range delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_time_range = AsyncMock(return_value=True)

    # Datos de prueba
    start_time = time(9, 0)
    end_time = time(17, 0)

    # Llamada al método del facade
    result = await schedule_repository.validate_time_range(start_time, end_time)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_time_range.assert_awaited_once_with(
        start_time, end_time
    )


@pytest.mark.asyncio
async def test_validate_schedule_conflicts(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_schedule_conflicts delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_schedule_conflicts = AsyncMock(return_value=True)

    # Datos de prueba
    employee_id = 1
    schedule_date = date(2024, 1, 15)
    start_time = time(9, 0)
    end_time = time(17, 0)
    exclude_schedule_id = 2

    # Llamada al método del facade
    result = await schedule_repository.validate_schedule_conflicts(
        employee_id, schedule_date, start_time, end_time, exclude_schedule_id
    )

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_schedule_conflicts.assert_awaited_once_with(
        employee_id, schedule_date, start_time, end_time, exclude_schedule_id
    )


@pytest.mark.asyncio
async def test_validate_team_membership(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_team_membership delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_team_membership = AsyncMock(return_value=True)

    # Datos de prueba
    employee_id = 1
    team_id = 1

    # Llamada al método del facade
    result = await schedule_repository.validate_team_membership(employee_id, team_id)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_team_membership.assert_awaited_once_with(
        employee_id, team_id
    )


@pytest.mark.asyncio
async def test_validate_search_filters(
    schedule_repository: ScheduleRepositoryFacade,
):
    """Verifica que el método validate_search_filters delega la llamada a ValidationModule."""
    # Mock para la operación subyacente
    schedule_repository.validation_module.validate_search_filters = AsyncMock(return_value=True)

    # Datos de prueba
    filters = {
        "employee_id": 1,
        "project_id": 1,
        "start_date": "2024-01-01",
        "end_date": "2024-01-31"
    }

    # Llamada al método del facade
    result = await schedule_repository.validate_search_filters(filters)

    # Verificación
    assert result is True
    schedule_repository.validation_module.validate_search_filters.assert_awaited_once_with(filters)