# c:\Users\raare\Documents\Personal\01Trabajo\AkGroup\Planificador2\src\planificador\tests\unit\test_repositories\employee\test_employee_repository_facade.py
import pytest
from unittest.mock import AsyncMock
from planificador.repositories.employee.employee_repository_facade import EmployeeRepositoryFacade
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
    employee_repository._crud.delete = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.delete_employee(employee_id)
    
    employee_repository._crud.delete.assert_awaited_once_with(employee_id)

@pytest.mark.asyncio
async def test_get_by_unique_field_delegates_to_crud_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_unique_field delega la llamada a CrudOperations."""
    employee_repository._crud.get_by_unique_field = AsyncMock()

    field_name = "email"
    value = "test@example.com"

    await employee_repository.get_by_unique_field(field_name, value)

    employee_repository._crud.get_by_unique_field.assert_awaited_once_with(
        field_name, value
    )


@pytest.mark.asyncio
async def test_get_all_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_all delega la llamada a QueryOperations."""
    employee_repository._queries.get_all = AsyncMock()
    
    await employee_repository.get_all()
    
    employee_repository._queries.get_all.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_by_full_name_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_full_name delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_full_name = AsyncMock()
    
    full_name = "John Doe"
    
    await employee_repository.get_by_full_name(full_name)
    
    employee_repository._queries.get_by_full_name.assert_awaited_once_with(full_name)


@pytest.mark.asyncio
async def test_get_by_email_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_email delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_email = AsyncMock()
    
    email = "john.doe@example.com"
    
    await employee_repository.get_by_email(email)
    
    employee_repository._queries.get_by_email.assert_awaited_once_with(email)


@pytest.mark.asyncio
async def test_employee_exists_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método employee_exists delega la llamada a QueryOperations."""
    employee_repository._queries.employee_exists = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.employee_exists(employee_id)
    
    employee_repository._queries.employee_exists.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_count_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método count delega la llamada a QueryOperations."""
    employee_repository._queries.count = AsyncMock()
    
    await employee_repository.count()
    
    employee_repository._queries.count.assert_awaited_once()


@pytest.mark.asyncio
async def test_search_by_name_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método search_by_name delega la llamada a QueryOperations."""
    employee_repository._queries.search_by_name = AsyncMock()
    
    name = "John"
    
    await employee_repository.search_by_name(name)
    
    employee_repository._queries.search_by_name.assert_awaited_once_with(name)


@pytest.mark.asyncio
async def test_get_by_department_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_department delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_department = AsyncMock()
    
    department = "Engineering"
    
    await employee_repository.get_by_department(department)
    
    employee_repository._queries.get_by_department.assert_awaited_once_with(department)


@pytest.mark.asyncio
async def test_get_by_position_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_position delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_position = AsyncMock()
    
    position = "Software Engineer"
    
    await employee_repository.get_by_position(position)
    
    employee_repository._queries.get_by_position.assert_awaited_once_with(position)


@pytest.mark.asyncio
async def test_get_by_salary_range_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_salary_range delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_salary_range = AsyncMock()
    
    min_salary = 50000.0
    max_salary = 80000.0
    
    await employee_repository.get_by_salary_range(min_salary, max_salary)
    
    employee_repository._queries.get_by_salary_range.assert_awaited_once_with(min_salary, max_salary)


@pytest.mark.asyncio
async def test_get_by_hire_date_range_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_hire_date_range delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_hire_date_range = AsyncMock()
    
    from datetime import date
    start_date = date(2023, 1, 1)
    end_date = date(2023, 12, 31)
    
    await employee_repository.get_by_hire_date_range(start_date, end_date)
    
    employee_repository._queries.get_by_hire_date_range.assert_awaited_once_with(start_date, end_date)


@pytest.mark.asyncio
async def test_advanced_search_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método advanced_search delega la llamada a QueryOperations."""
    employee_repository._queries.advanced_search = AsyncMock()
    
    filters = {"department": "Engineering", "position": "Software Engineer"}
    
    await employee_repository.advanced_search(filters)
    
    employee_repository._queries.advanced_search.assert_awaited_once_with(filters)


@pytest.mark.asyncio
async def test_get_by_employee_code_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_by_employee_code delega la llamada a QueryOperations."""
    employee_repository._queries.get_by_employee_code = AsyncMock()
    
    employee_code = "EMP123"
    
    await employee_repository.get_by_employee_code(employee_code)
    
    employee_repository._queries.get_by_employee_code.assert_awaited_once_with(employee_code)


@pytest.mark.asyncio
async def test_get_active_employees_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_active_employees delega la llamada a QueryOperations."""
    employee_repository._queries.get_active_employees = AsyncMock()
    
    await employee_repository.get_active_employees()
    
    employee_repository._queries.get_active_employees.assert_awaited_once()


