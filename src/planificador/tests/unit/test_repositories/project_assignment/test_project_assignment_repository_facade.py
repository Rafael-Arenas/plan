"""Pruebas unitarias para ProjectAssignmentRepositoryFacade.

Este módulo contiene pruebas exhaustivas para validar la funcionalidad del facade
de asignaciones de proyecto, cubriendo todos los escenarios críticos de:
- Operaciones CRUD
- Consultas y filtros
- Operaciones de relaciones
- Estadísticas y métricas
- Validaciones de negocio
"""

from datetime import date
from unittest.mock import AsyncMock, MagicMock

import pytest
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models import ProjectAssignment
from planificador.repositories.project_assignment import ProjectAssignmentRepositoryFacade
from planificador.schemas.assignment.assignment import ProjectAssignmentCreate, ProjectAssignmentUpdate


class TestProjectAssignmentRepositoryFacade:
    """Pruebas para la inicialización y configuración del facade."""

    def test_facade_initialization(self, mock_session: AsyncMock):
        """Prueba que el facade se inicializa correctamente con todos los módulos."""
        facade = ProjectAssignmentRepositoryFacade(mock_session)
        
        # Verificar que la sesión se asigna correctamente
        assert facade._session == mock_session
        
        # Verificar que todos los módulos se inicializan
        assert hasattr(facade, '_crud_operations')
        assert hasattr(facade, '_query_operations')
        assert hasattr(facade, '_relationship_operations')
        assert hasattr(facade, '_statistics_operations')
        assert hasattr(facade, '_validation_operations')
        
        # Verificar que el logger se configura
        assert hasattr(facade, '_logger')


