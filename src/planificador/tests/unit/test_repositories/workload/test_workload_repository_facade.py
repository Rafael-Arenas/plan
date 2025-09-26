# src/planificador/tests/unit/test_repositories/workload/test_workload_repository_facade.py

"""
Tests unitarios para WorkloadRepositoryFacade.

Este módulo contiene las pruebas unitarias para la fachada del repositorio
de cargas de trabajo, verificando la correcta delegación de operaciones
a los módulos especializados y el manejo adecuado de errores.

Principios de Testing:
    - Aislamiento: Cada test es independiente y no afecta a otros
    - Mocking: Se mockean todas las dependencias externas
    - Cobertura: Se cubren casos de éxito, error y edge cases
    - Claridad: Tests legibles con nombres descriptivos

Estructura de Tests:
    - TestWorkloadRepositoryFacadeCreateWorkload: Tests para creación
    - TestWorkloadRepositoryFacadeUpdateWorkload: Tests para actualización
    - TestWorkloadRepositoryFacadeDelegation: Tests de delegación
"""

import pytest
from unittest.mock import AsyncMock, MagicMock
from decimal import Decimal
from datetime import date

from planificador.repositories.workload.workload_repository_facade import WorkloadRepositoryFacade
from planificador.repositories.workload.modules import (
    WorkloadCrudModule,
    WorkloadQueryModule,
    WorkloadValidationModule,
    WorkloadRelationshipModule,
    WorkloadStatisticsModule
)
from planificador.schemas.workload.workload import WorkloadCreate
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    WorkloadQueryError,
    WorkloadValidationRepositoryError
)
from planificador.exceptions.validation import ValidationError

from .fixtures import (
    sample_workload_data,
    sample_workload_update_data,
    sample_workload_model,
    mock_crud_operations,
    mock_query_operations,
    mock_validation_operations,
    mock_statistics_operations,
    mock_relationship_operations
)


# Implementaciones concretas de los módulos para testing
class ConcreteWorkloadCrudModule(WorkloadCrudModule):
    """Implementación concreta del WorkloadCrudModule para testing."""
    
    def __init__(self, session):
        # No llamar super().__init__ para evitar inicialización completa
        self.session = session
        self._logger = MagicMock()
    
    async def create_workload(self, workload_data):
        return MagicMock()
    
    async def get_workload_by_id(self, workload_id):
        return MagicMock()
    
    async def update_workload(self, workload_id, update_data):
        return MagicMock()
    
    async def delete_workload(self, workload_id):
        return True
    
    async def create(self, workload_data):
        return MagicMock()
    
    async def update(self, workload_id, update_data):
        return MagicMock()
    
    async def delete(self, entity_id):
        return True
    
    async def add_workload(self, workload_data):
        return MagicMock()
    
    async def find_workload_by_id(self, workload_id):
        return MagicMock()
    
    async def modify_workload(self, workload_id, update_data):
        return MagicMock()
    
    async def remove_workload(self, workload_id):
        return True


class ConcreteWorkloadQueryModule(WorkloadQueryModule):
    """Implementación concreta del WorkloadQueryModule para testing."""
    
    def __init__(self, session):
        self.session = session
        self._logger = MagicMock()
    
    # Implementar todos los métodos abstractos con mocks
    async def get_by_employee(self, employee_id):
        return []
    
    async def get_by_employee_and_date(self, employee_id, workload_date):
        return None
    
    async def get_by_employee_date_range(self, employee_id, start_date, end_date):
        return []
    
    async def get_by_project_and_date(self, project_id, workload_date):
        return []
    
    async def get_by_date_range(self, start_date, end_date):
        return []
    
    async def get_by_project(self, project_id):
        return []
    
    async def get_by_project_date_range(self, project_id, start_date, end_date):
        return []
    
    async def get_overloaded_employees(self, target_date, threshold_hours=8.0):
        return []
    
    async def get_underutilized_employees(self, target_date, threshold_hours=4.0):
        return []
    
    async def get_with_relations(self, workload_id):
        return None
    
    async def get_team_workload(self, team_id, target_date):
        return []
    
    async def get_workloads_by_employee(self, employee_id, start_date=None, end_date=None):
        return []
    
    async def get_workloads_by_date_range(self, start_date, end_date):
        return []
    
    async def get_workloads_by_project(self, project_id, start_date=None, end_date=None):
        return []
    
    async def get_overloaded_employees_summary(self, target_date, threshold_hours=8.0):
        return []
    
    async def get_underutilized_employees_summary(self, target_date, threshold_hours=4.0):
        return []
    
    async def get_team_workloads(self, team_id, start_date, end_date):
        return []
    
    async def get_team_workload_summary(self, team_id, target_date):
        return {}
    
    async def get_weekly_workload(self, employee_id, week_start):
        return 0.0


