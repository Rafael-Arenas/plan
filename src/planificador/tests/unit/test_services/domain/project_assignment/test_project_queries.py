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
from unittest.mock import AsyncMock, patch
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
    def project_queries(self, mock_repository_facade: AsyncMock) -> ProjectQueries:
        """
        Fixture que crea una instancia de ProjectQueries con dependencias mockeadas.
        
        Returns:
            ProjectQueries: Instancia del servicio con mocks
        """
        return ProjectQueries(repository_facade=mock_repository_facade)

    # ==================== TESTS GET_ASSIGNMENTS_BY_PROJECT ====================

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_success(
        self,
        project_queries: ProjectQueries,
        sample_project_id: int,
        sample_assignment_list: List[ProjectAssignment]
    ):
        """
        Test: Obtención exitosa de asignaciones por proyecto.
        
        Verifica que el método get_assignments_by_project retorne
        correctamente las asignaciones del proyecto especificado.
        """
        # Arrange
        project_queries._repository.get_assignments_by_project.return_value = sample_assignment_list
        
        # Act
        result = await project_queries.get_assignments_by_project(sample_project_id)
        
        # Assert
        assert result == sample_assignment_list
        project_queries._repository.get_assignments_by_project.assert_called_once_with(project_id=sample_project_id)

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_empty_result(
        self, project_queries, sample_project_id
    ):
        """Test obtener asignaciones por proyecto con resultado vacío."""
        # Configurar mock
        project_queries._repository.get_assignments_by_project.return_value = []
        
        # Ejecutar
        result = await project_queries.get_assignments_by_project(sample_project_id)
        
        # Verificar
        assert result == []
        project_queries._repository.get_assignments_by_project.assert_called_once_with(
            project_id=sample_project_id
        )

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_invalid_id(
        self,
        project_queries: ProjectQueries
    ):
        """
        Test: ID de proyecto inválido.
        
        Verifica que se lance ValidationError para IDs inválidos.
        """
        # Arrange
        invalid_project_id = -1
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await project_queries.get_assignments_by_project(
                project_id=invalid_project_id,
                include_inactive=False
            )
        
        assert "ID de proyecto debe ser positivo" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_assignments_by_project_repository_error(
        self, project_queries, sample_project_id
    ):
        """Test manejo de error del repositorio."""
        # Configurar mock para lanzar excepción
        project_queries._repository.get_assignments_by_project.side_effect = RepositoryError(
            message="Error de base de datos",
            operation="get_assignments_by_project",
            entity_type="ProjectAssignment"
        )
        
        # Verificar que se propague la excepción
        with pytest.raises(RepositoryError):
            await project_queries.get_assignments_by_project(sample_project_id)

    # ==================== TESTS GET_PROJECT_TEAM_SUMMARY ====================

    @pytest.mark.asyncio
    async def test_get_project_team_summary(
        self, project_queries, sample_project_id, sample_assignment_list
    ):
        """Test obtener resumen del equipo del proyecto."""
        # Configurar mock
        project_queries._repository.get_assignments_by_project.return_value = sample_assignment_list
        
        # Ejecutar
        result = await project_queries.get_project_team_summary(sample_project_id)
        
        # Verificar estructura del resultado
        assert isinstance(result, dict)
        assert "project_id" in result
        assert "total_members" in result
        assert "team_composition" in result
        assert result["project_id"] == sample_project_id

    @pytest.mark.asyncio
    async def test_get_project_team_summary_no_assignments(
        self,
        project_queries: ProjectQueries,
        sample_project_id: int
    ):
        """
        Test: Resumen de equipo para proyecto sin asignaciones.
        
        Verifica que se genere un resumen vacío para proyectos
        sin asignaciones.
        """
        # Arrange
        project_queries._repository.get_assignments_by_project.return_value = []
        project_queries._repository.project_exists.return_value = True
        project_queries._repository.get_project_basic_info.return_value = {"name": "Empty Project"}
        
        # Act
        result = await project_queries.get_project_team_summary(sample_project_id)
        
        # Assert
        assert isinstance(result, dict)
        assert result["project_id"] == sample_project_id
        assert result["total_members"] == 0
        assert len(result["team_composition"]) == 0
        
        # Verificar que se llamaron los métodos correctos
        project_queries._repository.get_assignments_by_project.assert_called_once_with(
            project_id=sample_project_id, active_only=True
        )
        project_queries._repository.project_exists.assert_called_once_with(sample_project_id)
        project_queries._repository.get_project_basic_info.assert_called_once_with(sample_project_id)

    # ==================== TESTS GET_PROJECT_RESOURCE_ALLOCATION ====================

    @pytest.mark.asyncio
    async def test_get_project_resource_allocation(
        self, project_queries, sample_project_id, sample_assignment_list
    ):
        """Test obtener asignación de recursos del proyecto."""
        # Configurar mock
        project_queries._repository.get_assignments_by_project.return_value = sample_assignment_list
        
        # Ejecutar
        result = await project_queries.get_project_resource_allocation(sample_project_id)
        
        # Verificar estructura del resultado
        assert isinstance(result, dict)
        assert "project_id" in result
        assert "total_allocation" in result
        assert "resource_distribution" in result

    # ==================== TESTS GET_PROJECT_ASSIGNMENT_TIMELINE ====================

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_success(
        self, project_queries, sample_project_id, sample_assignment_list
    ):
        """Test obtener timeline del proyecto."""
        # Configurar mock
        project_queries._repository.get_assignments_by_project.return_value = sample_assignment_list
        
        # Ejecutar
        result = await project_queries.get_project_assignment_timeline(sample_project_id)
        
        # Verificar estructura del resultado
        assert isinstance(result, dict)
        assert "project_id" in result
        assert "timeline_events" in result

    @pytest.mark.asyncio
    async def test_get_project_assignment_timeline_invalid_date_range(
        self,
        project_queries: ProjectQueries,
        sample_project_id: int
    ):
        """
        Test: Rango de fechas inválido para línea de tiempo.
        
        Verifica que se lance ValidationError para rangos de fechas inválidos.
        """
        # Arrange
        start_date = pendulum.now().date()
        end_date = start_date.subtract(days=1)  # Fecha fin anterior a fecha inicio
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await project_queries.get_project_assignment_timeline(
                project_id=sample_project_id,
                start_date=start_date,
                end_date=end_date
            )
        
        assert "La fecha de fin debe ser posterior a la fecha de inicio" in str(exc_info.value)

    # ==================== TESTS MÉTODOS PRIVADOS ====================

    @pytest.mark.asyncio
    async def test_validate_project_id_valid(self, project_queries: ProjectQueries):
        """
        Test: Validación exitosa de ID de proyecto.
        
        Verifica que no se lance excepción para IDs válidos.
        """
        # Act & Assert - No debe lanzar excepción
        project_queries._validate_project_id(1)
        project_queries._validate_project_id(999)

    @pytest.mark.asyncio
    async def test_validate_project_id_invalid(self, project_queries: ProjectQueries):
        """
        Test: Validación fallida de ID de proyecto.
        
        Verifica que se lance ValidationError para IDs inválidos.
        """
        # Act & Assert
        with pytest.raises(ValidationError):
            project_queries._validate_project_id(0)
        
        with pytest.raises(ValidationError):
            project_queries._validate_project_id(-1)

    @pytest.mark.asyncio
    async def test_validate_date_range_valid(self, project_queries: ProjectQueries):
        """
        Test: Validación exitosa de rango de fechas.
        
        Verifica que no se lance excepción para rangos válidos.
        """
        # Arrange
        start_date = pendulum.now().date()
        end_date = start_date.add(days=30)
        
        # Act & Assert - No debe lanzar excepción
        project_queries._validate_date_range(start_date, end_date)

    @pytest.mark.asyncio
    async def test_validate_date_range_invalid(self, project_queries: ProjectQueries):
        """
        Test: Validación fallida de rango de fechas.
        
        Verifica que se lance ValidationError para rangos inválidos.
        """
        # Arrange
        start_date = pendulum.now().date()
        end_date = start_date.subtract(days=1)
        
        # Act & Assert
        with pytest.raises(ValidationError):
            project_queries._validate_date_range(start_date, end_date)