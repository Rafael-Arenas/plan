# c:\Users\raare\Documents\Personal\01Trabajo\AkGroup\Planificador2\src\planificador\tests\unit\test_repositories\employee\test_employee_repository_facade.py
import pytest
from unittest.mock import AsyncMock, MagicMock
from planificador.repositories.employee.employee_repository_facade import EmployeeRepositoryFacade
from planificador.models.employee import Employee
from planificador.tests.unit.test_repositories.employee.fixtures import employee_repository, mock_session

@pytest.mark.asyncio
async def test_create_employee_delegates_to_crud_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método create_employee delega la llamada a CrudOperations."""
    # Mock para la operación subyacente
    employee_repository._crud.create_employee = AsyncMock()

    # Datos de prueba
    employee_data = {"full_name": "John Doe", "email": "john.doe@example.com"}

    # Llamada al método del facade
    await employee_repository.create_employee(employee_data)

    # Verificación
    employee_repository._crud.create_employee.assert_awaited_once_with(employee_data)

@pytest.mark.asyncio
async def test_update_employee_delegates_to_crud_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método update_employee delega la llamada a CrudOperations."""
    employee_repository._crud.update_employee = AsyncMock()
    
    employee_id = 1
    update_data = {"full_name": "John Doe Updated"}
    
    await employee_repository.update_employee(employee_id, update_data)
    
    employee_repository._crud.update_employee.assert_awaited_once_with(employee_id, update_data)

@pytest.mark.asyncio
async def test_delete_employee_delegates_to_crud_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método delete_employee delega la llamada a CrudOperations."""
    employee_repository._crud.delete_employee = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.delete_employee(employee_id)
    
    employee_repository._crud.delete_employee.assert_awaited_once_with(employee_id)

@pytest.mark.asyncio
async def test_get_by_id_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_id delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_id = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_by_id(employee_id)
    
    employee_repository._queries.get_by_id.assert_awaited_once_with(employee_id)

@pytest.mark.asyncio
async def test_get_employee_teams_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_teams delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employee_teams = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_employee_teams(employee_id)
    
    employee_repository._relationships.get_employee_teams.assert_awaited_once_with(employee_id)

@pytest.mark.asyncio
async def test_get_employee_count_by_status_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_count_by_status delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_employee_count_by_status = AsyncMock()
    
    await employee_repository.get_employee_count_by_status()
    
    employee_repository._statistics.get_employee_count_by_status.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_status_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_status delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_status = AsyncMock()
    await employee_repository.get_by_status("active")
    employee_repository._queries.get_by_status.assert_awaited_once_with("active")


@pytest.mark.asyncio
async def test_get_available_employees_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_available_employees delega la llamada a QueryOperations."""
    employee_repository._queries.get_available_employees = AsyncMock()
    await employee_repository.get_available_employees()
    employee_repository._queries.get_available_employees.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_search_by_skills_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método search_by_skills delega la llamada a QueryOperations."""
    employee_repository._queries.search_by_skills = AsyncMock()
    await employee_repository.search_by_skills(["python", "sql"])
    employee_repository._queries.search_by_skills.assert_awaited_once_with(["python", "sql"])


@pytest.mark.asyncio
async def test_get_by_department_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_department delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_department = AsyncMock()
    await employee_repository.get_by_department("IT")
    employee_repository._queries.get_by_department.assert_awaited_once_with("IT")


@pytest.mark.asyncio
async def test_get_by_position_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_position delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_position = AsyncMock()
    await employee_repository.get_by_position("Developer")
    employee_repository._queries.get_by_position.assert_awaited_once_with("Developer")


@pytest.mark.asyncio
async def test_get_by_salary_range_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_salary_range delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_salary_range = AsyncMock()
    await employee_repository.get_by_salary_range(50000, 100000)
    employee_repository._queries.get_by_salary_range.assert_awaited_once_with(50000, 100000)


@pytest.mark.asyncio
async def test_get_by_hire_date_range_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_hire_date_range delega la llamada a QueryOperations."""
    from datetime import date
    employee_repository._queries.get_by_hire_date_range = AsyncMock()
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    await employee_repository.get_by_hire_date_range(start_date, end_date)
    employee_repository._queries.get_by_hire_date_range.assert_awaited_once_with(start_date, end_date)


