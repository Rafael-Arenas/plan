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