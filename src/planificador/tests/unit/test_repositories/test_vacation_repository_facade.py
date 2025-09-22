# src/planificador/tests/unit/test_repositories/test_vacation_repository_facade.py

"""
Tests unitarios para VacationRepositoryFacade.

Este módulo contiene tests para verificar el comportamiento correcto
de los métodos CRUD básicos del facade de repositorio de vacaciones.

Cobertura de Tests:
    - create_vacation: Creación de vacaciones con validación
    - update_vacation: Actualización de vacaciones existentes
    - Manejo de errores y excepciones
    - Validación de datos de entrada
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import date
from typing import Dict, Any

from planificador.models.vacation import Vacation, VacationStatus, VacationType
from planificador.repositories.vacation.vacation_repository_facade import VacationRepositoryFacade
from planificador.exceptions.repository import VacationRepositoryError


class ConcreteVacationRepositoryFacade(VacationRepositoryFacade):
    """
    Implementación concreta del VacationRepositoryFacade para testing.
    
    Esta clase implementa todos los métodos abstractos con mocks
    para permitir el testing de los métodos CRUD básicos.
    """
    
    # Implementación de métodos abstractos de IVacationQueryOperations
    async def get_by_employee_id(self, employee_id: int):
        return []
    
    async def get_by_status(self, status):
        return []
    
    async def get_by_type(self, vacation_type):
        return []
    
    async def get_by_date_range(self, start_date, end_date):
        return []
    
    async def get_by_employee_and_date_range(self, employee_id, start_date, end_date):
        return []
    
    async def search_vacations(self, **kwargs):
        return []
    
    async def get_employee_vacations(self, employee_id, year=None):
        return []
    
    async def get_pending_approvals(self, limit=50):
        return []
    
    async def check_vacation_overlap(self, start_date, end_date, employee_id=None):
        return []
    
    async def get_current_month_vacations(self):
        return []
    
    async def get_upcoming_vacations(self, days_ahead=30):
        return []
    
    async def get_with_relations(self, vacation_id):
        return None
    
    # Implementación de métodos abstractos de IVacationValidationOperations
    async def validate_create_data(self, data):
        return {"valid": True}
    
    async def validate_update_data(self, vacation_id, data):
        return {"valid": True}
    
    async def validate_vacation_exists(self, vacation_id):
        return {"exists": True}
    
    # Implementación de métodos abstractos de IVacationRelationshipOperations
    async def get_vacation_with_employee(self, vacation_id):
        return None
    
    async def get_vacation_with_all_relations(self, vacation_id):
        return None
    
    # Implementación de métodos abstractos de IVacationStatisticsOperations
    async def get_employee_vacations_with_details(self, employee_id, year=None):
        return []
    
    async def get_team_vacation_summary(self, team_id, year=None):
        return {}
    
    async def get_team_vacations_summary(self, team_ids, year=None):
        return {}
    
    async def get_vacation_balance_analysis(self, employee_id, year=None):
        return {}
    
    async def get_vacation_conflicts(self, start_date, end_date, employee_id=None):
        return []
    
    async def get_vacation_summary_by_employee(self, employee_id, year=None):
        return {}
    
    async def get_vacation_trends_by_employee(self, employee_id, years=None):
        return {}
    
    async def get_team_vacation_statistics(self, team_id, year=None):
        return {}


# =============================================================================
# FIXTURES PARA MOCKS DE SESIÓN Y MÓDULOS
# =============================================================================

@pytest.fixture
def mock_session():
    """Mock de sesión de base de datos asíncrona."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_crud_module():
    """Mock del módulo CRUD de vacaciones."""
    mock = AsyncMock()
    mock.create_vacation = AsyncMock()
    mock.update_vacation = AsyncMock()
    mock.delete_vacation = AsyncMock()
    mock.get_vacation_by_id = AsyncMock()
    mock.get_by_unique_field = AsyncMock()
    return mock


@pytest.fixture
def mock_query_module():
    """Mock del módulo de consultas de vacaciones."""
    mock = AsyncMock()
    mock.get_vacations_by_employee = AsyncMock()
    mock.get_vacations_by_date_range = AsyncMock()
    mock.get_vacations_by_status = AsyncMock()
    mock.get_vacations_by_type = AsyncMock()
    mock.search_vacations_by_criteria = AsyncMock()
    mock.get_vacations_with_pagination = AsyncMock()
    mock.count_vacations = AsyncMock()
    return mock


@pytest.fixture
def mock_validation_module():
    """Mock del módulo de validación de vacaciones."""
    mock = AsyncMock()
    mock.validate_vacation_data = AsyncMock()
    mock.validate_vacation_request = AsyncMock()
    mock.validate_vacation_id = AsyncMock()
    mock.check_vacation_conflicts = AsyncMock()
    mock.validate_business_rules = AsyncMock()
    mock.validate_data_consistency = AsyncMock()
    return mock


