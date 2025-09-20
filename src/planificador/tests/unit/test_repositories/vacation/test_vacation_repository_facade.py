# src/planificador/tests/unit/test_repositories/vacation/test_vacation_repository_facade.py
"""
Tests unitarios para VacationRepositoryFacade.

Este módulo contiene tests completos para todas las operaciones del facade de vacaciones,
incluyendo CRUD, consultas, validaciones, relaciones y estadísticas.
"""

import pytest
from datetime import date, datetime
from typing import Generator, Dict, Any, List
from unittest.mock import MagicMock, AsyncMock, patch

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.vacation import Vacation, VacationType, VacationStatus
from planificador.repositories.vacation.vacation_repository_facade import VacationRepositoryFacade
from planificador.repositories.vacation.modules.crud_module import VacationCrudModule
from planificador.repositories.vacation.modules.query_module import VacationQueryModule
from planificador.repositories.vacation.modules.validation_module import VacationValidationModule
from planificador.repositories.vacation.modules.statistics_module import VacationStatisticsModule
from planificador.repositories.vacation.modules.relationship_module import VacationRelationshipModule

from .fixtures import (
    mock_vacation_session,
    base_vacation_data,
    vacation_create_data,
    vacation_update_data,
    sample_vacation_instance,
    multiple_vacations_data,
    vacation_instances_list,
    vacation_search_filters,
    vacation_statistics_data,
    employee_vacation_summary,
    mock_crud_operations,
    mock_query_operations,
    mock_validation_operations,
    mock_statistics_operations,
    mock_relationship_operations
)


@pytest.fixture
def vacation_facade(
    mock_vacation_session: AsyncMock,
    mock_crud_operations: AsyncMock,
    mock_query_operations: AsyncMock,
    mock_validation_operations: AsyncMock,
    mock_statistics_operations: AsyncMock,
    mock_relationship_operations: AsyncMock,
) -> Generator[VacationRepositoryFacade, None, None]:
    """
    Fixture que crea una instancia de VacationRepositoryFacade con módulos mock.
    
    Utiliza patch para reemplazar las clases de operaciones reales por mocks
    durante la instanciación del facade, evitando errores con clases abstractas.
    """
    with patch(
        "planificador.repositories.vacation.vacation_repository_facade.VacationCrudModule",
        return_value=mock_crud_operations,
    ), patch(
        "planificador.repositories.vacation.vacation_repository_facade.VacationQueryModule",
        return_value=mock_query_operations,
    ), patch(
        "planificador.repositories.vacation.vacation_repository_facade.VacationValidationModule",
        return_value=mock_validation_operations,
    ), patch(
        "planificador.repositories.vacation.vacation_repository_facade.VacationStatisticsModule",
        return_value=mock_statistics_operations,
    ), patch(
        "planificador.repositories.vacation.vacation_repository_facade.VacationRelationshipModule",
        return_value=mock_relationship_operations,
    ):
        facade = VacationRepositoryFacade(session=mock_vacation_session)
        yield facade


