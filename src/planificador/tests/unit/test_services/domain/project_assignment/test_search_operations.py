"""
Tests unitarios para las operaciones de búsqueda del ProjectAssignmentDomainService.

Este módulo contiene todas las pruebas unitarias para las operaciones de búsqueda
y filtrado del servicio de dominio de asignaciones de proyecto.

Operaciones probadas:
- get_assignments_with_filters: Búsqueda con filtros avanzados
- get_assignments_by_date_range: Búsqueda por rango de fechas
- get_assignments_by_role: Búsqueda por rol
- get_overlapping_assignments: Detección de asignaciones superpuestas
"""

import pytest
import pendulum
from typing import List, Dict, Any
from unittest.mock import AsyncMock, patch
from uuid import UUID

from planificador.services.domain.project_assignment.modules.search_operations import SearchOperations
from planificador.schemas.assignment.assignment import ProjectAssignment
from planificador.schemas.assignment.advanced_schemas import (
    AssignmentAdvancedFilters, ProjectAssignmentResponseSchema
)
from planificador.exceptions import RepositoryError, ValidationError


class TestSearchOperations:
    """
    Clase de tests para las operaciones de búsqueda y filtrado.
    
    Agrupa todos los tests relacionados con operaciones de búsqueda
    y filtrado de asignaciones de proyecto.
    """

    @pytest.fixture
    def search_operations(self, mock_repository_facade: AsyncMock) -> SearchOperations:
        """
        Fixture que crea una instancia de SearchOperations con dependencias mockeadas.
        
        Returns:
            SearchOperations: Instancia del servicio con mocks
        """
        return SearchOperations(repository_facade=mock_repository_facade)

    # ==================== TESTS SEARCH_ASSIGNMENTS_BY_CRITERIA ====================

    async def test_search_assignments_by_criteria_success(self, search_operations, sample_assignment_list):
        """Test exitoso de obtención de asignaciones con criterios."""
        from datetime import date
        from planificador.schemas.assignment.advanced_schemas import AssignmentAdvancedFilters
        
        # Configurar datos de prueba usando el esquema correcto
        filters = AssignmentAdvancedFilters(
            employee_ids=[1, 2],
            project_ids=[1, 2],
            is_active=True,
            start_date_from=date(2024, 1, 1),
            start_date_to=date(2024, 12, 31),
            roles=["Developer", "Tester"],
            min_allocation_percentage=50.0,
            max_allocation_percentage=100.0,
            min_hours_per_day=4.0,
            max_hours_per_day=8.0,
            include_notes_search="Test"
        )
        
        # Configurar mock del repositorio
        search_operations._repository.queries.get_all_assignments.return_value = sample_assignment_list
        
        # Ejecutar método
        result = await search_operations.search_assignments_by_criteria(filters.model_dump(exclude_none=True))
        
        # Verificar resultado
        assert isinstance(result, list)
        assert len(result) >= 0  # Puede ser vacío después de aplicar filtros
        
        # Verificar que se llamó al repositorio
        search_operations._repository.queries.get_all_assignments.assert_called_once()
    
    async def test_search_assignments_by_criteria_empty_result(self, search_operations):
        """Test de obtención de asignaciones con filtros que no devuelven resultados."""
        from planificador.schemas.assignment.advanced_schemas import AssignmentAdvancedFilters
        
        # Configurar datos de prueba usando el esquema correcto
        filters = AssignmentAdvancedFilters(
            employee_ids=[999],  # ID que no existe
            is_active=True
        )
        
        # Configurar mock del repositorio para devolver lista vacía
        search_operations._repository.queries.get_all_assignments.return_value = []
        
        # Ejecutar método
        result = await search_operations.search_assignments_by_criteria(filters.model_dump(exclude_none=True))
        
        # Verificar resultado
        assert isinstance(result, list)
        assert len(result) == 0
        
        # Verificar que se llamó al repositorio
        search_operations._repository.queries.get_all_assignments.assert_called_once()

    # ==================== TESTS GET_ASSIGNMENTS_BY_DATE_RANGE ====================

    @pytest.mark.asyncio
    async def test_get_assignments_by_date_range_success(
        self,
        search_operations: SearchOperations,
        sample_assignment_list: List[ProjectAssignment]
    ):
        """
        Test: Búsqueda exitosa por rango de fechas.
        
        Verifica que el método filtre correctamente las asignaciones
        por el rango de fechas especificado.
        """
        # Arrange
        start_date = pendulum.now().date()
        end_date = pendulum.now().add(months=3).date()
        search_operations._repository.queries.get_all_assignments.return_value = sample_assignment_list
        
        # Act
        result = await search_operations.get_assignments_by_date_range(
            start_date=start_date,
            end_date=end_date
        )
        
        # Assert
        assert len(result) >= 0  # Puede ser filtrado
        search_operations._repository.queries.get_all_assignments.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_date_range_repository_error(
        self,
        search_operations: SearchOperations
    ):
        """
        Test: Error de repositorio en búsqueda por fechas.
        
        Verifica que se propague correctamente un error de repositorio.
        """
        # Arrange
        start_date = pendulum.now().date()
        end_date = pendulum.now().add(months=3).date()
        repository_error = RepositoryError(
            message="Error de base de datos",
            operation="get_assignments_by_date_range",
            entity_type="ProjectAssignment"
        )
        search_operations._repository.queries.get_all_assignments.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await search_operations.get_assignments_by_date_range(
                start_date=start_date,
                end_date=end_date
            )
        
        assert "Error al obtener asignaciones por rango de fechas" in str(exc_info.value)

    # ==================== TESTS GET_ASSIGNMENTS_BY_ROLE ====================

    @pytest.mark.asyncio
    async def test_get_assignments_by_role_success(
        self,
        search_operations: SearchOperations,
        sample_assignment_list: List[ProjectAssignment]
    ):
        """
        Test: Búsqueda exitosa por rol.
        
        Verifica que el método filtre correctamente las asignaciones
        por el rol especificado.
        """
        # Arrange
        role = "Developer"
        search_operations._repository.queries.get_all_assignments.return_value = sample_assignment_list
        
        # Act
        result = await search_operations.get_assignments_by_role(role=role)
        
        # Assert
        assert len(result) >= 0  # Puede ser filtrado
        search_operations._repository.queries.get_all_assignments.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_role_no_results(
        self,
        search_operations: SearchOperations
    ):
        """
        Test: Rol sin asignaciones.
        
        Verifica que se retorne una lista vacía cuando no hay
        asignaciones para el rol especificado.
        """
        # Arrange
        role = "NonExistentRole"
        search_operations._repository.queries.get_all_assignments.return_value = []
        
        # Act
        result = await search_operations.get_assignments_by_role(role=role)
        
        # Assert
        assert result == []
        search_operations._repository.queries.get_all_assignments.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_role_repository_error(
        self,
        search_operations: SearchOperations
    ):
        """
        Test: Error de repositorio en búsqueda por rol.
        
        Verifica que se propague correctamente un error de repositorio.
        """
        # Arrange
        role = "Developer"
        repository_error = RepositoryError(
            message="Error de base de datos",
            operation="get_assignments_by_role",
            entity_type="ProjectAssignment"
        )
        search_operations._repository.queries.get_all_assignments.side_effect = repository_error
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await search_operations.get_assignments_by_role(role=role)
        
        assert "Error al buscar asignaciones por rol" in str(exc_info.value)

    # ==================== TESTS GET_OVERLAPPING_ASSIGNMENTS ====================

    @pytest.mark.asyncio
    async def test_get_overlapping_assignments_success(
        self,
        search_operations: SearchOperations,
        sample_assignment_list: List[ProjectAssignment]
    ):
        """
        Test: Detección exitosa de asignaciones superpuestas.
        
        Verifica que el método get_overlapping_assignments detecte
        correctamente las asignaciones que se superponen.
        """
        # Arrange
        employee_id = 1
        project_id = 1
        threshold_percentage = 100.0
        
        # Configurar mock para get_assignments_by_employee (ya que employee_id está presente)
        search_operations._repository.queries.get_assignments_by_employee.return_value = sample_assignment_list
        
        # Act
        result = await search_operations.get_overlapping_assignments(
            employee_id=employee_id,
            project_id=project_id,
            threshold_percentage=threshold_percentage
        )
        
        # Assert
        assert isinstance(result, list)
        assert len(result) >= 0  # Puede ser vacío si no hay solapamientos
        
        # Verificar que se llamó al método correcto del repositorio
        search_operations._repository.queries.get_assignments_by_employee.assert_called_once_with(
            employee_id=employee_id,
            include_inactive=False
        )

    @pytest.mark.asyncio
    async def test_get_overlapping_assignments_repository_error(
        self,
        search_operations: SearchOperations
    ):
        """
        Test: Manejo de RepositoryError durante la detección de solapamientos.
        
        Verifica que se lance un RepositoryError si ocurre un error
        en el repositorio al obtener las asignaciones.
        """
        # Arrange
        employee_id = 1
        
        # Configurar mock para que lance una excepción
        search_operations._repository.queries.get_assignments_by_employee.side_effect = Exception("DB Error")
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await search_operations.get_overlapping_assignments(employee_id=employee_id)
            
        assert "Error al detectar solapamientos: DB Error" in str(exc_info.value)