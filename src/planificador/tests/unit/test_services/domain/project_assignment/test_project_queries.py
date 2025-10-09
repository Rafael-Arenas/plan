"""Tests unitarios para las operaciones de consulta de proyectos del ProjectAssignmentDomainService.

Este módulo contiene todas las pruebas unitarias para las operaciones de consulta
relacionadas con proyectos del servicio de dominio de asignaciones de proyecto.

Operaciones probadas:
- get_assignments_by_project: Obtención de asignaciones por proyecto
- get_project_team_summary: Resumen del equipo de proyecto
- get_project_resource_allocation: Asignación de recursos del proyecto
- get_project_assignment_timeline: Línea de tiempo de asignaciones del proyecto
"""

import pytest
import pendulum
from typing import List
from unittest.mock import MagicMock, AsyncMock
from uuid import UUID

from planificador.services.domain.project_assignment.modules.project_queries import ProjectQueries
from planificador.schemas.assignment.assignment import ProjectAssignment
from planificador.schemas.assignment.advanced_schemas import (
    ProjectTeamSummarySchema, ProjectResourceAllocationSchema,
    ProjectTimelineSchema, EmployeeWorkloadSummarySchema
)
from planificador.exceptions import RepositoryError, ValidationError


class TestProjectQueries:
    """
    Clase de tests para las operaciones de consulta de proyectos.
    
    Agrupa todos los tests relacionados con operaciones de consulta
    específicas de proyectos.
    """

    @pytest.fixture
    def mock_repository_facade(self) -> AsyncMock:
        """Fixture para mockear RepositoryFacade."""
        facade = AsyncMock()
        facade.project_assignment = AsyncMock()
        facade.project = AsyncMock()
        return facade

    @pytest.fixture
    def project_queries(self, mock_repository_facade: AsyncMock) -> ProjectQueries:
        """Fixture que crea una instancia de ProjectQueries con un mock de RepositoryFacade."""
        return ProjectQueries(repository_facade=mock_repository_facade)

    # ==================== TESTS GET_ASSIGNMENTS_BY_PROJECT ====================

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_success(self, project_queries, mock_repository_facade):
        """
        Prueba que se obtienen las asignaciones de un proyecto correctamente.
        """
        # Configuración del mock
        project_id = 1
        now = pendulum.now()
        mock_assignments = [
            ProjectAssignment(
                id=1, project_id=project_id, employee_id=101, 
                start_date=now.date(), created_at=now, updated_at=now
            ),
            ProjectAssignment(
                id=2, project_id=project_id, employee_id=102, 
                start_date=now.date(), created_at=now, updated_at=now
            ),
        ]
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = mock_assignments

        # Ejecución
        assignments = await project_queries.get_assignments_by_project(project_id)

        # Verificación
        assert assignments == mock_assignments
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_empty_result(self, project_queries, mock_repository_facade):
        """
        Prueba que se maneja correctamente un resultado vacío.
        """
        # Configuración del mock
        project_id = 99
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = []

        # Ejecución
        assignments = await project_queries.get_assignments_by_project(project_id)

        # Verificación
        assert assignments == []
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_invalid_id(self, project_queries):
        """Test con ID de proyecto inválido."""
        project_id = -1
        with pytest.raises(ValidationError, match="ID de proyecto debe ser un entero positivo."):
            await project_queries.get_assignments_by_project(project_id)

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_repository_error(self, project_queries, mock_repository_facade):
        """
        Prueba el manejo de RepositoryError.
        """
        # Configuración del mock
        project_id = 1
        error_message = "Database connection failed"
        mock_repository_facade.project_assignment.get_assignments_by_project.side_effect = RepositoryError(message=error_message)

        # Ejecución y verificación
        with pytest.raises(RepositoryError, match=error_message):
            await project_queries.get_assignments_by_project(project_id)
        
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    # ===========================================================================
    # Pruebas para get_project_team_summary
    # ===========================================================================

    @pytest.mark.asyncio
    async def test_get_project_team_summary_success(self, project_queries, mock_repository_facade):
        """
        Prueba que se obtiene el resumen del equipo de un proyecto correctamente.
        """
        # Configuración del mock
        project_id = 1
        now = pendulum.now()
        mock_assignments = [
            ProjectAssignment(
                id=1, project_id=project_id, employee_id=101, role_in_project="Developer",
                percentage_allocation=80.0, start_date=now.date(),
                end_date=now.date().add(months=6), is_active=True,
                created_at=now, updated_at=now
            ),
            ProjectAssignment(
                id=2, project_id=project_id, employee_id=102, role_in_project="Designer",
                percentage_allocation=60.0, start_date=now.date().add(months=1),
                end_date=now.date().add(months=5), is_active=True,
                created_at=now, updated_at=now
            ),
        ]
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = mock_assignments

        # Ejecución
        summary = await project_queries.get_project_team_summary(project_id)

        # Verificación
        assert summary["project_id"] == project_id
        assert summary["total_team_members"] == 2
        assert "Developer" in summary["team_composition"]["roles_distribution"]
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_team_summary_no_assignments(self, project_queries, mock_repository_facade):
        """
        Prueba el comportamiento cuando no hay asignaciones para el proyecto.
        """
        # Configuración del mock
        project_id = 2
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = []

        # Ejecución
        summary = await project_queries.get_project_team_summary(project_id)

        # Verificación
        assert summary["project_id"] == project_id
        assert summary["total_team_members"] == 0
        assert summary["team_composition"]["roles_distribution"] == {}
        assert summary["allocation_summary"]["total_allocated_hours"] == 0.0
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_team_summary_invalid_id(self, project_queries):
        """Test con ID de proyecto inválido."""
        project_id = -1
        with pytest.raises(ValidationError, match="ID de proyecto debe ser un entero positivo."):
            await project_queries.get_project_team_summary(project_id)

    @pytest.mark.asyncio
    async def test_get_project_team_summary_repository_error(self, project_queries, mock_repository_facade):
        """
        Prueba el manejo de RepositoryError en get_project_team_summary.
        """
        # Configuración del mock
        project_id = 1
        error_message = "Error fetching assignments"
        mock_repository_facade.project_assignment.get_assignments_by_project.side_effect = RepositoryError(message=error_message)

        # Ejecución y verificación
        with pytest.raises(RepositoryError, match=error_message):
            await project_queries.get_project_team_summary(project_id)
        
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    # ===========================================================================
    # Pruebas para get_project_resource_allocation
    # ===========================================================================

    @pytest.mark.asyncio
    async def test_get_project_resource_allocation_success(self, project_queries, mock_repository_facade):
        """
        Prueba que se obtiene la distribución de recursos de un proyecto correctamente.
        """
        # Configuración del mock
        project_id = 1
        now = pendulum.now()
        mock_assignments = [
            ProjectAssignment(
                id=1, project_id=project_id, employee_id=101, role_in_project="Backend",
                percentage_allocation=100.0, start_date=now.date(),
                created_at=now, updated_at=now
            ),
            ProjectAssignment(
                id=2, project_id=project_id, employee_id=102, role_in_project="Frontend",
                percentage_allocation=50.0, start_date=now.date().add(days=15),
                created_at=now, updated_at=now
            ),
        ]
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = mock_assignments

        # Ejecución
        allocation = await project_queries.get_project_resource_allocation(project_id)

        # Verificación
        assert allocation["project_id"] == project_id
        assert allocation["total_resources"] == 2
        assert "Backend" in allocation["resource_distribution"]["by_role"]
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_resource_allocation_no_assignments(self, project_queries, mock_repository_facade):
        """
        Prueba el caso donde no hay asignaciones para el proyecto.
        """
        # Configuración del mock
        project_id = 2
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = []

        # Ejecución
        allocation = await project_queries.get_project_resource_allocation(project_id)

        # Verificación
        assert allocation["project_id"] == project_id
        assert allocation["total_resources"] == 0
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_resource_allocation_invalid_id(self, project_queries):
        """Test con ID de proyecto inválido."""
        project_id = -1
        with pytest.raises(ValidationError, match="ID de proyecto debe ser un entero positivo."):
            await project_queries.get_project_resource_allocation(project_id)

    @pytest.mark.asyncio
    async def test_get_project_resource_allocation_repository_error(self, project_queries, mock_repository_facade):
        """
        Prueba el manejo de RepositoryError en get_project_resource_allocation.
        """
        # Configuración del mock
        project_id = 1
        error_message = "Failed to fetch data"
        mock_repository_facade.project_assignment.get_assignments_by_project.side_effect = RepositoryError(message=error_message)

        # Ejecución y verificación
        with pytest.raises(RepositoryError, match=error_message):
            await project_queries.get_project_resource_allocation(project_id)
        
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    # ===========================================================================
    # Pruebas para get_project_assignment_timeline
    # ===========================================================================

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_success(self, project_queries, mock_repository_facade):
        """
        Prueba que se genera la línea de tiempo de un proyecto correctamente.
        """
        # Configuración del mock
        project_id = 1
        now = pendulum.now()
        start_date = now.date()
        mock_assignments = [
            ProjectAssignment(
                id=1, project_id=project_id, employee_id=101, role_in_project="Lead",
                start_date=start_date, end_date=now.add(months=6).date(),
                created_at=now, updated_at=now
            ),
            ProjectAssignment(
                id=2, project_id=project_id, employee_id=102, role_in_project="Support",
                start_date=now.add(months=2).date(), end_date=now.add(months=9).date(),
                created_at=now, updated_at=now
            ),
        ]
        # Forzar el mock a ser un AsyncMock que devuelve la lista correcta
        mock_repository_facade.project_assignment.get_assignments_by_project = AsyncMock(return_value=mock_assignments)

        # Ejecución
        timeline = await project_queries.get_project_assignment_timeline(project_id)

        # Verificación
        assert timeline["project_id"] == project_id
        assert len(timeline["timeline_data"]) == 2
        assert timeline["project_span"]["duration_days"] > 0
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_no_assignments(self, project_queries, mock_repository_facade):
        """
        Prueba el caso donde no hay asignaciones para generar la línea de tiempo.
        """
        # Configuración del mock
        project_id = 2
        mock_repository_facade.project_assignment.get_assignments_by_project.return_value = []

        # Ejecución
        timeline = await project_queries.get_project_assignment_timeline(project_id)

        # Verificación
        assert timeline["project_id"] == project_id
        assert timeline["timeline_data"] == []
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_invalid_id(self, project_queries):
        """Test con ID de proyecto inválido."""
        project_id = -1
        with pytest.raises(ValidationError, match="ID de proyecto debe ser un entero positivo."):
            await project_queries.get_project_assignment_timeline(project_id)

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_invalid_date_range(self, project_queries):
        """
        Test: Rango de fechas inválido para línea de tiempo.
        
        Verifica que se lance ValidationError para rangos de fechas inválidos.
        """
        # Crear un mock para el objeto de rango de fechas
        class MockDateRange:
            def __init__(self, start, end):
                self.start_date = start
                self.end_date = end

        invalid_range = MockDateRange(
            start=pendulum.date(2023, 1, 1),
            end=pendulum.date(2022, 12, 31)
        )

        # Act & Assert
        with pytest.raises(ValidationError, match="La fecha de fin debe ser posterior a la fecha de inicio"):
            await project_queries.get_project_assignment_timeline(
                project_id=1,
                date_range=invalid_range
            )

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_repository_error(self, project_queries, mock_repository_facade):
        """
        Prueba el manejo de RepositoryError en get_project_assignment_timeline.
        """
        # Configuración del mock
        project_id = 1
        error_message = "Timeline generation failed"
        mock_repository_facade.project_assignment.get_assignments_by_project.side_effect = RepositoryError(message=error_message)

        # Ejecución y verificación
        with pytest.raises(RepositoryError, match=error_message):
            await project_queries.get_project_assignment_timeline(project_id)
        
        mock_repository_facade.project_assignment.get_assignments_by_project.assert_called_once_with(project_id)