class TestVacationRepositoryFacadeCRUD:
    """Tests para operaciones CRUD del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_create_data: Dict[str, Any],
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la creación exitosa de una vacación."""
        # Configurar el mock para devolver la instancia esperada
        vacation_facade._crud_operations.create_vacation.return_value = sample_vacation_instance
        
        # Ejecutar el método
        result = await vacation_facade.create_vacation(vacation_create_data)
        
        # Verificar que se llamó al método correcto con los datos apropiados
        vacation_facade._crud_operations.create_vacation.assert_awaited_once_with(vacation_create_data)
        
        # Verificar el resultado
        assert result == sample_vacation_instance
        assert result.vacation_type == VacationType.ANNUAL
        assert result.status == VacationStatus.PENDING

    @pytest.mark.asyncio
    async def test_update_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_update_data: Dict[str, Any],
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la actualización exitosa de una vacación."""
        vacation_id = 1
        
        # Configurar el mock
        updated_vacation = sample_vacation_instance
        updated_vacation.status = VacationStatus.APPROVED
        vacation_facade._crud_operations.update_vacation.return_value = updated_vacation
        
        # Ejecutar el método
        result = await vacation_facade.update_vacation(vacation_id, vacation_update_data)
        
        # Verificar la llamada
        vacation_facade._crud_operations.update_vacation.assert_awaited_once_with(
            vacation_id, vacation_update_data
        )
        
        # Verificar el resultado
        assert result == updated_vacation
        assert result.status == VacationStatus.APPROVED

    @pytest.mark.asyncio
    async def test_delete_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade
    ):
        """Test que verifica la eliminación exitosa de una vacación."""
        vacation_id = 1
        
        # Configurar el mock
        vacation_facade._crud_operations.delete_vacation.return_value = True
        
        # Ejecutar el método
        result = await vacation_facade.delete_vacation(vacation_id)
        
        # Verificar la llamada
        vacation_facade._crud_operations.delete_vacation.assert_awaited_once_with(vacation_id)
        
        # Verificar el resultado
        assert result is True

    @pytest.mark.asyncio
    async def test_get_vacation_by_id_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la obtención de una vacación por ID."""
        vacation_id = 1
        
        # Configurar el mock
        vacation_facade._crud_operations.get_vacation_by_id.return_value = sample_vacation_instance
        
        # Ejecutar el método
        result = await vacation_facade.get_vacation_by_id(vacation_id)
        
        # Verificar la llamada
        vacation_facade._crud_operations.get_vacation_by_id.assert_awaited_once_with(vacation_id)
        
        # Verificar el resultado
        assert result == sample_vacation_instance
        assert result.id == vacation_id