@pytest.mark.asyncio
async def test_get_with_teams_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_with_teams delega la llamada a QueryOperations."""
    employee_repository._queries.get_with_teams = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_with_teams(employee_id)
    
    employee_repository._queries.get_with_teams.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_with_projects_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_with_projects delega la llamada a QueryOperations."""
    employee_repository._queries.get_with_projects = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_with_projects(employee_id)
    
    employee_repository._queries.get_with_projects.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_full_name_exists_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método full_name_exists delega la llamada a QueryOperations."""
    employee_repository._queries.full_name_exists = AsyncMock()
    
    full_name = "John Doe"
    
    await employee_repository.full_name_exists(full_name)
    
    employee_repository._queries.full_name_exists.assert_awaited_once_with(full_name, None)


@pytest.mark.asyncio
async def test_employee_code_exists_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método employee_code_exists delega la llamada a QueryOperations."""
    employee_repository._queries.employee_code_exists = AsyncMock()
    
    employee_code = "EMP123"
    
    await employee_repository.employee_code_exists(employee_code)
    
    employee_repository._queries.employee_code_exists.assert_awaited_once_with(employee_code, None)


@pytest.mark.asyncio
async def test_email_exists_delegates_to_query_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método email_exists delega la llamada a QueryOperations."""
    employee_repository._queries.email_exists = AsyncMock()
    
    email = "john.doe@example.com"
    
    await employee_repository.email_exists(email)
    
    employee_repository._queries.email_exists.assert_awaited_once_with(email, None)


@pytest.mark.asyncio
async def test_get_employee_count_by_status_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_count_by_status delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_employee_count_by_status = AsyncMock()
    
    await employee_repository.get_employee_count_by_status()
    
    employee_repository._statistics.get_employee_count_by_status.assert_awaited_once_with()


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
async def test_get_employee_projects_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_projects delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employee_projects = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_employee_projects(employee_id)
    
    employee_repository._relationships.get_employee_projects.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_employee_vacations_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_vacations delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employee_vacations = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_employee_vacations(employee_id)
    
    employee_repository._relationships.get_employee_vacations.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_team_memberships_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_team_memberships delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_team_memberships = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_team_memberships(employee_id)
    
    employee_repository._relationships.get_team_memberships.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_project_assignments_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_project_assignments delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_project_assignments = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_project_assignments(employee_id)
    
    employee_repository._relationships.get_project_assignments.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_check_team_membership_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método check_team_membership delega la llamada a RelationshipOperations."""
    employee_repository._relationships.check_team_membership = AsyncMock()
    
    employee_id = 1
    team_id = 1
    
    await employee_repository.check_team_membership(employee_id, team_id)
    
    employee_repository._relationships.check_team_membership.assert_awaited_once_with(employee_id, team_id)