@pytest.fixture
def mock_relationship_module():
    """Mock del módulo de relaciones de vacaciones."""
    mock = AsyncMock()
    mock.get_vacation_with_employee_details = AsyncMock()
    mock.validate_employee_exists = AsyncMock()
    mock.get_overlapping_vacations = AsyncMock()
    mock.get_vacations_with_relationships = AsyncMock()
    return mock


@pytest.fixture
def mock_statistics_module():
    """Mock del módulo de estadísticas de vacaciones."""
    mock = AsyncMock()
    mock.get_employee_vacation_summary = AsyncMock()
    mock.get_employee_vacation_statistics = AsyncMock()
    mock.get_team_vacation_balance = AsyncMock()
    mock.get_vacation_trends = AsyncMock()
    mock.get_vacation_patterns_analysis = AsyncMock()
    mock.generate_vacation_summary_report = AsyncMock()
    return mock


@pytest.fixture
def vacation_facade(
    mock_session,
    mock_crud_module,
    mock_query_module,
    mock_validation_module,
    mock_relationship_module,
    mock_statistics_module
):
    """Fixture del VacationRepositoryFacade con módulos mockeados."""
    with patch('planificador.repositories.vacation.vacation_repository_facade.VacationCrudModule', return_value=mock_crud_module), \
         patch('planificador.repositories.vacation.vacation_repository_facade.VacationQueryModule', return_value=mock_query_module), \
         patch('planificador.repositories.vacation.vacation_repository_facade.VacationValidationModule', return_value=mock_validation_module), \
         patch('planificador.repositories.vacation.vacation_repository_facade.VacationRelationshipModule', return_value=mock_relationship_module), \
         patch('planificador.repositories.vacation.vacation_repository_facade.VacationStatisticsModule', return_value=mock_statistics_module):
        
        facade = ConcreteVacationRepositoryFacade(mock_session)
        return facade


@pytest.fixture
def sample_vacation_data():
    """Datos de ejemplo para crear una vacación."""
    return {
        "employee_id": 1,
        "start_date": date(2024, 6, 1),
        "end_date": date(2024, 6, 15),
        "vacation_type": "ANNUAL",
        "status": "PENDING",
        "description": "Vacaciones de verano",
        "days_requested": 14
    }


@pytest.fixture
def sample_vacation():
    """Instancia de ejemplo de una vacación."""
    vacation = Vacation()
    vacation.id = 1
    vacation.employee_id = 1
    vacation.start_date = date(2024, 6, 1)
    vacation.end_date = date(2024, 6, 15)
    vacation.vacation_type = "ANNUAL"
    vacation.status = "PENDING"
    vacation.description = "Vacaciones de verano"
    vacation.days_requested = 14
    return vacation


# =============================================================================
# TESTS PARA OPERACIONES CRUD
# =============================================================================