class TestVacationRepositoryFacadeQuery:
    """Tests para operaciones de consulta del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_by_employee_id_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones por ID de empleado."""
        employee_id = 1
        
        # Configurar el mock
        vacation_facade._query_operations.get_by_employee_id.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_by_employee_id(employee_id)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_by_employee_id.assert_awaited_once_with(employee_id)
        
        # Verificar el resultado
        assert result == vacation_instances_list
        assert len(result) > 0

    @pytest.mark.asyncio
    async def test_get_by_status_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones por estado."""
        status = VacationStatus.APPROVED
        
        # Configurar el mock
        vacation_facade._query_operations.get_by_status.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_by_status(status)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_by_status.assert_awaited_once_with(status)
        
        # Verificar el resultado
        assert result == vacation_instances_list

    @pytest.mark.asyncio
    async def test_get_by_type_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones por tipo."""
        vacation_type = VacationType.ANNUAL
        
        # Configurar el mock
        vacation_facade._query_operations.get_by_type.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_by_type(vacation_type)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_by_type.assert_awaited_once_with(vacation_type)
        
        # Verificar el resultado
        assert result == vacation_instances_list

    @pytest.mark.asyncio
    async def test_get_by_date_range_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones por rango de fechas."""
        start_date = date(2024, 7, 1)
        end_date = date(2024, 7, 31)
        
        # Configurar el mock
        vacation_facade._query_operations.get_by_date_range.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_by_date_range(start_date, end_date)
        
        # Verificar la llamada con parámetros nombrados
        vacation_facade._query_operations.get_by_date_range.assert_awaited_once_with(
            start_date=start_date, end_date=end_date
        )
        
        # Verificar el resultado
        assert result == vacation_instances_list

    @pytest.mark.asyncio
    async def test_search_vacations_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation],
        vacation_search_filters: Dict[str, Any]
    ):
        """Test que verifica la búsqueda de vacaciones con filtros."""
        # Configurar el mock
        vacation_facade._query_operations.search_vacations.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.search_vacations(**vacation_search_filters)
        
        # Verificar la llamada
        vacation_facade._query_operations.search_vacations.assert_awaited_once_with(
            **vacation_search_filters
        )
        
        # Verificar el resultado
        assert result == vacation_instances_list

    @pytest.mark.asyncio
    async def test_get_pending_approvals_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones pendientes de aprobación."""
        limit = 50
        
        # Configurar el mock
        vacation_facade._query_operations.get_pending_approvals.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_pending_approvals(limit)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_pending_approvals.assert_awaited_once_with(limit)
        
        # Verificar el resultado
        assert result == vacation_instances_list

    @pytest.mark.asyncio
    async def test_get_overlapping_vacations_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones que se solapan."""
        employee_id = 1
        start_date = date(2024, 7, 10)
        end_date = date(2024, 7, 20)
        
        # Configurar el mock en el módulo correcto
        vacation_facade._relationship_operations.get_overlapping_vacations.return_value = vacation_instances_list
        
        # Ejecutar el método con el orden correcto de parámetros
        result = await vacation_facade.get_overlapping_vacations(
            employee_id, start_date, end_date
        )
        
        # Verificar la llamada con el orden correcto de parámetros
        vacation_facade._relationship_operations.get_overlapping_vacations.assert_awaited_once_with(
            employee_id, start_date, end_date, None
        )
        
        # Verificar el resultado
        assert result == vacation_instances_list


class TestVacationRepositoryFacadeValidation:
    """Tests para operaciones de validación del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_validate_create_data_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_create_data: Dict[str, Any]
    ):
        """Test que verifica la validación exitosa de datos para crear vacación."""
        # Configurar el mock para retornar validación exitosa
        vacation_facade._validation_operations.validate_vacation_data.return_value = {
            'is_valid': True,
            'errors': []
        }
        
        # Ejecutar el método (no debería lanzar excepción)
        await vacation_facade.validate_create_data(vacation_create_data)
        
        # Verificar la llamada
        vacation_facade._validation_operations.validate_vacation_data.assert_awaited_once_with(
            vacation_create_data
        )

    @pytest.mark.asyncio
    async def test_validate_update_data_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_update_data: Dict[str, Any]
    ):
        """Test que verifica la validación exitosa de datos para actualizar vacación."""
        vacation_id = 1
        
        # Configurar el mock
        vacation_facade._validation_operations.validate_update_data.return_value = None
        
        # Ejecutar el método
        await vacation_facade.validate_update_data(vacation_id, vacation_update_data)
        
        # Verificar la llamada (solo con data, no con vacation_id)
        vacation_facade._validation_operations.validate_update_data.assert_awaited_once_with(
            vacation_update_data
        )

    @pytest.mark.asyncio
    async def test_validate_vacation_request_success(
        self, 
        vacation_facade: VacationRepositoryFacade
    ):
        """Test que verifica la validación exitosa de una solicitud de vacación."""
        employee_id = 1
        vacation_type = VacationType.ANNUAL
        start_date = date(2024, 7, 1)
        end_date = date(2024, 7, 15)
        
        # Configurar el mock
        validation_result = {"valid": True, "conflicts": []}
        vacation_facade._validation_operations.validate_vacation_request.return_value = validation_result
        
        # Ejecutar el método
        result = await vacation_facade.validate_vacation_request(
            employee_id, vacation_type, start_date, end_date
        )
        
        # Verificar la llamada
        vacation_facade._validation_operations.validate_vacation_request.assert_awaited_once_with(
            employee_id, start_date, end_date, vacation_type
        )
        
        # Verificar el resultado
        assert result == validation_result
        assert result["valid"] is True

    @pytest.mark.asyncio
    async def test_validate_vacation_id_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la validación exitosa de un ID de vacación."""
        vacation_id = 1
        
        # Configurar el mock
        vacation_facade._validation_operations.validate_vacation_id.return_value = sample_vacation_instance
        
        # Ejecutar el método
        result = await vacation_facade.validate_vacation_id(vacation_id)
        
        # Verificar la llamada
        vacation_facade._validation_operations.validate_vacation_id.assert_awaited_once_with(
            vacation_id
        )
        
        # Verificar el resultado
        assert result == sample_vacation_instance


class TestVacationRepositoryFacadeStatistics:
    """Tests para operaciones de estadísticas del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_employee_vacation_summary_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        employee_vacation_summary: Dict[str, Any]
    ):
        """Test que verifica la obtención del resumen de vacaciones por empleado."""
        employee_id = 1
        year = 2024
        
        # Configurar el mock en el módulo correcto
        vacation_facade._relationship_operations.get_employee_vacation_summary.return_value = employee_vacation_summary
        
        # Ejecutar el método
        result = await vacation_facade.get_employee_vacation_summary(employee_id, year)
        
        # Verificar la llamada
        vacation_facade._relationship_operations.get_employee_vacation_summary.assert_awaited_once_with(
            employee_id, year
        )
        
        # Verificar el resultado
        assert result == employee_vacation_summary
        assert result["employee_id"] == employee_id
        assert "total_vacations" in result

    @pytest.mark.asyncio
    async def test_get_vacation_trends_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_statistics_data: Dict[str, Any]
    ):
        """Test que verifica la obtención de tendencias de vacaciones."""
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Configurar el mock
        vacation_facade._statistics_operations.get_vacation_trends.return_value = vacation_statistics_data
        
        # Ejecutar el método
        result = await vacation_facade.get_vacation_trends(start_date, end_date)
        
        # Verificar la llamada con todos los parámetros (incluyendo default)
        vacation_facade._statistics_operations.get_vacation_trends.assert_awaited_once_with(
            start_date, end_date, "monthly"
        )
        
        # Verificar el resultado
        assert result == vacation_statistics_data
        assert "total_vacations" in result

    @pytest.mark.asyncio
    async def test_get_team_vacation_statistics_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_statistics_data: Dict[str, Any]
    ):
        """Test que verifica la obtención de estadísticas de vacaciones por equipo."""
        team_id = 1
        year = 2024
        
        # Configurar el mock
        vacation_facade._statistics_operations.get_team_vacation_statistics.return_value = vacation_statistics_data
        
        # Ejecutar el método
        result = await vacation_facade.get_team_vacation_statistics(team_id, year)
        
        # Verificar la llamada
        vacation_facade._statistics_operations.get_team_vacation_statistics.assert_awaited_once_with(
            team_id, year
        )
        
        # Verificar el resultado
        assert result == vacation_statistics_data


