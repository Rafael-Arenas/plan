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