class TestVacationRepositoryFacadeCrud:
    """Tests para operaciones CRUD del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_vacation_success(
        self,
        vacation_facade,
        sample_vacation_data,
        sample_vacation
    ):
        """Test exitoso de creación de vacación."""
        # Arrange
        vacation_facade.crud_module.create_vacation.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.create_vacation(sample_vacation_data)
        
        # Assert
        vacation_facade.crud_module.create_vacation.assert_called_once_with(sample_vacation_data)
        assert result == sample_vacation
        assert result.id == 1
        assert result.employee_id == 1
        assert result.start_date == date(2024, 6, 1)
        assert result.end_date == date(2024, 6, 15)
        assert result.vacation_type == "ANNUAL"

    @pytest.mark.asyncio
    async def test_create_vacation_error(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test de error en creación de vacación."""
        # Arrange
        error_message = "Error al crear vacación"
        vacation_facade.crud_module.create_vacation.side_effect = VacationRepositoryError(error_message)
        
        # Act & Assert
        with pytest.raises(VacationRepositoryError, match=error_message):
            await vacation_facade.create_vacation(sample_vacation_data)
        
        vacation_facade.crud_module.create_vacation.assert_called_once_with(sample_vacation_data)

    @pytest.mark.asyncio
    async def test_update_vacation_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de actualización de vacación."""
        # Arrange
        vacation_id = 1
        update_data = {
            "status": "APPROVED",
            "description": "Vacaciones aprobadas"
        }
        
        # Configurar el mock para devolver la vacación actualizada
        updated_vacation = Vacation()
        updated_vacation.id = vacation_id
        updated_vacation.employee_id = sample_vacation.employee_id
        updated_vacation.start_date = sample_vacation.start_date
        updated_vacation.end_date = sample_vacation.end_date
        updated_vacation.vacation_type = sample_vacation.vacation_type
        updated_vacation.status = "APPROVED"
        updated_vacation.description = "Vacaciones aprobadas"
        updated_vacation.days_requested = sample_vacation.days_requested
        
        vacation_facade.crud_module.update_vacation.return_value = updated_vacation
        
        # Act
        result = await vacation_facade.update_vacation(vacation_id, update_data)
        
        # Assert
        vacation_facade.crud_module.update_vacation.assert_called_once_with(vacation_id, update_data)
        assert result == updated_vacation
        assert result.id == vacation_id
        assert result.status == "APPROVED"
        assert result.description == "Vacaciones aprobadas"

    @pytest.mark.asyncio
    async def test_update_vacation_error(
        self,
        vacation_facade
    ):
        """Test de error en actualización de vacación."""
        # Arrange
        vacation_id = 999  # ID inexistente
        update_data = {"status": "APPROVED"}
        error_message = "Vacación no encontrada"
        vacation_facade.crud_module.update_vacation.side_effect = VacationRepositoryError(error_message)
        
        # Act & Assert
        with pytest.raises(VacationRepositoryError, match=error_message):
            await vacation_facade.update_vacation(vacation_id, update_data)
        
        vacation_facade.crud_module.update_vacation.assert_called_once_with(vacation_id, update_data)

    @pytest.mark.asyncio
    async def test_create_vacation_with_minimal_data(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test de creación de vacación con datos mínimos requeridos."""
        # Arrange
        minimal_data = {
            "employee_id": 1,
            "start_date": date(2024, 7, 1),
            "end_date": date(2024, 7, 5),
            "vacation_type": "SICK"
        }
        
        vacation_facade.crud_module.create_vacation.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.create_vacation(minimal_data)
        
        # Assert
        vacation_facade.crud_module.create_vacation.assert_called_once_with(minimal_data)
        assert result == sample_vacation

    @pytest.mark.asyncio
    async def test_update_vacation_partial_data(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test de actualización parcial de vacación."""
        # Arrange
        vacation_id = 1
        partial_update = {"status": "CANCELLED"}
        
        updated_vacation = Vacation()
        updated_vacation.id = vacation_id
        updated_vacation.employee_id = sample_vacation.employee_id
        updated_vacation.start_date = sample_vacation.start_date
        updated_vacation.end_date = sample_vacation.end_date
        updated_vacation.vacation_type = sample_vacation.vacation_type
        updated_vacation.status = "CANCELLED"
        updated_vacation.description = sample_vacation.description
        updated_vacation.days_requested = sample_vacation.days_requested
        
        vacation_facade.crud_module.update_vacation.return_value = updated_vacation
        
        # Act
        result = await vacation_facade.update_vacation(vacation_id, partial_update)
        
        # Assert
        vacation_facade.crud_module.update_vacation.assert_called_once_with(vacation_id, partial_update)
        assert result.status == "CANCELLED"
        # Verificar que otros campos no cambiaron
        assert result.employee_id == sample_vacation.employee_id
        assert result.start_date == sample_vacation.start_date
        assert result.end_date == sample_vacation.end_date

    @pytest.mark.asyncio
    async def test_delete_vacation_success(
        self,
        vacation_facade
    ):
        """Test exitoso de eliminación de vacación."""
        # Arrange
        vacation_id = 1
        vacation_facade.crud_module.delete_vacation.return_value = True
        
        # Act
        result = await vacation_facade.delete_vacation(vacation_id)
        
        # Assert
        vacation_facade.crud_module.delete_vacation.assert_called_once_with(vacation_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_delete_vacation_not_found(
        self,
        vacation_facade
    ):
        """Test de eliminación de vacación inexistente."""
        # Arrange
        vacation_id = 999
        vacation_facade.crud_module.delete_vacation.return_value = False
        
        # Act
        result = await vacation_facade.delete_vacation(vacation_id)
        
        # Assert
        vacation_facade.crud_module.delete_vacation.assert_called_once_with(vacation_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_vacation_by_id_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención de vacación por ID."""
        # Arrange
        vacation_id = 1
        vacation_facade.crud_module.get_vacation_by_id.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.get_vacation_by_id(vacation_id)
        
        # Assert
        vacation_facade.crud_module.get_vacation_by_id.assert_called_once_with(vacation_id)
        assert result == sample_vacation
        assert result.id == vacation_id

    @pytest.mark.asyncio
    async def test_get_vacation_by_id_not_found(
        self,
        vacation_facade
    ):
        """Test de obtención de vacación por ID inexistente."""
        # Arrange
        vacation_id = 999
        vacation_facade.crud_module.get_vacation_by_id.return_value = None
        
        # Act
        result = await vacation_facade.get_vacation_by_id(vacation_id)
        
        # Assert
        vacation_facade.crud_module.get_vacation_by_id.assert_called_once_with(vacation_id)
        assert result is None

    @pytest.mark.asyncio
    async def test_get_by_unique_field_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención por campo único."""
        # Arrange
        field_name = "employee_id"
        field_value = 1
        vacation_facade.crud_module.get_by_unique_field.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.get_by_unique_field(field_name, field_value)
        
        # Assert
        vacation_facade.crud_module.get_by_unique_field.assert_called_once_with(field_name, field_value)
        assert result == sample_vacation


# =============================================================================
# TESTS PARA OPERACIONES DE CONSULTA
# =============================================================================

class TestVacationRepositoryFacadeQuery:
    """Tests para operaciones de consulta del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_vacations_by_employee_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención de vacaciones por empleado."""
        # Arrange
        employee_id = 1
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.get_vacations_by_employee.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_vacations_by_employee(employee_id)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_employee.assert_called_once_with(employee_id, True)
        assert result == expected_vacations
        assert len(result) == 1
        assert result[0].employee_id == employee_id

    @pytest.mark.asyncio
    async def test_get_vacations_by_employee_inactive(
        self,
        vacation_facade
    ):
        """Test de obtención de vacaciones incluyendo inactivas."""
        # Arrange
        employee_id = 1
        vacation_facade.query_module.get_vacations_by_employee.return_value = []
        
        # Act
        result = await vacation_facade.get_vacations_by_employee(employee_id, active_only=False)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_employee.assert_called_once_with(employee_id, False)
        assert result == []

    @pytest.mark.asyncio
    async def test_get_vacations_by_date_range_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención por rango de fechas."""
        # Arrange
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.get_vacations_by_date_range.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_vacations_by_date_range(start_date, end_date)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_date_range.assert_called_once_with(
            start_date, end_date, None
        )
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_get_vacations_by_date_range_with_employee(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test de obtención por rango de fechas con empleado específico."""
        # Arrange
        start_date = date(2024, 6, 1)
        end_date = date(2024, 6, 30)
        employee_id = 1
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.get_vacations_by_date_range.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_vacations_by_date_range(start_date, end_date, employee_id)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_date_range.assert_called_once_with(
            start_date, end_date, employee_id
        )
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_get_vacations_by_status_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención por estado."""
        # Arrange
        status = "PENDING"
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.get_vacations_by_status.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_vacations_by_status(status)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_status.assert_called_once_with(status, None)
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_get_vacations_by_type_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención por tipo."""
        # Arrange
        vacation_type = "ANNUAL"
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.get_vacations_by_type.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_vacations_by_type(vacation_type)
        
        # Assert
        vacation_facade.query_module.get_vacations_by_type.assert_called_once_with(vacation_type, None)
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_search_vacations_by_criteria_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de búsqueda por criterios."""
        # Arrange
        criteria = {"status": "PENDING", "vacation_type": "ANNUAL"}
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.search_vacations_by_criteria.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.search_vacations_by_criteria(criteria)
        
        # Assert
        vacation_facade.query_module.search_vacations_by_criteria.assert_called_once_with(
            criteria, None, None
        )
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_search_vacations_with_pagination_params(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test de búsqueda con parámetros de paginación."""
        # Arrange
        criteria = {"status": "APPROVED"}
        limit = 10
        offset = 20
        expected_vacations = [sample_vacation]
        vacation_facade.query_module.search_vacations_by_criteria.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.search_vacations_by_criteria(criteria, limit, offset)
        
        # Assert
        vacation_facade.query_module.search_vacations_by_criteria.assert_called_once_with(
            criteria, limit, offset
        )
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_get_vacations_with_pagination_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención con paginación."""
        # Arrange
        page = 1
        page_size = 20
        expected_result = ([sample_vacation], 1)
        vacation_facade.query_module.get_vacations_with_pagination.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_vacations_with_pagination(page, page_size)
        
        # Assert
        vacation_facade.query_module.get_vacations_with_pagination.assert_called_once_with(
            page, page_size, None
        )
        assert result == expected_result
        assert len(result[0]) == 1
        assert result[1] == 1

    @pytest.mark.asyncio
    async def test_count_vacations_success(
        self,
        vacation_facade
    ):
        """Test exitoso de conteo de vacaciones."""
        # Arrange
        expected_count = 5
        vacation_facade.query_module.count_vacations.return_value = expected_count
        
        # Act
        result = await vacation_facade.count_vacations()
        
        # Assert
        vacation_facade.query_module.count_vacations.assert_called_once_with(None)
        assert result == expected_count

    @pytest.mark.asyncio
    async def test_count_vacations_with_filters(
        self,
        vacation_facade
    ):
        """Test de conteo con filtros."""
        # Arrange
        filters = {"status": "APPROVED"}
        expected_count = 3
        vacation_facade.query_module.count_vacations.return_value = expected_count
        
        # Act
        result = await vacation_facade.count_vacations(filters)
        
        # Assert
        vacation_facade.query_module.count_vacations.assert_called_once_with(filters)
        assert result == expected_count


# =============================================================================
# TESTS PARA OPERACIONES DE VALIDACIÓN
# =============================================================================

class TestVacationRepositoryFacadeValidation:
    """Tests para operaciones de validación del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_validate_vacation_data_success(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test exitoso de validación de datos."""
        # Arrange
        expected_result = {"is_valid": True, "errors": []}
        vacation_facade.validation_module.validate_vacation_data.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_vacation_data(sample_vacation_data)
        
        # Assert
        vacation_facade.validation_module.validate_vacation_data.assert_called_once_with(sample_vacation_data)
        assert result == expected_result
        assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_vacation_data_invalid(
        self,
        vacation_facade
    ):
        """Test de validación con datos inválidos."""
        # Arrange
        invalid_data = {"employee_id": None, "start_date": "invalid"}
        expected_result = {
            "is_valid": False,
            "errors": ["employee_id es requerido", "start_date debe ser una fecha válida"]
        }
        vacation_facade.validation_module.validate_vacation_data.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_vacation_data(invalid_data)
        
        # Assert
        vacation_facade.validation_module.validate_vacation_data.assert_called_once_with(invalid_data)
        assert result == expected_result
        assert result["is_valid"] is False
        assert len(result["errors"]) == 2

    @pytest.mark.asyncio
    async def test_validate_vacation_request_success(
        self,
        vacation_facade
    ):
        """Test exitoso de validación de solicitud."""
        # Arrange
        employee_id = 1
        start_date = date(2024, 7, 1)
        end_date = date(2024, 7, 15)
        vacation_type = "ANNUAL"
        expected_result = {"is_valid": True, "conflicts": []}
        vacation_facade.validation_module.validate_vacation_request.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_vacation_request(
            employee_id, start_date, end_date, vacation_type
        )
        
        # Assert
        vacation_facade.validation_module.validate_vacation_request.assert_called_once_with(
            employee_id, start_date, end_date, vacation_type
        )
        assert result == expected_result
        assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_vacation_id_exists(
        self,
        vacation_facade
    ):
        """Test de validación de ID existente."""
        # Arrange
        vacation_id = 1
        expected_result = {"exists": True, "vacation_id": vacation_id}
        vacation_facade.validation_module.validate_vacation_id.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_vacation_id(vacation_id)
        
        # Assert
        vacation_facade.validation_module.validate_vacation_id.assert_called_once_with(vacation_id)
        assert result == expected_result
        assert result["exists"] is True

    @pytest.mark.asyncio
    async def test_check_vacation_conflicts_no_conflicts(
        self,
        vacation_facade
    ):
        """Test de verificación sin conflictos."""
        # Arrange
        employee_id = 1
        start_date = date(2024, 8, 1)
        end_date = date(2024, 8, 15)
        expected_result = {"has_conflicts": False, "conflicts": []}
        vacation_facade.validation_module.check_vacation_conflicts.return_value = expected_result
        
        # Act
        result = await vacation_facade.check_vacation_conflicts(employee_id, start_date, end_date)
        
        # Assert
        vacation_facade.validation_module.check_vacation_conflicts.assert_called_once_with(
            employee_id, start_date, end_date, None
        )
        assert result == expected_result
        assert result["has_conflicts"] is False

    @pytest.mark.asyncio
    async def test_check_vacation_conflicts_with_conflicts(
        self,
        vacation_facade
    ):
        """Test de verificación con conflictos."""
        # Arrange
        employee_id = 1
        start_date = date(2024, 6, 10)
        end_date = date(2024, 6, 20)
        expected_result = {
            "has_conflicts": True,
            "conflicts": [{"vacation_id": 2, "overlap_days": 5}]
        }
        vacation_facade.validation_module.check_vacation_conflicts.return_value = expected_result
        
        # Act
        result = await vacation_facade.check_vacation_conflicts(employee_id, start_date, end_date)
        
        # Assert
        vacation_facade.validation_module.check_vacation_conflicts.assert_called_once_with(
            employee_id, start_date, end_date, None
        )
        assert result == expected_result
        assert result["has_conflicts"] is True
        assert len(result["conflicts"]) == 1

    @pytest.mark.asyncio
    async def test_validate_business_rules_success(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test exitoso de validación de reglas de negocio."""
        # Arrange
        operation = "create"
        expected_result = {"is_valid": True, "violations": []}
        vacation_facade.validation_module.validate_business_rules.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_business_rules(operation, sample_vacation_data)
        
        # Assert
        vacation_facade.validation_module.validate_business_rules.assert_called_once_with(
            operation, sample_vacation_data
        )
        assert result == expected_result
        assert result["is_valid"] is True

    @pytest.mark.asyncio
    async def test_validate_data_consistency_success(
        self,
        vacation_facade
    ):
        """Test exitoso de validación de consistencia."""
        # Arrange
        expected_result = {"is_consistent": True, "issues": []}
        vacation_facade.validation_module.validate_data_consistency.return_value = expected_result
        
        # Act
        result = await vacation_facade.validate_data_consistency()
        
        # Assert
        vacation_facade.validation_module.validate_data_consistency.assert_called_once()
        assert result == expected_result
        assert result["is_consistent"] is True


# =============================================================================
# TESTS PARA OPERACIONES DE RELACIONES
# =============================================================================

class TestVacationRepositoryFacadeRelationships:
    """Tests para operaciones de relaciones del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_vacation_with_employee_details_success(
        self,
        vacation_facade
    ):
        """Test exitoso de obtención con detalles del empleado."""
        # Arrange
        vacation_id = 1
        expected_result = {
            "vacation": {"id": 1, "employee_id": 1},
            "employee": {"id": 1, "name": "Juan Pérez"}
        }
        vacation_facade.relationship_module.get_vacation_with_employee_details.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_vacation_with_employee_details(vacation_id)
        
        # Assert
        vacation_facade.relationship_module.get_vacation_with_employee_details.assert_called_once_with(vacation_id)
        assert result == expected_result
        assert result["vacation"]["id"] == vacation_id

    @pytest.mark.asyncio
    async def test_validate_employee_exists_true(
        self,
        vacation_facade
    ):
        """Test de validación de empleado existente."""
        # Arrange
        employee_id = 1
        vacation_facade.relationship_module.validate_employee_exists.return_value = True
        
        # Act
        result = await vacation_facade.validate_employee_exists(employee_id)
        
        # Assert
        vacation_facade.relationship_module.validate_employee_exists.assert_called_once_with(employee_id)
        assert result is True

    @pytest.mark.asyncio
    async def test_validate_employee_exists_false(
        self,
        vacation_facade
    ):
        """Test de validación de empleado inexistente."""
        # Arrange
        employee_id = 999
        vacation_facade.relationship_module.validate_employee_exists.return_value = False
        
        # Act
        result = await vacation_facade.validate_employee_exists(employee_id)
        
        # Assert
        vacation_facade.relationship_module.validate_employee_exists.assert_called_once_with(employee_id)
        assert result is False

    @pytest.mark.asyncio
    async def test_get_overlapping_vacations_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de obtención de vacaciones solapadas."""
        # Arrange
        employee_id = 1
        start_date = date(2024, 6, 10)
        end_date = date(2024, 6, 20)
        expected_vacations = [sample_vacation]
        vacation_facade.relationship_module.get_overlapping_vacations.return_value = expected_vacations
        
        # Act
        result = await vacation_facade.get_overlapping_vacations(employee_id, start_date, end_date)
        
        # Assert
        vacation_facade.relationship_module.get_overlapping_vacations.assert_called_once_with(
            employee_id, start_date, end_date, None
        )
        assert result == expected_vacations

    @pytest.mark.asyncio
    async def test_get_vacations_with_relationships_success(
        self,
        vacation_facade
    ):
        """Test exitoso de obtención con relaciones."""
        # Arrange
        vacation_ids = [1, 2, 3]
        expected_result = [
            {"vacation": {"id": 1}, "employee": {"id": 1}},
            {"vacation": {"id": 2}, "employee": {"id": 2}}
        ]
        vacation_facade.relationship_module.get_vacations_with_relationships.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_vacations_with_relationships(vacation_ids)
        
        # Assert
        vacation_facade.relationship_module.get_vacations_with_relationships.assert_called_once_with(
            vacation_ids, True
        )
        assert result == expected_result
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_employee_vacation_summary_success(
        self,
        vacation_facade
    ):
        """Test exitoso de resumen de vacaciones del empleado."""
        # Arrange
        employee_id = 1
        year = 2024
        expected_result = {
            "employee_id": employee_id,
            "year": year,
            "total_days": 25,
            "used_days": 10,
            "remaining_days": 15
        }
        vacation_facade.relationship_module.get_employee_vacation_summary.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_employee_vacation_summary(employee_id, year)
        
        # Assert
        vacation_facade.relationship_module.get_employee_vacation_summary.assert_called_once_with(
            employee_id, year
        )
        assert result == expected_result
        assert result["employee_id"] == employee_id


# =============================================================================
# TESTS PARA OPERACIONES DE ESTADÍSTICAS
# =============================================================================

class TestVacationRepositoryFacadeStatistics:
    """Tests para operaciones de estadísticas del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_get_employee_vacation_statistics_success(
        self,
        vacation_facade
    ):
        """Test exitoso de estadísticas del empleado."""
        # Arrange
        employee_id = 1
        year = 2024
        expected_result = {
            "employee_id": employee_id,
            "year": year,
            "statistics": {
                "total_vacations": 3,
                "total_days": 21,
                "average_duration": 7,
                "most_common_type": "ANNUAL"
            }
        }
        vacation_facade.statistics_module.get_employee_vacation_statistics.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_employee_vacation_statistics(employee_id, year)
        
        # Assert
        vacation_facade.statistics_module.get_employee_vacation_statistics.assert_called_once_with(
            employee_id, year
        )
        assert result == expected_result
        assert result["employee_id"] == employee_id

    @pytest.mark.asyncio
    async def test_get_team_vacation_balance_success(
        self,
        vacation_facade
    ):
        """Test exitoso de balance del equipo."""
        # Arrange
        team_id = 1
        year = 2024
        expected_result = {
            "team_id": team_id,
            "year": year,
            "balance": {
                "total_allocated": 250,
                "total_used": 180,
                "total_remaining": 70,
                "utilization_rate": 0.72
            }
        }
        vacation_facade.statistics_module.get_team_vacation_balance.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_team_vacation_balance(team_id, year)
        
        # Assert
        vacation_facade.statistics_module.get_team_vacation_balance.assert_called_once_with(
            team_id, year
        )
        assert result == expected_result
        assert result["team_id"] == team_id

    @pytest.mark.asyncio
    async def test_get_vacation_trends_success(
        self,
        vacation_facade
    ):
        """Test exitoso de tendencias de vacaciones."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        granularity = "monthly"
        expected_result = [
            {"period": "2024-01", "total_days": 45},
            {"period": "2024-02", "total_days": 38}
        ]
        vacation_facade.statistics_module.get_vacation_trends.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_vacation_trends(start_date, end_date, granularity)
        
        # Assert
        vacation_facade.statistics_module.get_vacation_trends.assert_called_once_with(
            start_date, end_date, granularity
        )
        assert result == expected_result
        assert len(result) == 2

    @pytest.mark.asyncio
    async def test_get_vacation_patterns_analysis_success(
        self,
        vacation_facade
    ):
        """Test exitoso de análisis de patrones."""
        # Arrange
        employee_id = 1
        year = 2024
        expected_result = {
            "patterns": {
                "preferred_months": ["July", "December"],
                "average_duration": 7.5,
                "frequency": "quarterly"
            }
        }
        vacation_facade.statistics_module.get_vacation_patterns_analysis.return_value = expected_result
        
        # Act
        result = await vacation_facade.get_vacation_patterns_analysis(employee_id, None, year)
        
        # Assert
        vacation_facade.statistics_module.get_vacation_patterns_analysis.assert_called_once_with(
            employee_id, None, year
        )
        assert result == expected_result

    @pytest.mark.asyncio
    async def test_generate_vacation_summary_report_success(
        self,
        vacation_facade
    ):
        """Test exitoso de generación de reporte resumen."""
        # Arrange
        year = 2024
        include_projections = True
        expected_result = {
            "year": year,
            "summary": {
                "total_employees": 50,
                "total_vacations": 150,
                "total_days": 1050
            },
            "projections": {
                "remaining_year_estimate": 300
            }
        }
        vacation_facade.statistics_module.generate_vacation_summary_report.return_value = expected_result
        
        # Act
        result = await vacation_facade.generate_vacation_summary_report(year, include_projections)
        
        # Assert
        vacation_facade.statistics_module.generate_vacation_summary_report.assert_called_once_with(
            year, include_projections
        )
        assert result == expected_result
        assert result["year"] == year


# =============================================================================
# TESTS PARA MÉTODOS COMPUESTOS DE ALTO NIVEL
# =============================================================================

class TestVacationRepositoryFacadeComposite:
    """Tests para métodos compuestos del VacationRepositoryFacade."""

    @pytest.mark.asyncio
    async def test_create_vacation_with_validation_success(
        self,
        vacation_facade,
        sample_vacation_data,
        sample_vacation
    ):
        """Test exitoso de creación con validación completa."""
        # Arrange
        vacation_facade.validation_module.validate_vacation_data.return_value = {
            "is_valid": True, "errors": []
        }
        vacation_facade.validation_module.validate_business_rules.return_value = {
            "is_valid": True, "violations": []
        }
        vacation_facade.validation_module.check_vacation_conflicts.return_value = {
            "has_conflicts": False, "conflicts": []
        }
        vacation_facade.crud_module.create_vacation.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.create_vacation_with_validation(sample_vacation_data)
        
        # Assert
        assert result["success"] is True
        assert result["vacation"] == sample_vacation
        assert "validation_result" in result
        vacation_facade.validation_module.validate_vacation_data.assert_called_once()
        vacation_facade.validation_module.validate_business_rules.assert_called_once()
        vacation_facade.validation_module.check_vacation_conflicts.assert_called_once()
        vacation_facade.crud_module.create_vacation.assert_called_once()

    @pytest.mark.asyncio
    async def test_create_vacation_with_validation_invalid_data(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test de creación con datos inválidos."""
        # Arrange
        vacation_facade.validation_module.validate_vacation_data.return_value = {
            "is_valid": False,
            "errors": ["start_date es requerido"]
        }
        
        # Act
        result = await vacation_facade.create_vacation_with_validation(sample_vacation_data)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Datos de vacación inválidos"
        assert result["vacation"] is None
        assert "validation_errors" in result
        vacation_facade.validation_module.validate_vacation_data.assert_called_once()
        vacation_facade.crud_module.create_vacation.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_vacation_with_validation_business_rules_violation(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test de creación con violación de reglas de negocio."""
        # Arrange
        vacation_facade.validation_module.validate_vacation_data.return_value = {
            "is_valid": True, "errors": []
        }
        vacation_facade.validation_module.validate_business_rules.return_value = {
            "is_valid": False,
            "errors": ["Excede el límite anual de días"]
        }
        
        # Act
        result = await vacation_facade.create_vacation_with_validation(sample_vacation_data)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Violación de reglas de negocio"
        assert result["vacation"] is None
        vacation_facade.validation_module.validate_business_rules.assert_called_once()
        vacation_facade.crud_module.create_vacation.assert_not_called()

    @pytest.mark.asyncio
    async def test_create_vacation_with_validation_conflicts(
        self,
        vacation_facade,
        sample_vacation_data
    ):
        """Test de creación con conflictos detectados."""
        # Arrange
        vacation_facade.validation_module.validate_vacation_data.return_value = {
            "is_valid": True, "errors": []
        }
        vacation_facade.validation_module.validate_business_rules.return_value = {
            "is_valid": True, "violations": []
        }
        vacation_facade.validation_module.check_vacation_conflicts.return_value = {
            "has_conflicts": True,
            "conflicts": [{"vacation_id": 2, "overlap_days": 3}]
        }
        
        # Act
        result = await vacation_facade.create_vacation_with_validation(sample_vacation_data)
        
        # Assert
        assert result["success"] is False
        assert result["error"] == "Conflictos detectados con vacaciones existentes"
        assert result["vacation"] is None
        assert "conflicts" in result
        vacation_facade.validation_module.check_vacation_conflicts.assert_called_once()
        vacation_facade.crud_module.create_vacation.assert_not_called()

    @pytest.mark.asyncio
    async def test_get_vacation_dashboard_data_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de datos de dashboard para empleado."""
        # Arrange
        employee_id = 1
        year = 2024
        
        # Configurar mocks
        vacation_facade.statistics_module.get_employee_vacation_statistics.return_value = {
            "total_vacations": 3, "total_days": 21
        }
        vacation_facade.relationship_module.get_employee_vacation_summary.return_value = {
            "used_days": 10, "remaining_days": 15
        }
        vacation_facade.statistics_module.get_vacation_patterns_analysis.return_value = {
            "patterns": {"preferred_months": ["July"]}
        }
        vacation_facade.query_module.get_vacations_by_employee.return_value = [sample_vacation]
        vacation_facade.statistics_module.get_vacation_trends.return_value = [
            {"period": "2024-01", "total_days": 5}
        ]
        
        # Act
        result = await vacation_facade.get_vacation_dashboard_data(employee_id, None, year)
        
        # Assert
        assert "summary" in result
        assert "statistics" in result
        assert "trends" in result
        assert "patterns" in result
        assert "recent_vacations" in result
        assert len(result["recent_vacations"]) == 1
        vacation_facade.statistics_module.get_employee_vacation_statistics.assert_called_once()
        vacation_facade.relationship_module.get_employee_vacation_summary.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_vacation_dashboard_data_team_success(
        self,
        vacation_facade
    ):
        """Test exitoso de datos de dashboard para equipo."""
        # Arrange
        team_id = 1
        year = 2024
        
        # Configurar mocks
        vacation_facade.statistics_module.get_team_vacation_balance.return_value = {
            "total_allocated": 250, "total_used": 180
        }
        vacation_facade.statistics_module.get_vacation_patterns_analysis.return_value = {
            "patterns": {"team_trends": "high_summer_usage"}
        }
        vacation_facade.statistics_module.get_vacation_trends.return_value = [
            {"period": "2024-01", "total_days": 45}
        ]
        
        # Act
        result = await vacation_facade.get_vacation_dashboard_data(None, team_id, year)
        
        # Assert
        assert "summary" in result
        assert "statistics" in result
        assert "trends" in result
        assert "patterns" in result
        vacation_facade.statistics_module.get_team_vacation_balance.assert_called_once()
        vacation_facade.statistics_module.get_vacation_patterns_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_bulk_vacation_operation_create_success(
        self,
        vacation_facade,
        sample_vacation
    ):
        """Test exitoso de operación en lote - crear."""
        # Arrange
        vacation_data_list = [
            {"employee_id": 1, "start_date": date(2024, 7, 1), "end_date": date(2024, 7, 5)},
            {"employee_id": 2, "start_date": date(2024, 8, 1), "end_date": date(2024, 8, 5)}
        ]
        
        # Configurar mocks para validación exitosa
        vacation_facade.validation_module.validate_vacation_data.return_value = {
            "is_valid": True, "errors": []
        }
        vacation_facade.validation_module.validate_business_rules.return_value = {
            "is_valid": True, "violations": []
        }
        vacation_facade.validation_module.check_vacation_conflicts.return_value = {
            "has_conflicts": False, "conflicts": []
        }
        vacation_facade.crud_module.create_vacation.return_value = sample_vacation
        
        # Act
        result = await vacation_facade.bulk_vacation_operation("create", vacation_data_list)
        
        # Assert
        assert len(result) == 2
        for i, res in enumerate(result):
            assert res["index"] == i
            assert res["success"] is True
            assert res["vacation_id"] == sample_vacation.id
            assert res["error"] is None

    @pytest.mark.asyncio
    async def test_bulk_vacation_operation_update_missing_id(
        self,
        vacation_facade
    ):
        """Test de operación en lote - actualizar sin ID."""
        # Arrange
        vacation_data_list = [
            {"status": "APPROVED"},  # Sin ID
            {"id": 2, "status": "REJECTED"}
        ]
        
        vacation_facade.crud_module.update_vacation.return_value = Vacation()
        
        # Act
        result = await vacation_facade.bulk_vacation_operation("update", vacation_data_list)
        
        # Assert
        assert len(result) == 2
        assert result[0]["success"] is False
        assert "ID de vacación requerido" in result[0]["error"]
        assert result[1]["success"] is True