class TestVacationRepositoryFacadeRelationship:
    """Tests para operaciones de relaciones del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_with_relations_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la obtención de vacación con relaciones."""
        vacation_id = 1
        
        # Configurar el mock en el módulo correcto
        vacation_facade._query_operations.get_with_relations.return_value = sample_vacation_instance
        
        # Ejecutar el método
        result = await vacation_facade.get_with_relations(vacation_id)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_with_relations.assert_awaited_once_with(
            vacation_id
        )
        
        # Verificar el resultado
        assert result == sample_vacation_instance

    @pytest.mark.asyncio
    async def test_get_vacation_with_employee_details_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        vacation_instances_list: List[Vacation]
    ):
        """Test que verifica la obtención de vacaciones con detalles del empleado."""
        employee_id = 1
        
        # Configurar el mock
        vacation_facade._relationship_operations.get_vacation_with_employee_details.return_value = vacation_instances_list
        
        # Ejecutar el método
        result = await vacation_facade.get_vacation_with_employee_details(employee_id)
        
        # Verificar la llamada
        vacation_facade._relationship_operations.get_vacation_with_employee_details.assert_awaited_once_with(
            employee_id
        )
        
        # Verificar el resultado
        assert result == vacation_instances_list


class TestVacationRepositoryFacadeSpecialOperations:
    """Tests para operaciones especiales del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_approve_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la aprobación exitosa de una vacación."""
        vacation_id = 1
        approved_by = "Manager Test"
        notes = "Vacación aprobada"
        
        # Configurar los mocks
        vacation_facade._crud_operations.get_vacation_by_id.return_value = sample_vacation_instance
        
        approved_vacation = sample_vacation_instance
        approved_vacation.status = VacationStatus.APPROVED
        vacation_facade._crud_operations.update_vacation.return_value = approved_vacation
        
        # Ejecutar el método
        result = await vacation_facade.approve_vacation(vacation_id, approved_by, notes)
        
        # Verificar las llamadas
        vacation_facade._crud_operations.get_vacation_by_id.assert_awaited_once_with(vacation_id)
        vacation_facade._crud_operations.update_vacation.assert_awaited_once()
        
        # Verificar el resultado
        assert result == approved_vacation

    @pytest.mark.asyncio
    async def test_reject_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica el rechazo exitoso de una vacación."""
        vacation_id = 1
        rejected_by = "Manager Test"
        reason = "Conflicto de fechas"
        
        # Configurar los mocks
        vacation_facade._crud_operations.get_vacation_by_id.return_value = sample_vacation_instance
        
        rejected_vacation = sample_vacation_instance
        rejected_vacation.status = VacationStatus.REJECTED
        vacation_facade._crud_operations.update_vacation.return_value = rejected_vacation
        
        # Ejecutar el método
        result = await vacation_facade.reject_vacation(vacation_id, rejected_by, reason)
        
        # Verificar las llamadas
        vacation_facade._crud_operations.get_vacation_by_id.assert_awaited_once_with(vacation_id)
        vacation_facade._crud_operations.update_vacation.assert_awaited_once()
        
        # Verificar el resultado
        assert result == rejected_vacation

    @pytest.mark.asyncio
    async def test_cancel_vacation_success(
        self, 
        vacation_facade: VacationRepositoryFacade,
        sample_vacation_instance: Vacation
    ):
        """Test que verifica la cancelación exitosa de una vacación."""
        vacation_id = 1
        cancelled_by = 1
        reason = "Cambio de planes"
        
        # Configurar los mocks
        vacation_facade._crud_operations.get_vacation_by_id.return_value = sample_vacation_instance
        
        cancelled_vacation = sample_vacation_instance
        cancelled_vacation.status = VacationStatus.CANCELLED
        vacation_facade._crud_operations.update_vacation.return_value = cancelled_vacation
        
        # Ejecutar el método
        result = await vacation_facade.cancel_vacation(vacation_id, cancelled_by, reason)
        
        # Verificar las llamadas
        vacation_facade._crud_operations.get_vacation_by_id.assert_awaited_once_with(vacation_id)
        vacation_facade._crud_operations.update_vacation.assert_awaited_once()
        
        # Verificar el resultado
        assert result == cancelled_vacation


class TestVacationRepositoryFacadeEdgeCases:
    """Tests para casos límite y manejo de errores del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_vacation_by_id_not_found(
        self, 
        vacation_facade: VacationRepositoryFacade
    ):
        """Test que verifica el comportamiento cuando no se encuentra una vacación por ID."""
        vacation_id = 999
        
        # Configurar el mock para devolver None
        vacation_facade._crud_operations.get_vacation_by_id.return_value = None
        
        # Ejecutar el método
        result = await vacation_facade.get_vacation_by_id(vacation_id)
        
        # Verificar la llamada
        vacation_facade._crud_operations.get_vacation_by_id.assert_awaited_once_with(vacation_id)
        
        # Verificar el resultado
        assert result is None

    @pytest.mark.asyncio
    async def test_search_vacations_empty_result(
        self, 
        vacation_facade: VacationRepositoryFacade
    ):
        """Test que verifica el comportamiento cuando la búsqueda no devuelve resultados."""
        search_filters = {"employee_id": 999, "status": VacationStatus.APPROVED}
        
        # Configurar el mock para devolver lista vacía
        vacation_facade._query_operations.search_vacations.return_value = []
        
        # Ejecutar el método
        result = await vacation_facade.search_vacations(**search_filters)
        
        # Verificar la llamada con todos los parámetros (incluyendo defaults)
        vacation_facade._query_operations.search_vacations.assert_awaited_once_with(
            employee_id=999,
            start_date=None,
            end_date=None,
            status=VacationStatus.APPROVED,
            vacation_type=None,
            limit=100,
            offset=0
        )
        
        # Verificar el resultado
        assert result == []
        assert len(result) == 0

    @pytest.mark.asyncio
    async def test_get_by_employee_id_empty_result(
        self, 
        vacation_facade: VacationRepositoryFacade
    ):
        """Test que verifica el comportamiento cuando un empleado no tiene vacaciones."""
        employee_id = 999
        
        # Configurar el mock para devolver lista vacía
        vacation_facade._query_operations.get_by_employee_id.return_value = []
        
        # Ejecutar el método
        result = await vacation_facade.get_by_employee_id(employee_id)
        
        # Verificar la llamada
        vacation_facade._query_operations.get_by_employee_id.assert_awaited_once_with(employee_id)
        
        # Verificar el resultado
        assert result == []
        assert len(result) == 0