class TestCrudOperations:
    """Pruebas para las operaciones CRUD del facade."""

    @pytest.mark.asyncio
    async def test_create_assignment_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_create: ProjectAssignmentCreate
    ):
        """Prueba la creación exitosa de una asignación."""
        # Configurar mock
        expected_assignment = MagicMock(spec=ProjectAssignment)
        project_assignment_repository._crud_operations.create_assignment = AsyncMock(
            return_value=expected_assignment
        )
        
        # Ejecutar
        result = await project_assignment_repository.create_assignment(sample_assignment_create)
        
        # Verificar
        assert result == expected_assignment
        project_assignment_repository._crud_operations.create_assignment.assert_called_once_with(
            sample_assignment_create
        )

    @pytest.mark.asyncio
    async def test_update_assignment_success(
        self,
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_update: ProjectAssignmentUpdate
    ):
        """Prueba la actualización exitosa de una asignación."""
        # Configurar mock
        assignment_id = 1
        expected_assignment = MagicMock(spec=ProjectAssignment)
        project_assignment_repository._crud_operations.update_assignment = AsyncMock(
            return_value=expected_assignment
        )
        
        # Ejecutar
        result = await project_assignment_repository.update_assignment(
            assignment_id, sample_assignment_update
        )
        
        # Verificar
        assert result == expected_assignment
        project_assignment_repository._crud_operations.update_assignment.assert_called_once_with(
            assignment_id, sample_assignment_update
        )

    @pytest.mark.asyncio
    async def test_update_assignment_not_found(
        self,
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_update: ProjectAssignmentUpdate
    ):
        """Prueba la actualización de una asignación que no existe."""
        # Configurar mock
        assignment_id = 999
        project_assignment_repository._crud_operations.update_assignment = AsyncMock(
            return_value=None
        )
        
        # Ejecutar
        result = await project_assignment_repository.update_assignment(
            assignment_id, sample_assignment_update
        )
        
        # Verificar
        assert result is None
        project_assignment_repository._crud_operations.update_assignment.assert_called_once_with(
            assignment_id, sample_assignment_update
        )

    @pytest.mark.asyncio
    async def test_delete_assignment_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la eliminación exitosa de una asignación."""
        # Configurar mock
        assignment_id = 1
        project_assignment_repository._crud_operations.delete_assignment = AsyncMock(
            return_value=True
        )
        
        # Ejecutar
        result = await project_assignment_repository.delete_assignment(assignment_id)
        
        # Verificar
        assert result is True
        project_assignment_repository._crud_operations.delete_assignment.assert_called_once_with(
            assignment_id
        )

    @pytest.mark.asyncio
    async def test_delete_assignment_not_found(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la eliminación de una asignación que no existe."""
        # Configurar mock
        assignment_id = 999
        project_assignment_repository._crud_operations.delete_assignment = AsyncMock(
            return_value=False
        )
        
        # Ejecutar
        result = await project_assignment_repository.delete_assignment(assignment_id)
        
        # Verificar
        assert result is False
        project_assignment_repository._crud_operations.delete_assignment.assert_called_once_with(
            assignment_id
        )

    @pytest.mark.asyncio
    async def test_get_assignment_by_id_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención exitosa de una asignación por ID."""
        # Configurar mock
        assignment_id = 1
        expected_assignment = MagicMock(spec=ProjectAssignment)
        project_assignment_repository._crud_operations.get_assignment_by_id = AsyncMock(
            return_value=expected_assignment
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignment_by_id(assignment_id)
        
        # Verificar
        assert result == expected_assignment
        project_assignment_repository._crud_operations.get_assignment_by_id.assert_called_once_with(
            assignment_id
        )

    @pytest.mark.asyncio
    async def test_get_assignment_by_id_not_found(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de una asignación que no existe."""
        # Configurar mock
        assignment_id = 999
        project_assignment_repository._crud_operations.get_assignment_by_id = AsyncMock(
            return_value=None
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignment_by_id(assignment_id)
        
        # Verificar
        assert result is None
        project_assignment_repository._crud_operations.get_assignment_by_id.assert_called_once_with(
            assignment_id
        )


class TestQueryOperations:
    """Pruebas para las operaciones de consulta del facade."""

    @pytest.mark.asyncio
    async def test_get_all_assignments_default_params(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de todas las asignaciones con parámetros por defecto."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(3)]
        project_assignment_repository._query_operations.get_all_assignments = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_all_assignments()
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_all_assignments.assert_called_once_with(
            None, 0
        )

    @pytest.mark.asyncio
    async def test_get_all_assignments_with_pagination(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de todas las asignaciones con paginación."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(2)]
        project_assignment_repository._query_operations.get_all_assignments = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_all_assignments(limit=10, offset=5)
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_all_assignments.assert_called_once_with(
            10, 5
        )

    @pytest.mark.asyncio
    async def test_get_assignments_by_employee(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones por empleado."""
        # Configurar mock
        employee_id = 1
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(2)]
        project_assignment_repository._query_operations.get_assignments_by_employee = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_employee(employee_id)
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_assignments_by_employee.assert_called_once_with(
            employee_id
        )

    @pytest.mark.asyncio
    async def test_get_assignments_by_project(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones por proyecto."""
        # Configurar mock
        project_id = 1
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(3)]
        project_assignment_repository._query_operations.get_assignments_by_project = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_project(project_id)
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_assignments_by_project.assert_called_once_with(
            project_id
        )

    @pytest.mark.asyncio
    async def test_get_active_assignments(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones activas."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(5)]
        project_assignment_repository._query_operations.get_active_assignments = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_active_assignments()
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_active_assignments.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_date_range(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_date_range: tuple[date, date]
    ):
        """Prueba la obtención de asignaciones por rango de fechas."""
        # Configurar mock
        start_date, end_date = sample_date_range
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(4)]
        project_assignment_repository._query_operations.get_assignments_by_date_range = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_date_range(
            start_date, end_date
        )
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_assignments_by_date_range.assert_called_once_with(
            start_date, end_date
        )

    @pytest.mark.asyncio
    async def test_get_assignments_by_role(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones por rol."""
        # Configurar mock
        role = "Developer"
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(3)]
        project_assignment_repository._query_operations.get_assignments_by_role = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_role(role)
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_assignments_by_role.assert_called_once_with(
            role
        )

    @pytest.mark.asyncio
    async def test_get_assignments_with_filters_all_params(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones con todos los filtros."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(2)]
        project_assignment_repository._query_operations.get_assignments_with_filters = AsyncMock(
            return_value=expected_assignments
        )
        
        # Parámetros de prueba
        filters = {
            "employee_id": 1,
            "project_id": 2,
            "status": "active",
            "role": "Developer",
            "start_date": date(2024, 1, 1),
            "end_date": date(2024, 12, 31),
            "allocation_category": "full_time",
            "limit": 10,
            "offset": 0
        }
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_with_filters(**filters)
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_assignments_with_filters.assert_called_once_with(
            **filters
        )

    @pytest.mark.asyncio
    async def test_get_overlapping_assignments(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones superpuestas."""
        # Configurar mock
        employee_id = 1
        start_date = date(2024, 6, 1)
        end_date = date(2024, 8, 31)
        exclude_id = 5
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(1)]
        project_assignment_repository._query_operations.get_overlapping_assignments = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_overlapping_assignments(
            employee_id, start_date, end_date, exclude_id
        )
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._query_operations.get_overlapping_assignments.assert_called_once_with(
            employee_id, start_date, end_date, exclude_id
        )

    @pytest.mark.asyncio
    async def test_get_assignments_with_employee_data(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones con datos del empleado."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(3)]
        project_assignment_repository._relationship_operations.get_assignments_with_employee_data = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_with_employee_data(
            limit=20, offset=10
        )
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._relationship_operations.get_assignments_with_employee_data.assert_called_once_with(
            20, 10
        )

    @pytest.mark.asyncio
    async def test_get_assignments_with_project_data(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones con datos del proyecto."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(4)]
        project_assignment_repository._relationship_operations.get_assignments_with_project_data = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_with_project_data()
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._relationship_operations.get_assignments_with_project_data.assert_called_once_with(
            None, 0
        )

    @pytest.mark.asyncio
    async def test_get_assignments_with_full_data(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de asignaciones con datos completos."""
        # Configurar mock
        expected_assignments = [MagicMock(spec=ProjectAssignment) for _ in range(2)]
        project_assignment_repository._relationship_operations.get_assignments_with_full_data = AsyncMock(
            return_value=expected_assignments
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_with_full_data(
            limit=5, offset=2
        )
        
        # Verificar
        assert result == expected_assignments
        project_assignment_repository._relationship_operations.get_assignments_with_full_data.assert_called_once_with(
            5, 2
        )


class TestRelationshipOperations:
    """Pruebas para las operaciones de relaciones del facade."""

    @pytest.mark.asyncio
    async def test_transfer_employee_assignments_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la transferencia exitosa de asignaciones entre empleados."""
        # Configurar mock
        from_employee_id = 1
        to_employee_id = 2
        project_id = None
        project_assignment_repository._relationship_operations.transfer_employee_assignments = AsyncMock(
            return_value=True
        )
        
        # Ejecutar
        result = await project_assignment_repository.transfer_employee_assignments(
            from_employee_id, to_employee_id, project_id
        )
        
        # Verificar
        assert result is True
        project_assignment_repository._relationship_operations.transfer_employee_assignments.assert_called_once_with(
            from_employee_id, to_employee_id, project_id
        )

    @pytest.mark.asyncio
    async def test_transfer_employee_assignments_with_project(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la transferencia de asignaciones entre empleados para un proyecto específico."""
        # Configurar mock
        from_employee_id = 1
        to_employee_id = 2
        project_id = 3
        project_assignment_repository._relationship_operations.transfer_employee_assignments = AsyncMock(
            return_value=True
        )
        
        # Ejecutar
        result = await project_assignment_repository.transfer_employee_assignments(
            from_employee_id, to_employee_id, project_id
        )
        
        # Verificar
        assert result is True
        project_assignment_repository._relationship_operations.transfer_employee_assignments.assert_called_once_with(
            from_employee_id, to_employee_id, project_id
        )

    @pytest.mark.asyncio
    async def test_reassign_project_assignments_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la reasignación exitosa de asignaciones entre proyectos."""
        # Configurar mock
        from_project_id = 1
        to_project_id = 2
        employee_id = None
        project_assignment_repository._relationship_operations.reassign_project_assignments = AsyncMock(
            return_value=True
        )
        
        # Ejecutar
        result = await project_assignment_repository.reassign_project_assignments(
            from_project_id, to_project_id, employee_id
        )
        
        # Verificar
        assert result is True
        project_assignment_repository._relationship_operations.reassign_project_assignments.assert_called_once_with(
            from_project_id, to_project_id, employee_id
        )

    @pytest.mark.asyncio
    async def test_reassign_project_assignments_with_employee(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la reasignación de asignaciones entre proyectos para un empleado específico."""
        # Configurar mock
        from_project_id = 1
        to_project_id = 2
        employee_id = 3
        project_assignment_repository._relationship_operations.reassign_project_assignments = AsyncMock(
            return_value=True
        )
        
        # Ejecutar
        result = await project_assignment_repository.reassign_project_assignments(
            from_project_id, to_project_id, employee_id
        )
        
        # Verificar
        assert result is True
        project_assignment_repository._relationship_operations.reassign_project_assignments.assert_called_once_with(
            from_project_id, to_project_id, employee_id
        )

    @pytest.mark.asyncio
    async def test_get_employee_workload_summary(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del resumen de carga de trabajo del empleado."""
        # Configurar mock
        employee_id = 1
        expected_summary = {
            "employee_id": employee_id,
            "total_assignments": 3,
            "active_assignments": 2,
            "total_allocation_percentage": 150.0,
            "unique_projects": 2,
            "unique_roles": ["Developer", "Lead"]
        }
        project_assignment_repository._relationship_operations.get_employee_workload_summary = AsyncMock(
            return_value=expected_summary
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_employee_workload_summary(employee_id)
        
        # Verificar
        assert result == expected_summary
        project_assignment_repository._relationship_operations.get_employee_workload_summary.assert_called_once_with(
            employee_id
        )

    @pytest.mark.asyncio
    async def test_get_project_team_summary(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del resumen del equipo del proyecto."""
        # Configurar mock
        project_id = 1
        expected_summary = {
            "project_id": project_id,
            "total_assignments": 5,
            "active_assignments": 4,
            "unique_employees": 3,
            "unique_roles": ["Developer", "Lead", "Tester"],
            "total_allocation_percentage": 320.0
        }
        project_assignment_repository._relationship_operations.get_project_team_summary = AsyncMock(
            return_value=expected_summary
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_project_team_summary(project_id)
        
        # Verificar
        assert result == expected_summary
        project_assignment_repository._relationship_operations.get_project_team_summary.assert_called_once_with(
            project_id
        )


class TestStatisticsOperations:
    """Pruebas para las operaciones de estadísticas del facade."""

    @pytest.mark.asyncio
    async def test_get_total_assignments_count(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del conteo total de asignaciones."""
        # Configurar mock
        expected_count = 42
        project_assignment_repository._statistics_operations.get_total_assignments_count = AsyncMock(
            return_value=expected_count
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_total_assignments_count()
        
        # Verificar
        assert result == expected_count
        project_assignment_repository._statistics_operations.get_total_assignments_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_active_assignments_count(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del conteo de asignaciones activas."""
        # Configurar mock
        expected_count = 28
        project_assignment_repository._statistics_operations.get_active_assignments_count = AsyncMock(
            return_value=expected_count
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_active_assignments_count()
        
        # Verificar
        assert result == expected_count
        project_assignment_repository._statistics_operations.get_active_assignments_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_status_count(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del conteo de asignaciones por estado."""
        # Configurar mock
        expected_counts = {
            "active": 25,
            "completed": 15,
            "cancelled": 2
        }
        project_assignment_repository._statistics_operations.get_assignments_by_status_count = AsyncMock(
            return_value=expected_counts
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_status_count()
        
        # Verificar
        assert result == expected_counts
        project_assignment_repository._statistics_operations.get_assignments_by_status_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignments_by_allocation_category_count(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención del conteo de asignaciones por categoría de asignación."""
        # Configurar mock
        expected_counts = {
            "full_time": 20,
            "part_time": 15,
            "contractor": 7
        }
        project_assignment_repository._statistics_operations.get_assignments_by_allocation_category_count = AsyncMock(
            return_value=expected_counts
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignments_by_allocation_category_count()
        
        # Verificar
        assert result == expected_counts
        project_assignment_repository._statistics_operations.get_assignments_by_allocation_category_count.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_employee_assignment_stats(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de asignaciones por empleado."""
        # Configurar mock
        employee_id = 1
        expected_stats = {
            "employee_id": employee_id,
            "total_assignments": 8,
            "active_assignments": 3,
            "completed_assignments": 5,
            "average_allocation_percentage": 75.5,
            "total_projects": 4
        }
        project_assignment_repository._statistics_operations.get_employee_assignment_stats = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_employee_assignment_stats(employee_id)
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_employee_assignment_stats.assert_called_once_with(
            employee_id
        )

    @pytest.mark.asyncio
    async def test_get_project_assignment_stats(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de asignaciones por proyecto."""
        # Configurar mock
        project_id = 1
        expected_stats = {
            "project_id": project_id,
            "total_assignments": 12,
            "active_assignments": 8,
            "completed_assignments": 4,
            "unique_employees": 6,
            "average_allocation_percentage": 82.3
        }
        project_assignment_repository._statistics_operations.get_project_assignment_stats = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_project_assignment_stats(project_id)
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_project_assignment_stats.assert_called_once_with(
            project_id
        )

    @pytest.mark.asyncio
    async def test_get_assignment_duration_stats(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de duración de asignaciones."""
        # Configurar mock
        expected_stats = {
            "average_duration_days": 180.5,
            "min_duration_days": 30,
            "max_duration_days": 365,
            "median_duration_days": 150
        }
        project_assignment_repository._statistics_operations.get_assignment_duration_stats = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignment_duration_stats()
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_assignment_duration_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_workload_distribution_stats(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de distribución de carga de trabajo."""
        # Configurar mock
        expected_stats = {
            "total_employees": 25,
            "overloaded_employees": 3,
            "underutilized_employees": 5,
            "optimal_load_employees": 17,
            "average_workload_percentage": 78.2
        }
        project_assignment_repository._statistics_operations.get_workload_distribution_stats = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_workload_distribution_stats()
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_workload_distribution_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_assignment_trends(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de tendencias de asignaciones."""
        # Configurar mock
        days = 60
        expected_trends = [
            {"date": "2024-01-01", "new_assignments": 3, "completed_assignments": 1},
            {"date": "2024-01-02", "new_assignments": 2, "completed_assignments": 0},
            {"date": "2024-01-03", "new_assignments": 1, "completed_assignments": 2}
        ]
        project_assignment_repository._statistics_operations.get_assignment_trends = AsyncMock(
            return_value=expected_trends
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_assignment_trends(days)
        
        # Verificar
        assert result == expected_trends
        project_assignment_repository._statistics_operations.get_assignment_trends.assert_called_once_with(
            days
        )

    @pytest.mark.asyncio
    async def test_get_overlap_statistics(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de superposición."""
        # Configurar mock
        expected_stats = {
            "total_overlaps": 15,
            "employees_with_overlaps": 8,
            "average_overlaps_per_employee": 1.9,
            "max_overlaps_single_employee": 4
        }
        project_assignment_repository._statistics_operations.get_overlap_statistics = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_overlap_statistics()
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_overlap_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_role_distribution_stats(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de estadísticas de distribución por roles."""
        # Configurar mock
        expected_stats = {
            "Developer": 25,
            "Lead": 8,
            "Tester": 12,
            "Analyst": 6
        }
        project_assignment_repository._statistics_operations.get_role_distribution_stats = AsyncMock(
            return_value=expected_stats
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_role_distribution_stats()
        
        # Verificar
        assert result == expected_stats
        project_assignment_repository._statistics_operations.get_role_distribution_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_comprehensive_dashboard_metrics(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la obtención de métricas completas del dashboard."""
        # Configurar mock
        expected_metrics = {
            "total_assignments": 150,
            "active_assignments": 95,
            "total_employees": 30,
            "total_projects": 12,
            "average_allocation": 76.8,
            "workload_distribution": {
                "overloaded": 4,
                "optimal": 22,
                "underutilized": 4
            },
            "role_distribution": {
                "Developer": 25,
                "Lead": 8,
                "Tester": 12
            }
        }
        project_assignment_repository._statistics_operations.get_comprehensive_dashboard_metrics = AsyncMock(
            return_value=expected_metrics
        )
        
        # Ejecutar
        result = await project_assignment_repository.get_comprehensive_dashboard_metrics()
        
        # Verificar
        assert result == expected_metrics
        project_assignment_repository._statistics_operations.get_comprehensive_dashboard_metrics.assert_called_once()


class TestValidationOperations:
    """Pruebas para las operaciones de validación del facade."""

    @pytest.mark.asyncio
    async def test_validate_assignment_data_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_data: dict
    ):
        """Prueba la validación exitosa de datos de asignación."""
        # Configurar mock
        exclude_id = None
        project_assignment_repository._validation_operations.validate_assignment_data = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_assignment_data(
            sample_assignment_data, exclude_id
        )
        
        # Verificar
        project_assignment_repository._validation_operations.validate_assignment_data.assert_called_once_with(
            sample_assignment_data, exclude_id
        )

    def test_validate_required_fields_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_data: dict
    ):
        """Prueba la validación exitosa de campos requeridos."""
        # Configurar mock
        project_assignment_repository._validation_operations.validate_required_fields = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_required_fields(sample_assignment_data)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_required_fields.assert_called_once_with(
            sample_assignment_data
        )

    def test_validate_date_range_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_date_range: tuple[date, date]
    ):
        """Prueba la validación exitosa de rango de fechas."""
        # Configurar mock
        start_date, end_date = sample_date_range
        project_assignment_repository._validation_operations.validate_date_range = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_date_range(start_date, end_date)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_date_range.assert_called_once_with(
            start_date, end_date
        )

    def test_validate_allocation_percentage_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de porcentaje de asignación."""
        # Configurar mock
        allocation_percentage = 80.0
        project_assignment_repository._validation_operations.validate_allocation_percentage = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_allocation_percentage(allocation_percentage)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_allocation_percentage.assert_called_once_with(
            allocation_percentage
        )

    def test_validate_hours_per_day_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de horas por día."""
        # Configurar mock
        hours_per_day = 8.0
        project_assignment_repository._validation_operations.validate_hours_per_day = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_hours_per_day(hours_per_day)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_hours_per_day.assert_called_once_with(
            hours_per_day
        )

    @pytest.mark.asyncio
    async def test_validate_employee_exists_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de existencia del empleado."""
        # Configurar mock
        employee_id = 1
        project_assignment_repository._validation_operations.validate_employee_exists = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_employee_exists(employee_id)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_employee_exists.assert_called_once_with(
            employee_id
        )

    @pytest.mark.asyncio
    async def test_validate_project_exists_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de existencia del proyecto."""
        # Configurar mock
        project_id = 1
        project_assignment_repository._validation_operations.validate_project_exists = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_project_exists(project_id)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_project_exists.assert_called_once_with(
            project_id
        )

    @pytest.mark.asyncio
    async def test_validate_no_overlapping_assignments_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de no superposición de asignaciones."""
        # Configurar mock
        employee_id = 1
        start_date = date(2024, 6, 1)
        end_date = date(2024, 8, 31)
        exclude_id = 5
        project_assignment_repository._validation_operations.validate_no_overlapping_assignments = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_no_overlapping_assignments(
            employee_id, start_date, end_date, exclude_id
        )
        
        # Verificar
        project_assignment_repository._validation_operations.validate_no_overlapping_assignments.assert_called_once_with(
            employee_id, start_date, end_date, exclude_id
        )

    @pytest.mark.asyncio
    async def test_validate_workload_limits_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de límites de carga de trabajo."""
        # Configurar mock
        employee_id = 1
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        allocation_percentage = 80.0
        project_assignment_repository._validation_operations.validate_workload_limits = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_workload_limits(
            employee_id, start_date, end_date, allocation_percentage
        )
        
        # Verificar
        project_assignment_repository._validation_operations.validate_workload_limits.assert_called_once_with(
            employee_id, start_date, end_date, allocation_percentage
        )

    @pytest.mark.asyncio
    async def test_validate_assignment_deletion_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de eliminación de asignación."""
        # Configurar mock
        assignment_id = 1
        project_assignment_repository._validation_operations.validate_assignment_deletion = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_assignment_deletion(assignment_id)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_assignment_deletion.assert_called_once_with(
            assignment_id
        )

    @pytest.mark.asyncio
    async def test_validate_business_rules_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_data: dict
    ):
        """Prueba la validación exitosa de reglas de negocio."""
        # Configurar mock
        exclude_id = None
        project_assignment_repository._validation_operations.validate_business_rules = AsyncMock()
        
        # Ejecutar
        await project_assignment_repository.validate_business_rules(
            sample_assignment_data, exclude_id
        )
        
        # Verificar
        project_assignment_repository._validation_operations.validate_business_rules.assert_called_once_with(
            sample_assignment_data, exclude_id
        )


class TestSyncValidationOperations:
    """Pruebas para las operaciones de validación síncronas del facade."""

    def test_validate_required_fields_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_assignment_data: dict
    ):
        """Prueba la validación exitosa de campos requeridos."""
        # Configurar mock
        project_assignment_repository._validation_operations.validate_required_fields = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_required_fields(sample_assignment_data)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_required_fields.assert_called_once_with(
            sample_assignment_data
        )

    def test_validate_date_range_success(
        self, 
        project_assignment_repository: ProjectAssignmentRepositoryFacade,
        sample_date_range: tuple[date, date]
    ):
        """Prueba la validación exitosa de rango de fechas."""
        # Configurar mock
        start_date, end_date = sample_date_range
        project_assignment_repository._validation_operations.validate_date_range = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_date_range(start_date, end_date)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_date_range.assert_called_once_with(
            start_date, end_date
        )

    def test_validate_allocation_percentage_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de porcentaje de asignación."""
        # Configurar mock
        allocation_percentage = 80.0
        project_assignment_repository._validation_operations.validate_allocation_percentage = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_allocation_percentage(allocation_percentage)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_allocation_percentage.assert_called_once_with(
            allocation_percentage
        )

    def test_validate_hours_per_day_success(
        self, project_assignment_repository: ProjectAssignmentRepositoryFacade
    ):
        """Prueba la validación exitosa de horas por día."""
        # Configurar mock
        hours_per_day = 8.0
        project_assignment_repository._validation_operations.validate_hours_per_day = MagicMock()
        
        # Ejecutar
        project_assignment_repository.validate_hours_per_day(hours_per_day)
        
        # Verificar
        project_assignment_repository._validation_operations.validate_hours_per_day.assert_called_once_with(
            hours_per_day
        )