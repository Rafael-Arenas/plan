"""Pruebas unitarias para el facade del repositorio de membresías de equipo."""

import pytest
from datetime import date
from unittest.mock import AsyncMock, MagicMock

from planificador.models.team_membership import TeamMembership
from planificador.repositories.team_membership import TeamMembershipRepositoryFacade


@pytest.mark.asyncio
class TestTeamMembershipRepositoryFacade:
    """Clase de pruebas para el facade del repositorio de membresías de equipo."""

    async def test_repository_initialization(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Verifica que el repositorio se inicializa correctamente."""
        assert isinstance(team_membership_repository, TeamMembershipRepositoryFacade)
        assert hasattr(team_membership_repository, "session")
        assert team_membership_repository.session is not None


@pytest.mark.asyncio
class TestCrudOperations:
    """Clase de pruebas para las operaciones CRUD del facade."""

    async def test_create_membership_success(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_data: dict,
    ) -> None:
        """Verifica la creación exitosa de una membresía."""
        membership = TeamMembership(**sample_membership_data)
        team_membership_repository._crud_module.create_membership = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.create_membership(
            sample_membership_data
        )

        assert result == membership
        team_membership_repository._crud_module.create_membership.assert_called_once_with(
            sample_membership_data
        )

    async def test_update_membership_success(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_data: dict,
    ) -> None:
        """Verifica la actualización exitosa de una membresía."""
        membership = TeamMembership(**sample_membership_data)
        team_membership_repository._crud_module.update_membership = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.update_membership(
            1, sample_membership_data
        )

        assert result == membership
        team_membership_repository._crud_module.update_membership.assert_called_once_with(
            1, sample_membership_data
        )

    async def test_get_membership_by_id_success(
        self, team_membership_repository: TeamMembershipRepositoryFacade
    ) -> None:
        """Verifica la obtención exitosa de una membresía por ID."""
        from planificador.models.team_membership import MembershipRole
        
        membership = TeamMembership(
            id=1,
            employee_id=1,
            team_id=1,
            role=MembershipRole.MEMBER,
            start_date=date(2024, 1, 1),
            end_date=None,
            is_active=True,
        )
        team_membership_repository._query_module.get_membership_by_id = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.get_membership_by_id(1)

        assert result == membership
        team_membership_repository._query_module.get_membership_by_id.assert_called_once_with(1)

    async def test_activate_membership_success(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_data: dict,
    ) -> None:
        """Verifica la activación exitosa de una membresía."""
        membership = TeamMembership(**sample_membership_data)
        team_membership_repository._crud_module.activate_membership = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.activate_membership(1)

        assert result == membership
        team_membership_repository._crud_module.activate_membership.assert_called_once_with(1)

    async def test_deactivate_membership_success(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_data: dict,
    ) -> None:
        """Verifica la desactivación exitosa de una membresía."""
        membership = TeamMembership(**sample_membership_data)
        team_membership_repository._crud_module.deactivate_membership = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.deactivate_membership(1)

        assert result == membership
        team_membership_repository._crud_module.deactivate_membership.assert_called_once_with(1, None)

    async def test_get_by_unique_field_success(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_list: list[TeamMembership],
    ) -> None:
        """Verifica la búsqueda por campo único."""
        membership = sample_membership_list[0]
        membership.id = 1  # Asegurar que el objeto tenga ID
        team_membership_repository._crud_module.get_by_unique_field = AsyncMock(
            return_value=membership
        )

        result = await team_membership_repository.get_by_unique_field("id", 1)

        assert result.id == 1
        team_membership_repository._crud_module.get_by_unique_field.assert_called_once_with("id", 1)

    async def test_get_memberships_by_role(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención de membresías por rol."""
        from planificador.models.team_membership import MembershipRole
        
        team_membership_repository._query_module.get_memberships_by_role = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_memberships_by_role(
            MembershipRole.MEMBER
        )

        assert result == sample_membership_list
        team_membership_repository._query_module.get_memberships_by_role.assert_called_once_with(
            MembershipRole.MEMBER, True
        )

    async def test_get_active_memberships(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención de membresías activas."""
        team_membership_repository._query_module.get_active_memberships = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_active_memberships()

        assert result == sample_membership_list
        team_membership_repository._query_module.get_active_memberships.assert_called_once()

    async def test_get_past_memberships(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención de membresías pasadas."""
        team_membership_repository._query_module.get_past_memberships = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_past_memberships()

        assert result == sample_membership_list
        team_membership_repository._query_module.get_past_memberships.assert_called_once_with(None)

    async def test_get_memberships_by_date_range(
        self,
        team_membership_repository: TeamMembershipRepositoryFacade,
        sample_membership_list: list[TeamMembership],
    ) -> None:
        """Verifica la obtención de membresías por rango de fechas."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)

        team_membership_repository._query_module.get_memberships_by_date_range = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_memberships_by_date_range(
            start_date, end_date
        )

        assert result == sample_membership_list
        team_membership_repository._query_module.get_memberships_by_date_range.assert_called_once_with(
            start_date, end_date, True
        )

    async def test_get_memberships_by_employee(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la búsqueda de membresías por ID de empleado."""
        team_membership_repository._query_module.get_memberships_by_employee = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_memberships_by_employee(1)

        assert result == sample_membership_list
        team_membership_repository._query_module.get_memberships_by_employee.assert_called_once_with(
            1, True
        )

    async def test_get_memberships_by_team(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la búsqueda de membresías por ID de equipo."""
        team_membership_repository._query_module.get_memberships_by_team = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_memberships_by_team(1)

        assert result == sample_membership_list
        team_membership_repository._query_module.get_memberships_by_team.assert_called_once_with(
            1, True
        )

    async def test_get_membership_by_employee_and_team(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la búsqueda de membresía por empleado y equipo."""
        team_membership_repository._query_module.get_membership_by_employee_and_team = AsyncMock(
            return_value=sample_membership_list[0]
        )

        result = await team_membership_repository.get_membership_by_employee_and_team(
            1, 1
        )

        assert result == sample_membership_list[0]
        team_membership_repository._query_module.get_membership_by_employee_and_team.assert_called_once_with(
            1, 1, True
        )

    async def test_get_current_membership_for_employee(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención de la membresía actual de un empleado."""
        team_membership_repository._query_module.get_current_membership_for_employee = AsyncMock(
            return_value=sample_membership_list[0]
        )

        result = await team_membership_repository.get_current_membership_for_employee(1)

        assert result == sample_membership_list[0]
        team_membership_repository._query_module.get_current_membership_for_employee.assert_called_once_with(
            1
        )

    async def test_get_current_membership_for_employee(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención de la membresía actual de un empleado."""
        team_membership_repository._query_module.get_current_memberships = AsyncMock(
            return_value=sample_membership_list
        )

        result = await team_membership_repository.get_current_memberships()

        assert result == sample_membership_list
        team_membership_repository._query_module.get_current_memberships.assert_called_once_with(None)

    async def test_get_employee_for_membership(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención del empleado para una membresía."""
        from planificador.models.employee import Employee

        employee = Employee(
            first_name="John",
            last_name="Doe",
            email="john.doe@example.com",
            phone="123456789",
            hire_date=date(2024, 1, 1),
        )

        # Mock del membership con employee
        membership_with_employee = sample_membership_list[0]
        membership_with_employee.employee = employee
        
        team_membership_repository._relationship_module.get_membership_with_employee = AsyncMock(
            return_value=membership_with_employee
        )

        result = await team_membership_repository.get_employee_for_membership(1)

        assert result == employee
        team_membership_repository._relationship_module.get_membership_with_employee.assert_called_once_with(
            1
        )

    async def test_get_team_for_membership(
        self, team_membership_repository: TeamMembershipRepositoryFacade, sample_membership_list: list[TeamMembership]
    ) -> None:
        """Verifica la obtención del equipo para una membresía."""
        from planificador.models.team import Team

        team = Team(
            id=1,
            name="Development Team",
            description="Main development team",
            is_active=True,
        )

        # Mock del membership con team
        membership_with_team = sample_membership_list[0]
        membership_with_team.team = team

        team_membership_repository._relationship_module.get_membership_with_team = AsyncMock(
            return_value=membership_with_team
        )

        result = await team_membership_repository.get_team_for_membership(1)

        assert result == team
        team_membership_repository._relationship_module.get_membership_with_team.assert_called_once_with(1)

    async def test_get_membership_count(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener el número total de membresías."""
        team_membership_repository.count_total_memberships = AsyncMock(return_value=10)

        result = await team_membership_repository.get_membership_count()

        assert result == 10
        team_membership_repository.count_total_memberships.assert_called_once_with()

    async def test_get_active_membership_count(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener el número de membresías activas."""
        team_membership_repository.count_total_memberships = AsyncMock(return_value=5)

        result = await team_membership_repository.get_active_membership_count()

        assert result == 5
        team_membership_repository.count_total_memberships.assert_called_once_with(active_only=True)

    async def test_get_membership_count_by_role(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener el número de membresías por rol."""
        from planificador.models.team_membership import MembershipRole

        role = MembershipRole.LEAD
        team_membership_repository.count_memberships_by_role = AsyncMock(
            return_value={role: 2, MembershipRole.MEMBER: 5}
        )

        result = await team_membership_repository.get_membership_count_by_role(role)

        assert result == 2
        team_membership_repository.count_memberships_by_role.assert_called_once_with()

    async def test_get_average_membership_duration(
        self, team_membership_repository: TeamMembershipRepositoryFacade
    ) -> None:
        """Prueba que se pueda obtener la duración promedio de las membresías."""
        team_membership_repository.get_membership_duration_statistics = AsyncMock(
            return_value={"average_duration": 180.5, "median_duration": 175.0}
        )

        result = await team_membership_repository.get_average_membership_duration()

        assert result == 180.5
        team_membership_repository.get_membership_duration_statistics.assert_called_once_with()

    async def test_get_memberships_per_team(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener el número de membresías por equipo."""
        expected_result = {1: 5, 2: 3, 3: 7}
        team_membership_repository._statistics_module.get_memberships_per_team = AsyncMock(return_value=expected_result)

        result = await team_membership_repository.get_memberships_per_team()

        assert result == expected_result
        team_membership_repository._statistics_module.get_memberships_per_team.assert_called_once_with()

    async def test_get_memberships_per_employee(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener el número de membresías por empleado."""
        expected_result = {1: 3, 2: 2, 3: 4}
        team_membership_repository._statistics_module.get_memberships_per_employee = AsyncMock(return_value=expected_result)

        result = await team_membership_repository.get_memberships_per_employee()

        assert result == expected_result
        team_membership_repository._statistics_module.get_memberships_per_employee.assert_called_once_with()

    async def test_get_role_distribution(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener la distribución de roles."""
        expected_result = {"LEAD": 2, "MEMBER": 8}
        team_membership_repository._statistics_module.get_role_distribution = AsyncMock(return_value=expected_result)

        result = await team_membership_repository.get_role_distribution()

        assert result == expected_result
        team_membership_repository._statistics_module.get_role_distribution.assert_called_once_with()

    async def test_get_average_duration_by_role(self, team_membership_repository: TeamMembershipRepositoryFacade) -> None:
        """Prueba que se pueda obtener la duración promedio por rol."""
        expected_result = {"LEAD": 200.5, "MEMBER": 150.3}
        team_membership_repository._statistics_module.get_average_duration_by_role = AsyncMock(return_value=expected_result)

        result = await team_membership_repository.get_average_duration_by_role()

        assert result == expected_result
        team_membership_repository._statistics_module.get_average_duration_by_role.assert_called_once_with()


@pytest.mark.asyncio
class TestValidationOperations:
    """
    Pruebas para las operaciones de validación de la fachada del repositorio.
    """

    async def test_validate_membership_dates_success(
        self, team_membership_repository: TeamMembershipRepositoryFacade
    ) -> None:
        """Prueba que se puedan validar fechas de membresía correctamente."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        team_membership_repository._validation_module.validate_dates = AsyncMock(return_value=None)

        await team_membership_repository.validate_membership_dates(start_date, end_date)

        team_membership_repository._validation_module.validate_dates.assert_called_once_with(start_date, end_date)

    async def test_check_employee_active_membership_exists(
        self, team_membership_repository: TeamMembershipRepositoryFacade
    ) -> None:
        """Prueba que se pueda verificar si un empleado tiene membresía activa."""
        employee_id = 1
        team_membership_repository._validation_module.has_active_membership = AsyncMock(return_value=True)

        result = await team_membership_repository.check_employee_active_membership(employee_id)

        assert result is True
        team_membership_repository._validation_module.has_active_membership.assert_called_once_with(employee_id)

    async def test_validate_role_for_update_success(
        self, team_membership_repository: TeamMembershipRepositoryFacade
    ) -> None:
        """Prueba que se pueda validar un rol para actualización."""
        from planificador.models.team_membership import MembershipRole

        membership_id = 1
        new_role = MembershipRole.LEAD
        team_membership_repository._validation_module.is_valid_role_for_update = AsyncMock(return_value=True)

        result = await team_membership_repository.validate_role_for_update(membership_id, new_role)

        assert result is True
        team_membership_repository._validation_module.is_valid_role_for_update.assert_called_once_with(
            membership_id, new_role
        )