class ConcreteWorkloadValidationModule(WorkloadValidationModule):
    """Implementación concreta del WorkloadValidationModule para testing."""
    
    def __init__(self, session):
        self.session = session
        self._logger = MagicMock()
    
    async def validate_workload_data(self, workload_data):
        return True
    
    async def validate_workload_hours(self, hours):
        return True
    
    async def validate_workload_date_range(self, start_date, end_date):
        return True
    
    async def validate_employee_workload_capacity(self, employee_id, workload_date, hours):
        return True
    
    async def validate_project_assignment(self, employee_id, project_id):
        return True
    
    async def validate_workload_overlap(self, employee_id, workload_date, exclude_workload_id=None):
        return True
    
    # Implementar método abstracto faltante
    async def get_by_unique_field(self, field_name, field_value):
        return None


class ConcreteWorkloadRelationshipModule(WorkloadRelationshipModule):
    """Implementación concreta del WorkloadRelationshipModule para testing."""
    
    def __init__(self, session):
        self.session = session
        self._logger = MagicMock()
    
    async def get_project_workloads(self, project_id, start_date=None, end_date=None):
        return []
    
    async def get_employee_projects(self, employee_id, start_date=None, end_date=None):
        return []
    
    async def get_workload_with_project_details(self, workload_id):
        return None
    
    async def get_workload_with_employee_details(self, workload_id):
        return None
    
    async def get_project_team_workloads(self, project_id, target_date):
        return []
    
    async def get_employee_workload_distribution(self, employee_id, start_date, end_date):
        return {}
    
    async def get_cross_project_workloads(self, employee_id, target_date):
        return []
    
    async def get_project_dependencies_workload(self, project_id):
        return []
    
    async def get_team_collaboration_matrix(self, team_id, start_date, end_date):
        return {}
    
    async def get_resource_allocation_conflicts(self, start_date, end_date):
        return []
    
    # Implementar métodos abstractos faltantes
    async def get_by_unique_field(self, field_name, field_value):
        return None
    
    async def check_workload_conflicts(self, employee_id, workload_date, exclude_workload_id=None):
        return []
    
    async def get_cross_project_employees(self, target_date):
        return []
    
    async def get_project_dependencies(self, project_id):
        return []
    
    async def get_project_employees(self, project_id, start_date=None, end_date=None):
        return []
    
    async def get_team_projects(self, team_id, start_date=None, end_date=None):
        return []
    
    async def validate_employee_project_assignment(self, employee_id, project_id):
        return True