@pytest.mark.asyncio
async def test_advanced_search_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método advanced_search delega la llamada a QueryOperations."""
    employee_repository._queries.advanced_search = AsyncMock()
    filters = {"department": "IT"}
    await employee_repository.advanced_search(filters)
    employee_repository._queries.advanced_search.assert_awaited_once_with(filters)


@pytest.mark.asyncio
async def test_get_by_full_name_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_full_name delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_full_name = AsyncMock()
    await employee_repository.get_by_full_name("John Doe")
    employee_repository._queries.get_by_full_name.assert_awaited_once_with("John Doe")


@pytest.mark.asyncio
async def test_get_by_employee_code_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_by_employee_code delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_employee_code = AsyncMock()
    await employee_repository.get_by_employee_code("EMP123")
    employee_repository._queries.get_by_employee_code.assert_awaited_once_with("EMP123")


@pytest.mark.asyncio
async def test_get_active_employees_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_active_employees delega la llamada a QueryOperations."""
    employee_repository._queries.get_active_employees = AsyncMock()
    await employee_repository.get_active_employees()
    employee_repository._queries.get_active_employees.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_with_teams_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_with_teams delega la llamada a QueryOperations."""
    employee_repository._queries.get_with_teams = AsyncMock()
    await employee_repository.get_with_teams(1)
    employee_repository._queries.get_with_teams.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_get_with_projects_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método get_with_projects delega la llamada a QueryOperations."""
    employee_repository._queries.get_with_projects = AsyncMock()
    await employee_repository.get_with_projects(1)
    employee_repository._queries.get_with_projects.assert_awaited_once_with(1)


@pytest.mark.asyncio
async def test_full_name_exists_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método full_name_exists delega la llamada a QueryOperations."""
    employee_repository._queries.full_name_exists = AsyncMock()
    await employee_repository.full_name_exists("John Doe", 1)
    employee_repository._queries.full_name_exists.assert_awaited_once_with("John Doe", 1)


@pytest.mark.asyncio
async def test_employee_code_exists_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método employee_code_exists delega la llamada a QueryOperations."""
    employee_repository._queries.employee_code_exists = AsyncMock()
    await employee_repository.employee_code_exists("EMP123", 1)
    employee_repository._queries.employee_code_exists.assert_awaited_once_with("EMP123", 1)


@pytest.mark.asyncio
async def test_email_exists_delegates_to_queries(
    employee_repository: EmployeeRepositoryFacade,
) -> None:
    """Verifica que el método email_exists delega la llamada a QueryOperations."""
    employee_repository._queries.email_exists = AsyncMock()
    await employee_repository.email_exists("test@example.com", 1)
    employee_repository._queries.email_exists.assert_awaited_once_with("test@example.com", 1)

def test_validate_create_data_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_create_data delega la llamada a ValidationOperations."""
    employee_repository._validation.validate_create_data = MagicMock()
    
    data = {"full_name": "Jane Doe"}
    
    employee_repository.validate_create_data(data)
    
    employee_repository._validation.validate_create_data.assert_called_once_with(data)


def test_validate_update_data_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_update_data delega la llamada a ValidationOperations."""
    employee_repository._validation.validate_update_data = MagicMock()
    
    data = {"full_name": "Jane Doe Updated"}
    
    employee_repository.validate_update_data(data)
    
    employee_repository._validation.validate_update_data.assert_called_once_with(data)


def test_validate_skills_json_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_skills_json delega la llamada a ValidationOperations."""
    employee_repository._validation.validate_skills_json = MagicMock()
    
    skills_json = '["python", "sql"]'
    
    employee_repository.validate_skills_json(skills_json)
    
    employee_repository._validation.validate_skills_json.assert_called_once_with(skills_json)


def test_validate_search_term_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_search_term delega la llamada a ValidationOperations."""
    employee_repository._validation.validate_search_term = MagicMock()
    
    search_term = "  test search  "
    
    employee_repository.validate_search_term(search_term)
    
    employee_repository._validation.validate_search_term.assert_called_once_with(search_term)


def test_validate_employee_id_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_employee_id delega la llamada a ValidationOperations."""
    employee_repository._validation.validate_employee_id = MagicMock()
    
    employee_id = 1
    
    employee_repository.validate_employee_id(employee_id)
    
    employee_repository._validation.validate_employee_id.assert_called_once_with(employee_id)