@pytest.mark.asyncio
async def test_check_project_assignment_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método check_project_assignment delega la llamada a RelationshipOperations."""
    employee_repository._relationships.check_project_assignment = AsyncMock()
    
    employee_id = 1
    project_id = 1
    
    await employee_repository.check_project_assignment(employee_id, project_id)
    
    employee_repository._relationships.check_project_assignment.assert_awaited_once_with(employee_id, project_id)


@pytest.mark.asyncio
async def test_get_employees_by_team_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_by_team delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employees_by_team = AsyncMock()
    
    team_id = 1
    
    await employee_repository.get_employees_by_team(team_id)
    
    employee_repository._relationships.get_employees_by_team.assert_awaited_once_with(team_id)


@pytest.mark.asyncio
async def test_get_employees_by_project_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_by_project delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employees_by_project = AsyncMock()
    
    project_id = 1
    
    await employee_repository.get_employees_by_project(project_id)
    
    employee_repository._relationships.get_employees_by_project.assert_awaited_once_with(project_id)


@pytest.mark.asyncio
async def test_validate_employee_exists_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_employee_exists delega la llamada a RelationshipOperations."""
    employee_repository._relationships.validate_employee_exists = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.validate_employee_exists(employee_id)
    
    employee_repository._relationships.validate_employee_exists.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_employee_with_all_relations_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_with_all_relations delega la llamada a RelationshipOperations."""
    employee_repository._relationships.get_employee_with_all_relations = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_employee_with_all_relations(employee_id)
    
    employee_repository._relationships.get_employee_with_all_relations.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_count_employee_relationships_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método count_employee_relationships delega la llamada a RelationshipOperations."""
    employee_repository._relationships.count_employee_relationships = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.count_employee_relationships(employee_id)
    
    employee_repository._relationships.count_employee_relationships.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_has_dependencies_delegates_to_relationship_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método has_dependencies delega la llamada a RelationshipOperations."""
    employee_repository._relationships.has_dependencies = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.has_dependencies(employee_id)
    
    employee_repository._relationships.has_dependencies.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_employee_count_by_department_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_count_by_department delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_employee_count_by_department = AsyncMock()
    
    await employee_repository.get_employee_count_by_department()
    
    employee_repository._statistics.get_employee_count_by_department.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_employee_count_by_position_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_count_by_position delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_employee_count_by_position = AsyncMock()
    
    await employee_repository.get_employee_count_by_position()
    
    employee_repository._statistics.get_employee_count_by_position.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_salary_statistics_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_salary_statistics delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_salary_statistics = AsyncMock()
    
    await employee_repository.get_salary_statistics()
    
    employee_repository._statistics.get_salary_statistics.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_hire_date_distribution_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_hire_date_distribution delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_hire_date_distribution = AsyncMock()
    
    await employee_repository.get_hire_date_distribution("monthly")
    
    employee_repository._statistics.get_hire_date_distribution.assert_awaited_once_with("monthly")


@pytest.mark.asyncio
async def test_get_team_participation_stats_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_team_participation_stats delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_team_participation_stats = AsyncMock()
    
    await employee_repository.get_team_participation_stats()
    
    employee_repository._statistics.get_team_participation_stats.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_project_participation_stats_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_project_participation_stats delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_project_participation_stats = AsyncMock()
    
    await employee_repository.get_project_participation_stats()
    
    employee_repository._statistics.get_project_participation_stats.assert_awaited_once_with()


@pytest.mark.asyncio
async def test_get_vacation_statistics_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_vacation_statistics delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_vacation_statistics = AsyncMock()
    
    await employee_repository.get_vacation_statistics(year=2024)
    
    employee_repository._statistics.get_vacation_statistics.assert_awaited_once_with(2024)


@pytest.mark.asyncio
async def test_get_skills_distribution_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_skills_distribution delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_skills_distribution = AsyncMock()
    
    await employee_repository.get_skills_distribution(limit=10)
    
    employee_repository._statistics.get_skills_distribution.assert_awaited_once_with(10)


@pytest.mark.asyncio
async def test_get_employee_workload_stats_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_workload_stats delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_employee_workload_stats = AsyncMock()
    
    from datetime import date
    employee_id = 1
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    
    await employee_repository.get_employee_workload_stats(employee_id, start_date, end_date)
    
    employee_repository._statistics.get_employee_workload_stats.assert_awaited_once_with(employee_id, start_date, end_date)


@pytest.mark.asyncio
async def test_get_comprehensive_summary_delegates_to_statistics_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_comprehensive_summary delega la llamada a StatisticsOperations."""
    employee_repository._statistics.get_comprehensive_summary = AsyncMock()
    
    await employee_repository.get_comprehensive_summary()
    
    employee_repository._statistics.get_comprehensive_summary.assert_awaited_once_with()


# ============================================================================
# TESTS PARA DATE OPERATIONS
# ============================================================================

@pytest.mark.asyncio
async def test_get_employees_hired_current_week_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_hired_current_week delega la llamada a DateOperations."""
    employee_repository._dates.get_employees_hired_current_week = AsyncMock()
    
    kwargs = {"status": "active"}
    
    await employee_repository.get_employees_hired_current_week(**kwargs)
    
    employee_repository._dates.get_employees_hired_current_week.assert_awaited_once_with(**kwargs)


@pytest.mark.asyncio
async def test_get_employees_hired_current_month_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_hired_current_month delega la llamada a DateOperations."""
    employee_repository._dates.get_employees_hired_current_month = AsyncMock()
    
    kwargs = {"department": "IT"}
    
    await employee_repository.get_employees_hired_current_month(**kwargs)
    
    employee_repository._dates.get_employees_hired_current_month.assert_awaited_once_with(**kwargs)