class ConcreteWorkloadStatisticsModule(WorkloadStatisticsModule):
    """Implementación concreta del WorkloadStatisticsModule para testing."""
    
    def __init__(self, session):
        self.session = session
        self._logger = MagicMock()
    
    async def get_employee_workload_statistics(self, employee_id, start_date=None, end_date=None):
        return {}
    
    async def get_project_workload_statistics(self, project_id, start_date=None, end_date=None):
        return {}
    
    async def get_team_productivity_metrics(self, team_id, start_date, end_date):
        return {}
    
    async def get_workload_trends(self, start_date, end_date, granularity="daily"):
        return {}
    
    async def get_efficiency_analysis(self, employee_id=None, project_id=None, start_date=None, end_date=None):
        return {}
    
    async def get_capacity_utilization_report(self, start_date, end_date):
        return {}
    
    # Implementar métodos abstractos faltantes
    async def get_by_unique_field(self, field_name, field_value):
        return None
    
    async def get_capacity_utilization(self, start_date, end_date):
        return {}
    
    async def get_employee_average_hours(self, employee_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_employee_total_hours(self, employee_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_employee_workload_distribution(self, employee_id, start_date, end_date):
        return {}
    
    async def get_peak_workload_periods(self, start_date, end_date):
        return []
    
    async def get_project_employee_distribution(self, project_id, start_date, end_date):
        return {}
    
    async def get_project_total_hours(self, project_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_team_average_hours(self, team_id, start_date, end_date):
        return 0.0
    
    async def get_team_total_hours(self, team_id, start_date, end_date):
        return 0.0
    
    async def get_team_workload_distribution(self, team_id, start_date, end_date):
        return {}


class ConcreteWorkloadRepositoryFacade(WorkloadRepositoryFacade):
    """
    Implementación concreta del WorkloadRepositoryFacade para testing.
    
    Esta clase usa módulos concretos mockeados para permitir el testing
    de los métodos CRUD básicos sin errores de métodos abstractos.
    """
    
    def __init__(self, session):
        # Inicializar con módulos concretos mockeados
        self.session = session
        self.crud_module = ConcreteWorkloadCrudModule(session)
        self.query_module = ConcreteWorkloadQueryModule(session)
        self.validation_module = ConcreteWorkloadValidationModule(session)
        self.relationship_module = ConcreteWorkloadRelationshipModule(session)
        self.statistics_module = ConcreteWorkloadStatisticsModule(session)
    
    # Implementar todos los métodos abstractos de las interfaces
    
    # Métodos CRUD básicos
    async def create(self, workload_data):
        return await self.crud_module.create(workload_data)
    
    async def update(self, workload_id, update_data):
        return await self.crud_module.update(workload_id, update_data)
    
    async def delete(self, entity_id):
        return await self.crud_module.delete(entity_id)
    
    # Métodos de consulta
    async def get_by_employee(self, employee_id):
        return await self.query_module.get_by_employee(employee_id)
    
    async def get_by_employee_and_date(self, employee_id, workload_date):
        return await self.query_module.get_by_employee_and_date(employee_id, workload_date)
    
    async def get_by_employee_date_range(self, employee_id, start_date, end_date):
        return await self.query_module.get_by_employee_date_range(employee_id, start_date, end_date)
    
    async def get_by_project_and_date(self, project_id, workload_date):
        return await self.query_module.get_by_project_and_date(project_id, workload_date)
    
    async def get_by_date_range(self, start_date, end_date):
        return await self.query_module.get_by_date_range(start_date, end_date)
    
    async def get_by_project(self, project_id):
        return await self.query_module.get_by_project(project_id)
    
    async def get_by_project_date_range(self, project_id, start_date, end_date):
        return await self.query_module.get_by_project_date_range(project_id, start_date, end_date)
    
    async def get_overloaded_employees(self, target_date, threshold_hours=8.0):
        return await self.query_module.get_overloaded_employees(target_date, threshold_hours)
    
    async def get_underutilized_employees(self, target_date, threshold_hours=4.0):
        return await self.query_module.get_underutilized_employees(target_date, threshold_hours)
    
    async def get_with_relations(self, workload_id):
        return await self.query_module.get_with_relations(workload_id)
    
    async def get_team_workload(self, team_id, target_date):
        return await self.query_module.get_team_workload(team_id, target_date)
    
    async def get_overloaded_employees_summary(self, target_date, threshold_hours=8.0):
        return await self.query_module.get_overloaded_employees_summary(target_date, threshold_hours)
    
    async def get_underutilized_employees_summary(self, target_date, threshold_hours=4.0):
        return await self.query_module.get_underutilized_employees_summary(target_date, threshold_hours)
    
    async def get_team_workloads(self, team_id, start_date, end_date):
        return await self.query_module.get_team_workloads(team_id, start_date, end_date)
    
    async def get_team_workload_summary(self, team_id, target_date):
        return await self.query_module.get_team_workload_summary(team_id, target_date)
    
    async def get_weekly_workload(self, employee_id, week_start):
        return await self.query_module.get_weekly_workload(employee_id, week_start)
    
    # Métodos de validación
    async def validate_create_data(self, workload_data):
        return await self.validation_module.validate_workload_data(workload_data)
    
    async def validate_update_data(self, update_data):
        return await self.validation_module.validate_workload_data(update_data)
    
    async def validate_workload_id(self, workload_id):
        return True
    
    async def validate_date_range(self, start_date, end_date):
        return await self.validation_module.validate_workload_date_range(start_date, end_date)
    
    async def validate_employee_project_assignment(self, employee_id, project_id):
        return await self.validation_module.validate_project_assignment(employee_id, project_id)
    
    async def validate_team_id(self, team_id):
        return True
    
    async def validate_threshold_hours(self, threshold_hours):
        return True
    
    async def check_workload_conflicts(self, employee_id, workload_date, exclude_workload_id=None):
        return await self.validation_module.validate_workload_overlap(employee_id, workload_date, exclude_workload_id)
    
    async def check_employee_project_consistency(self, employee_id, project_id):
        return await self.validation_module.validate_project_assignment(employee_id, project_id)
    
    # Métodos de relaciones
    async def get_project_workloads(self, project_id, start_date=None, end_date=None):
        return await self.relationship_module.get_project_workloads(project_id, start_date, end_date)
    
    async def get_employee_projects(self, employee_id, start_date=None, end_date=None):
        return await self.relationship_module.get_employee_projects(employee_id, start_date, end_date)
    
    async def get_employee_workloads(self, employee_id, start_date=None, end_date=None):
        return await self.query_module.get_workloads_by_employee(employee_id, start_date, end_date)
    
    async def get_cross_project_employees(self, target_date):
        return []
    
    async def get_project_dependencies(self, project_id):
        return await self.relationship_module.get_project_dependencies_workload(project_id)
    
    async def get_project_employees(self, project_id, start_date=None, end_date=None):
        return []
    
    async def get_team_projects(self, team_id, start_date=None, end_date=None):
        return []
    
    async def get_employee_workload_distribution(self, employee_id, start_date, end_date):
        return await self.relationship_module.get_employee_workload_distribution(employee_id, start_date, end_date)
    
    async def get_project_employee_distribution(self, project_id, start_date, end_date):
        return {}
    
    async def get_team_workload_distribution(self, team_id, start_date, end_date):
        return {}
    
    # Métodos de estadísticas
    async def get_employee_total_hours(self, employee_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_project_total_hours(self, project_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_team_total_hours(self, team_id, start_date, end_date):
        return 0.0
    
    async def get_employee_average_hours(self, employee_id, start_date=None, end_date=None):
        return 0.0
    
    async def get_team_average_hours(self, team_id, start_date, end_date):
        return 0.0
    
    async def get_workload_trends(self, start_date, end_date, granularity="daily"):
        return await self.statistics_module.get_workload_trends(start_date, end_date, granularity)
    
    async def get_capacity_utilization(self, start_date, end_date):
        return await self.statistics_module.get_capacity_utilization_report(start_date, end_date)
    
    async def get_peak_workload_periods(self, start_date, end_date):
        return []



@pytest.fixture
def workload_facade():
    """
    Fixture que proporciona una instancia de ConcreteWorkloadRepositoryFacade con mocks.
    
    Configura todos los módulos de operaciones como mocks para permitir
    el testing aislado de la lógica de la fachada.
    """
    # Crear una sesión mock
    mock_session = AsyncMock()
    
    facade = ConcreteWorkloadRepositoryFacade(mock_session)
    
    # Convertir los módulos en mocks para control total en tests
    facade.crud_module = AsyncMock()
    facade.query_module = AsyncMock()
    facade.validation_module = AsyncMock()
    facade.relationship_module = AsyncMock()
    facade.statistics_module = AsyncMock()
    
    return facade


class TestWorkloadRepositoryFacadeCreateWorkload:
    """Tests para el método create_workload."""

    @pytest.mark.asyncio
    async def test_create_workload_success(
        self,
        workload_facade,
        sample_workload_data,
        sample_workload_model
    ):
        """Test exitoso de creación de carga de trabajo."""
        # Configurar el mock
        workload_facade.crud_module.create_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.create_workload(sample_workload_data)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)

    @pytest.mark.asyncio
    async def test_create_workload_repository_error(
        self,
        workload_facade,
        sample_workload_data
    ):
        """Test de error del repositorio al crear carga de trabajo."""
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.create_workload.side_effect = WorkloadRepositoryError(
            message="Error al crear carga de trabajo",
            operation="create_workload"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.create_workload(sample_workload_data)
        
        assert "Error al crear carga de trabajo" in str(exc_info.value)
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)

    @pytest.mark.asyncio
    async def test_create_workload_validation_error(
        self,
        workload_facade,
        sample_workload_data
    ):
        """Test de error de validación al crear carga de trabajo."""
        # Configurar el mock para lanzar excepción de validación
        workload_facade.crud_module.create_workload.side_effect = WorkloadValidationRepositoryError(
            validation_type="data_validation",
            invalid_data={"planned_hours": -1},
            reason="Datos de carga de trabajo inválidos"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadValidationRepositoryError) as exc_info:
            await workload_facade.create_workload(sample_workload_data)
        
        assert "Datos de carga de trabajo inválidos" in str(exc_info.value)
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)

    @pytest.mark.asyncio
    async def test_create_workload_unexpected_error(
        self,
        workload_facade,
        sample_workload_data
    ):
        """Test de error inesperado al crear carga de trabajo."""
        # Configurar el mock para lanzar excepción inesperada
        workload_facade.crud_module.create_workload.side_effect = Exception("Error inesperado")
        
        # Ejecutar y verificar excepción
        with pytest.raises(Exception) as exc_info:
            await workload_facade.create_workload(sample_workload_data)
        
        assert "Error inesperado" in str(exc_info.value)
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)


class TestWorkloadRepositoryFacadeUpdateWorkload:
    """Tests para el método update_workload."""

    @pytest.mark.asyncio
    async def test_update_workload_success(
        self,
        workload_facade,
        sample_workload_update_data,
        sample_workload_model
    ):
        """Test exitoso de actualización de carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock
        workload_facade.crud_module.update_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.update_workload(workload_id, sample_workload_update_data)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )

    @pytest.mark.asyncio
    async def test_update_workload_repository_error(
        self,
        workload_facade,
        sample_workload_update_data
    ):
        """Test de error del repositorio al actualizar carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.update_workload.side_effect = WorkloadRepositoryError(
            message="Error al actualizar carga de trabajo",
            operation="update_workload",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.update_workload(workload_id, sample_workload_update_data)
        
        assert "Error al actualizar carga de trabajo" in str(exc_info.value)
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )

    @pytest.mark.asyncio
    async def test_update_workload_validation_error(
        self,
        workload_facade,
        sample_workload_update_data
    ):
        """Test de error de validación al actualizar carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción de validación
        workload_facade.crud_module.update_workload.side_effect = WorkloadValidationRepositoryError(
            validation_type="data_validation",
            invalid_data={"actual_hours": -1},
            reason="Datos de actualización inválidos",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadValidationRepositoryError) as exc_info:
            await workload_facade.update_workload(workload_id, sample_workload_update_data)
        
        assert "Datos de actualización inválidos" in str(exc_info.value)
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )

    @pytest.mark.asyncio
    async def test_update_workload_unexpected_error(
        self,
        workload_facade,
        sample_workload_update_data
    ):
        """Test de error inesperado al actualizar carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción genérica
        workload_facade.crud_module.update_workload.side_effect = Exception("Error inesperado")
        
        # Ejecutar y verificar excepción
        with pytest.raises(Exception) as exc_info:
            await workload_facade.update_workload(workload_id, sample_workload_update_data)
        
        assert "Error inesperado" in str(exc_info.value)
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )


class TestWorkloadRepositoryFacadeDelegation:
    """Tests para verificar la correcta delegación a los módulos."""

    @pytest.mark.asyncio
    async def test_create_workload_delegates_to_crud_module(
        self,
        workload_facade,
        sample_workload_data,
        sample_workload_model
    ):
        """Test que verifica la delegación correcta al módulo CRUD para create."""
        # Configurar el mock
        workload_facade.crud_module.create_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.create_workload(sample_workload_data)
        
        # Verificar delegación
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)
        assert result == sample_workload_model

    @pytest.mark.asyncio
    async def test_update_workload_delegates_to_crud_module(
        self,
        workload_facade,
        sample_workload_update_data,
        sample_workload_model
    ):
        """Test que verifica la delegación correcta al módulo CRUD para update."""
        workload_id = 1
        
        # Configurar el mock
        workload_facade.crud_module.update_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.update_workload(workload_id, sample_workload_update_data)
        
        # Verificar delegación
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )
        assert result == sample_workload_model


