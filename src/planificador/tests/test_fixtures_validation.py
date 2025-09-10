"""Tests de validación para las fixtures de base de datos."""

import pytest
from datetime import date
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.client import Client
from planificador.models.employee import Employee
from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.models.team import Team


class TestFixturesValidation:
    """Tests para validar que las fixtures funcionan correctamente."""

    @pytest.mark.asyncio
    async def test_project_with_different_statuses_fixture(
        self,
        project_with_different_statuses: list[Project],
        test_session: AsyncSession,
    ):
        """Test que la fixture project_with_different_statuses funciona correctamente."""
        # Verificar que tenemos proyectos con diferentes estados
        assert len(project_with_different_statuses) >= 3
        
        # Verificar que hay al menos un proyecto con cada estado principal
        statuses = [project.status for project in project_with_different_statuses]
        assert ProjectStatus.PLANNED in statuses
        assert ProjectStatus.IN_PROGRESS in statuses
        assert ProjectStatus.COMPLETED in statuses

    @pytest.mark.asyncio
    async def test_project_with_different_priorities_fixture(
        self,
        project_with_different_priorities: list[Project],
        test_session: AsyncSession,
    ):
        """Test que la fixture project_with_different_priorities funciona correctamente."""
        # Verificar que tenemos proyectos con diferentes prioridades
        assert len(project_with_different_priorities) >= 3
        
        # Verificar que hay al menos un proyecto con cada prioridad
        priorities = [project.priority for project in project_with_different_priorities]
        assert ProjectPriority.LOW in priorities
        assert ProjectPriority.MEDIUM in priorities
        assert ProjectPriority.HIGH in priorities
        
        # Verificar que todos los proyectos están en progreso
        for project in project_with_different_priorities:
            assert project.status == ProjectStatus.IN_PROGRESS

    @pytest.mark.asyncio
    async def test_multiple_teams_fixture(
        self,
        test_session: AsyncSession,
        multiple_teams: list[Team]
    ):
        """Test que valida la fixture multiple_teams."""
        # Verificar que se crearon equipos
        assert len(multiple_teams) >= 3
        
        # Verificar que hay equipos activos e inactivos
        active_teams = [team for team in multiple_teams if team.is_active]
        inactive_teams = [team for team in multiple_teams if not team.is_active]
        
        assert len(active_teams) >= 2
        assert len(inactive_teams) >= 1
        
        # Verificar nombres específicos
        team_names = [team.name for team in multiple_teams]
        assert "Frontend Team" in team_names
        assert "Backend Team" in team_names
        assert "QA Team" in team_names
        assert "Inactive Team" in team_names

    @pytest.mark.asyncio
    async def test_project_with_long_duration_fixture(
        self,
        project_with_long_duration: Project,
        test_session: AsyncSession,
    ):
        """Test que la fixture project_with_long_duration funciona correctamente."""
        # Verificar que el proyecto tiene una duración larga
        assert project_with_long_duration.duration_days is not None
        assert project_with_long_duration.duration_days >= 365  # Al menos un año
        
        # Verificar que está en progreso
        assert project_with_long_duration.status == ProjectStatus.IN_PROGRESS
        
        # Verificar que tiene fechas de inicio y fin
        assert project_with_long_duration.start_date is not None
        assert project_with_long_duration.end_date is not None

    @pytest.mark.asyncio
    async def test_team_with_members_fixture(
        self,
        test_session: AsyncSession,
        team_with_members: Team,
        multiple_employees: list[Employee]
    ):
        """Test que valida la fixture team_with_members."""
        team = team_with_members
        
        # Verificar que el equipo existe
        assert team is not None
        assert team.name == "Full Development Team"
        assert team.is_active is True
        
        # Verificar que hay empleados disponibles
        assert multiple_employees is not None
        assert len(multiple_employees) > 0
        
        # Verificar que los miembros tienen propiedades válidas
        for employee in multiple_employees:
            assert employee.first_name is not None
            assert employee.last_name is not None
            assert employee.email is not None
            assert "@" in employee.email