@pytest.mark.asyncio
async def test_get_employees_hired_business_days_only_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_hired_business_days_only delega la llamada a DateOperations."""
    employee_repository._dates.get_employees_hired_business_days_only = AsyncMock()
    
    from datetime import date
    start_date = date(2024, 1, 1)
    end_date = date(2024, 1, 31)
    kwargs = {"status": "active"}
    
    await employee_repository.get_employees_hired_business_days_only(
        start_date=start_date, end_date=end_date, **kwargs
    )
    
    employee_repository._dates.get_employees_hired_business_days_only.assert_awaited_once_with(
        start_date=start_date, end_date=end_date, **kwargs
    )


@pytest.mark.asyncio
async def test_get_employee_tenure_stats_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employee_tenure_stats delega la llamada a DateOperations."""
    employee_repository._dates.get_employee_tenure_stats = AsyncMock()
    
    employee_id = 1
    
    await employee_repository.get_employee_tenure_stats(employee_id)
    
    employee_repository._dates.get_employee_tenure_stats.assert_awaited_once_with(employee_id)


@pytest.mark.asyncio
async def test_get_employees_by_tenure_range_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método get_employees_by_tenure_range delega la llamada a DateOperations."""
    employee_repository._dates.get_employees_by_tenure_range = AsyncMock()
    
    min_years = 2.0
    max_years = 5.0
    status = "active"
    
    await employee_repository.get_employees_by_tenure_range(
        min_years=min_years, max_years=max_years, status=status
    )
    
    employee_repository._dates.get_employees_by_tenure_range.assert_awaited_once_with(
        min_years=min_years, max_years=max_years, status=status
    )


@pytest.mark.asyncio
async def test_create_employee_with_date_validation_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método create_employee_with_date_validation delega la llamada a DateOperations."""
    employee_repository._dates.create_employee_with_date_validation = AsyncMock()
    
    employee_data = {"name": "John Doe", "email": "john@example.com"}
    validate_hire_date_business_day = True
    
    await employee_repository.create_employee_with_date_validation(
        employee_data=employee_data,
        validate_hire_date_business_day=validate_hire_date_business_day
    )
    
    employee_repository._dates.create_employee_with_date_validation.assert_awaited_once_with(
        employee_data=employee_data,
        validate_hire_date_business_day=validate_hire_date_business_day
    )


def test_format_employee_hire_date_delegates_to_date_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método format_employee_hire_date delega la llamada a DateOperations."""
    from unittest.mock import MagicMock
    employee_repository._dates.format_employee_hire_date = MagicMock()
    
    employee = MagicMock()
    format_type = "iso"
    
    employee_repository.format_employee_hire_date(
        employee=employee, format_type=format_type
    )
    
    employee_repository._dates.format_employee_hire_date.assert_called_once_with(
        employee=employee, format_type=format_type
    )


# ============================================================================
# TESTS PARA VALIDATION OPERATIONS
# ============================================================================

def test_validate_create_data_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_create_data delega la llamada a ValidationOperations."""
    from unittest.mock import MagicMock
    employee_repository._validation.validate_create_data = MagicMock()
    
    employee_data = {"name": "John", "email": "john@example.com"}
    
    employee_repository.validate_create_data(employee_data)
    
    employee_repository._validation.validate_create_data.assert_called_once_with(employee_data)


def test_validate_update_data_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_update_data delega la llamada a ValidationOperations."""
    from unittest.mock import MagicMock
    employee_repository._validation.validate_update_data = MagicMock()
    
    employee_data = {"name": "John Updated", "position": "Senior Developer"}
    
    employee_repository.validate_update_data(employee_data)
    
    employee_repository._validation.validate_update_data.assert_called_once_with(employee_data)


def test_validate_skills_json_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_skills_json delega la llamada a ValidationOperations."""
    from unittest.mock import MagicMock
    employee_repository._validation.validate_skills_json = MagicMock()
    
    skills_json = '["Python", "JavaScript", "SQL"]'
    
    employee_repository.validate_skills_json(skills_json)
    
    employee_repository._validation.validate_skills_json.assert_called_once_with(skills_json)


def test_validate_search_term_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_search_term delega la llamada a ValidationOperations."""
    from unittest.mock import MagicMock
    employee_repository._validation.validate_search_term = MagicMock()
    
    search_term = "John Doe"
    
    employee_repository.validate_search_term(search_term)
    
    employee_repository._validation.validate_search_term.assert_called_once_with(search_term)


def test_validate_employee_id_delegates_to_validation_operations(
    employee_repository: EmployeeRepositoryFacade,
):
    """Verifica que el método validate_employee_id delega la llamada a ValidationOperations."""
    from unittest.mock import MagicMock
    employee_repository._validation.validate_employee_id = MagicMock()
    
    employee_id = 1
    
    employee_repository.validate_employee_id(employee_id)
    
    employee_repository._validation.validate_employee_id.assert_called_once_with(employee_id)