class TestWorkloadRepositoryFacadeDeleteWorkload:
    """Tests para el método delete_workload."""

    @pytest.mark.asyncio
    async def test_delete_workload_success(self, workload_facade):
        """Test exitoso de eliminación de carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock
        workload_facade.crud_module.delete_workload.return_value = True
        
        # Ejecutar
        result = await workload_facade.delete_workload(workload_id)
        
        # Verificar
        assert result is True
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_delete_workload_not_found(self, workload_facade):
        """Test de carga de trabajo no encontrada al eliminar."""
        workload_id = 999
        
        # Configurar el mock para lanzar excepción de no encontrado
        workload_facade.crud_module.delete_workload.side_effect = WorkloadRepositoryError(
            message="Carga de trabajo no encontrada",
            operation="delete_workload",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.delete_workload(workload_id)
        
        assert "Carga de trabajo no encontrada" in str(exc_info.value)
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_delete_workload_repository_error(self, workload_facade):
        """Test de error del repositorio al eliminar carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.delete_workload.side_effect = WorkloadRepositoryError(
            message="Error al eliminar carga de trabajo",
            operation="delete_workload",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.delete_workload(workload_id)
        
        assert "Error al eliminar carga de trabajo" in str(exc_info.value)
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_delete_workload_unexpected_error(self, workload_facade):
        """Test de error inesperado al eliminar carga de trabajo."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción inesperada
        workload_facade.crud_module.delete_workload.side_effect = Exception("Error inesperado")
        
        # Ejecutar y verificar excepción
        with pytest.raises(Exception) as exc_info:
            await workload_facade.delete_workload(workload_id)
        
        assert "Error inesperado" in str(exc_info.value)
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)


class TestWorkloadRepositoryFacadeGetWorkloadById:
    """Tests para el método get_workload_by_id."""

    @pytest.mark.asyncio
    async def test_get_workload_by_id_success(self, workload_facade, sample_workload_model):
        """Test exitoso de obtención de carga de trabajo por ID."""
        workload_id = 1
        
        # Configurar el mock
        workload_facade.crud_module.get_workload_by_id.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.get_workload_by_id(workload_id)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.get_workload_by_id.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_get_workload_by_id_not_found(self, workload_facade):
        """Test de carga de trabajo no encontrada por ID."""
        workload_id = 999
        
        # Configurar el mock para retornar None
        workload_facade.crud_module.get_workload_by_id.return_value = None
        
        # Ejecutar
        result = await workload_facade.get_workload_by_id(workload_id)
        
        # Verificar
        assert result is None
        workload_facade.crud_module.get_workload_by_id.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_get_workload_by_id_repository_error(self, workload_facade):
        """Test de error del repositorio al obtener carga de trabajo por ID."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.get_workload_by_id.side_effect = WorkloadRepositoryError(
            message="Error al obtener carga de trabajo",
            operation="get_workload_by_id",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.get_workload_by_id(workload_id)
        
        assert "Error al obtener carga de trabajo" in str(exc_info.value)
        workload_facade.crud_module.get_workload_by_id.assert_awaited_once_with(workload_id)


class TestWorkloadRepositoryFacadeGetByUniqueField:
    """Tests para el método get_by_unique_field."""

    @pytest.mark.asyncio
    async def test_get_by_unique_field_success(self, workload_facade, sample_workload_model):
        """Test exitoso de obtención por campo único."""
        field_name = "employee_id"
        field_value = 1
        
        # Configurar el mock
        workload_facade.crud_module.get_by_unique_field.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.get_by_unique_field(field_name, field_value)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.get_by_unique_field.assert_awaited_once_with(
            field_name, field_value
        )

    @pytest.mark.asyncio
    async def test_get_by_unique_field_not_found(self, workload_facade):
        """Test de registro no encontrado por campo único."""
        field_name = "employee_id"
        field_value = 999
        
        # Configurar el mock para retornar None
        workload_facade.crud_module.get_by_unique_field.return_value = None
        
        # Ejecutar
        result = await workload_facade.get_by_unique_field(field_name, field_value)
        
        # Verificar
        assert result is None
        workload_facade.crud_module.get_by_unique_field.assert_awaited_once_with(
            field_name, field_value
        )

    @pytest.mark.asyncio
    async def test_get_by_unique_field_repository_error(self, workload_facade):
        """Test de error del repositorio al obtener por campo único."""
        field_name = "employee_id"
        field_value = 1
        
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.get_by_unique_field.side_effect = WorkloadRepositoryError(
            message="Error al obtener por campo único",
            operation="get_by_unique_field"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.get_by_unique_field(field_name, field_value)
        
        assert "Error al obtener por campo único" in str(exc_info.value)
        workload_facade.crud_module.get_by_unique_field.assert_awaited_once_with(
            field_name, field_value
        )


class TestWorkloadRepositoryFacadeAliasMethodsCrud:
    """Tests para los métodos alias CRUD: add_workload, find_workload_by_id, modify_workload, remove_workload."""

    @pytest.mark.asyncio
    async def test_add_workload_success(self, workload_facade, sample_workload_data, sample_workload_model):
        """Test exitoso de add_workload (alias de create_workload)."""
        # Configurar el mock del método create_workload
        workload_facade.crud_module.create_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.add_workload(sample_workload_data)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)

    @pytest.mark.asyncio
    async def test_add_workload_repository_error(self, workload_facade, sample_workload_data):
        """Test de error del repositorio en add_workload."""
        # Configurar el mock para lanzar excepción
        workload_facade.crud_module.create_workload.side_effect = WorkloadRepositoryError(
            message="Error al agregar carga de trabajo",
            operation="create_workload"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.add_workload(sample_workload_data)
        
        assert "Error al agregar carga de trabajo" in str(exc_info.value)
        workload_facade.crud_module.create_workload.assert_awaited_once_with(sample_workload_data)

    @pytest.mark.asyncio
    async def test_find_workload_by_id_success(self, workload_facade, sample_workload_model):
        """Test exitoso de find_workload_by_id (alias de get_workload_by_id)."""
        workload_id = 1
        
        # Configurar el mock del método get_workload_by_id
        workload_facade.crud_module.get_workload_by_id.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.find_workload_by_id(workload_id)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.get_workload_by_id.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_find_workload_by_id_not_found(self, workload_facade):
        """Test de find_workload_by_id cuando no se encuentra el registro."""
        workload_id = 999
        
        # Configurar el mock para retornar None
        workload_facade.crud_module.get_workload_by_id.return_value = None
        
        # Ejecutar
        result = await workload_facade.find_workload_by_id(workload_id)
        
        # Verificar
        assert result is None
        workload_facade.crud_module.get_workload_by_id.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_modify_workload_success(
        self, 
        workload_facade, 
        sample_workload_update_data, 
        sample_workload_model
    ):
        """Test exitoso de modify_workload (alias de update_workload)."""
        workload_id = 1
        
        # Configurar el mock del método update_workload
        workload_facade.crud_module.update_workload.return_value = sample_workload_model
        
        # Ejecutar
        result = await workload_facade.modify_workload(workload_id, sample_workload_update_data)
        
        # Verificar
        assert result == sample_workload_model
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )

    @pytest.mark.asyncio
    async def test_modify_workload_validation_error(self, workload_facade, sample_workload_update_data):
        """Test de error de validación en modify_workload."""
        workload_id = 1
        
        # Configurar el mock para lanzar excepción de validación
        workload_facade.crud_module.update_workload.side_effect = WorkloadValidationRepositoryError(
            validation_type="data_validation",
            invalid_data={"actual_hours": -1},
            reason="Datos de modificación inválidos",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadValidationRepositoryError) as exc_info:
            await workload_facade.modify_workload(workload_id, sample_workload_update_data)
        
        assert "Datos de modificación inválidos" in str(exc_info.value)
        workload_facade.crud_module.update_workload.assert_awaited_once_with(
            workload_id, sample_workload_update_data
        )

    @pytest.mark.asyncio
    async def test_remove_workload_success(self, workload_facade):
        """Test exitoso de remove_workload (alias de delete_workload)."""
        workload_id = 1
        
        # Configurar el mock del método delete_workload
        workload_facade.crud_module.delete_workload.return_value = True
        
        # Ejecutar
        result = await workload_facade.remove_workload(workload_id)
        
        # Verificar
        assert result is True
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)

    @pytest.mark.asyncio
    async def test_remove_workload_not_found(self, workload_facade):
        """Test de remove_workload cuando no se encuentra el registro."""
        workload_id = 999
        
        # Configurar el mock para lanzar excepción de no encontrado
        workload_facade.crud_module.delete_workload.side_effect = WorkloadRepositoryError(
            message="Carga de trabajo no encontrada para eliminar",
            operation="delete_workload",
            workload_id=workload_id
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(WorkloadRepositoryError) as exc_info:
            await workload_facade.remove_workload(workload_id)
        
        assert "Carga de trabajo no encontrada para eliminar" in str(exc_info.value)
        workload_facade.crud_module.delete_workload.assert_awaited_once_with(workload_id)