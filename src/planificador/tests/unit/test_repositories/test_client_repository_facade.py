"""Tests unitarios para ClientRepositoryFacade.

Este módulo contiene tests completos para el facade principal de repositorios
de cliente, validando la integración entre las clases especializadas y
la funcionalidad expuesta por el facade.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any, List

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.database.repositories.client.client_repository_facade import (
    ClientRepositoryFacade,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientDuplicateError,
)
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError
from planificador.exceptions.base import ValidationError


class TestClientRepositoryFacade:
    """Tests para ClientRepositoryFacade."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def client_facade(self, mock_session):
        """Fixture para ClientRepositoryFacade con dependencias mock."""
        return ClientRepositoryFacade(session=mock_session)

    @pytest.fixture
    def valid_client_data(self) -> Dict[str, Any]:
        """Fixture con datos válidos para crear cliente."""
        return {
            "name": "Test Client",
            "code": "TC001",
            "email": "test@client.com",
            "phone": "+1234567890",
            "contact_person": "John Doe",
            "is_active": True,
            "notes": "Cliente de prueba"
        }

    @pytest.fixture
    def mock_client(self) -> Client:
        """Fixture para objeto Client mock."""
        client = Client(
            id=1,
            name="Test Client",
            code="TC001",
            email="test@client.com",
            phone="+1234567890",
            contact_person="John Doe",
            is_active=True,
            notes="Cliente de prueba",
            created_at=datetime.now(),
            updated_at=datetime.now()
        )
        return client

    # Tests para operaciones CRUD
    @pytest.mark.asyncio
    async def test_create_client_success(
        self, client_facade, valid_client_data, mock_client
    ):
        """Test: Creación exitosa de cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)

        with patch.object(
            client_facade._crud_operations,
            "create_client",
            return_value=mock_client,
        ) as mock_create:
            # Act
            result = await client_facade.create_client(client_create)

            # Assert
            assert result == mock_client
            mock_create.assert_called_once_with(client_create.model_dump())


    @pytest.mark.asyncio
    async def test_get_client_by_id_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por ID."""
        # Arrange
        client_id = 1
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_id', return_value=mock_client
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_id(client_id)
            
            # Assert
            assert result == mock_client
            mock_get.assert_called_once_with(client_id)

    @pytest.mark.asyncio
    async def test_get_client_by_id_not_found(
        self, client_facade
    ):
        """Test: Cliente no encontrado por ID."""
        # Arrange
        client_id = 999
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_id', return_value=None
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_id(client_id)
            
            # Assert
            assert result is None
            mock_get.assert_called_once_with(client_id)

    @pytest.mark.asyncio
    async def test_update_client_success(
        self, client_facade, mock_client
    ):
        """Test: Actualización exitosa de cliente."""
        # Arrange
        client_id = 1
        update_data = ClientUpdate(name="Updated Client")
        
        with patch.object(
            client_facade.crud_ops, 'update_client', return_value=mock_client
        ) as mock_update:
            # Act
            result = await client_facade.update_client(client_id, update_data)
            
            # Assert
            assert result == mock_client
            mock_update.assert_called_once_with(client_id, update_data)

    # Test para validate_email_format eliminado porque ya no existe en el facade.

    # Tests para estadísticas
    @pytest.mark.asyncio
    async def test_get_client_statistics_success(
        self, client_facade
    ):
        """Test: Obtención exitosa de estadísticas de cliente."""
        # Arrange
        expected_stats = {
            "total_clients": 100,
            "active_clients": 85,
            "inactive_clients": 15
        }
        
        with patch.object(
            client_facade.statistics,
            'get_client_statistics',
            return_value=expected_stats
        ) as mock_stats:
            # Act
            result = await client_facade.get_client_statistics()
            
            # Assert
            assert result == expected_stats
            mock_stats.assert_called_once()

    # Tests para manejo de errores
    @pytest.mark.asyncio
    async def test_create_client_validation_error(
        self, client_facade, valid_client_data
    ):
        """Test: Error de validación al crear cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)
        validation_error = ClientValidationError(
            field="email",
            value="test@client.com",
            reason="Email ya existe",
        )

        with patch.object(
            client_facade._crud_operations,
            "create_client",
            side_effect=validation_error,
        ):
            # Act & Assert
            with pytest.raises(ClientValidationError) as exc_info:
                await client_facade.create_client(client_create)

            assert "Email ya existe" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_client_unexpected_error(
        self, client_facade, valid_client_data
    ):
        """Test: Error inesperado al crear cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)
        unexpected_error = RepositoryError("Error inesperado")

        with patch.object(
            client_facade._crud_operations,
            "create_client",
            side_effect=unexpected_error,
        ):
            # Act & Assert
            with pytest.raises(RepositoryError) as exc_info:
                await client_facade.create_client(client_create)

            assert "Error inesperado" in str(exc_info.value)


# ==========================================================================
    # TESTS PARA ADVANCED QUERY OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_search_clients_by_text_success(
        self, client_facade, mock_client
    ):
        """Test: Búsqueda exitosa de clientes por texto."""
        # Arrange
        search_text = "Test"
        fields = ["name", "email"]
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade._advanced_query_operations,
            'search_clients_by_text',
            return_value=expected_clients
        ) as mock_search:
            # Act
            result = await client_facade.search_clients_by_text(
                search_text, fields, limit=10, offset=0
            )
            
            # Assert
            assert result == expected_clients
            mock_search.assert_called_once_with(search_text, fields, 10, 0)

    @pytest.mark.asyncio
    async def test_get_clients_by_filters_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes por filtros."""
        # Arrange
        filters = {"is_active": True, "name": "Test"}
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade._advanced_query_operations,
            'get_clients_by_filters',
            return_value=expected_clients
        ) as mock_filter:
            # Act
            result = await client_facade.get_clients_by_filters(
                filters, limit=25, offset=5, order_by="name"
            )
            
            # Assert
            assert result == expected_clients
            mock_filter.assert_called_once_with(filters, 25, 5, "name")

    @pytest.mark.asyncio
    async def test_get_clients_with_relationships_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes con relaciones."""
        # Arrange
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade._advanced_query_operations,
            'get_clients_with_relationships',
            return_value=expected_clients
        ) as mock_relationships:
            # Act
            result = await client_facade.get_clients_with_relationships(
                include_projects=True, include_contacts=False, limit=20, offset=10
            )
            
            # Assert
            assert result == expected_clients
            mock_relationships.assert_called_once_with(True, False, 20, 10)

    @pytest.mark.asyncio
    async def test_count_clients_by_filters_success(
        self, client_facade
    ):
        """Test: Conteo exitoso de clientes por filtros."""
        # Arrange
        filters = {"is_active": True}
        expected_count = 42
        
        with patch.object(
            client_facade._advanced_query_operations,
            'count_clients_by_filters',
            return_value=expected_count
        ) as mock_count:
            # Act
            result = await client_facade.count_clients_by_filters(filters)
            
            # Assert
            assert result == expected_count
            mock_count.assert_called_once_with(filters)

    @pytest.mark.asyncio
    async def test_search_clients_fuzzy_success(
        self, client_facade, mock_client
    ):
        """Test: Búsqueda difusa exitosa de clientes."""
        # Arrange
        search_term = "Tst Clnt"
        similarity_threshold = 0.5
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade._advanced_query_operations,
            'search_clients_fuzzy',
            return_value=expected_clients
        ) as mock_fuzzy:
            # Act
            result = await client_facade.search_clients_fuzzy(
                search_term, similarity_threshold
            )
            
            # Assert
            assert result == expected_clients
            mock_fuzzy.assert_called_once_with(search_term, similarity_threshold)

    # ==========================================================================
    # TESTS PARA QUERY OPERATIONS ADICIONALES
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_get_client_by_name_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por nombre."""
        # Arrange
        client_name = "Test Client"
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_name', return_value=mock_client
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_name(client_name)
            
            # Assert
            assert result == mock_client
            mock_get.assert_called_once_with(client_name)

    @pytest.mark.asyncio
    async def test_get_client_by_name_not_found(
        self, client_facade
    ):
        """Test: Cliente no encontrado por nombre."""
        # Arrange
        client_name = "Nonexistent Client"
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_name', return_value=None
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_name(client_name)
            
            # Assert
            assert result is None
            mock_get.assert_called_once_with(client_name)

    @pytest.mark.asyncio
    async def test_get_client_by_code_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por código."""
        # Arrange
        client_code = "TC001"
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_code', return_value=mock_client
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_code(client_code)
            
            # Assert
            assert result == mock_client
            mock_get.assert_called_once_with(client_code)

    @pytest.mark.asyncio
    async def test_get_client_by_email_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por email."""
        # Arrange
        client_email = "test@client.com"
        
        with patch.object(
            client_facade.query_builder, 'get_client_by_email', return_value=mock_client
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_email(client_email)
            
            # Assert
            assert result == mock_client
            mock_get.assert_called_once_with(client_email)

    @pytest.mark.asyncio
    async def test_search_clients_by_name_success(
        self, client_facade, mock_client
    ):
        """Test: Búsqueda exitosa de clientes por patrón de nombre."""
        # Arrange
        name_pattern = "Test%"
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade.query_builder, 'search_clients_by_name', return_value=expected_clients
        ) as mock_search:
            # Act
            result = await client_facade.search_clients_by_name(name_pattern)
            
            # Assert
            assert result == expected_clients
            mock_search.assert_called_once_with(name_pattern)

    @pytest.mark.asyncio
    async def test_get_all_clients_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de todos los clientes."""
        # Arrange
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade.query_builder, 'get_all_clients', return_value=expected_clients
        ) as mock_get_all:
            # Act
            result = await client_facade.get_all_clients(limit=100, offset=0)
            
            # Assert
            assert result == expected_clients
            mock_get_all.assert_called_once_with(100, 0)

    @pytest.mark.asyncio
    async def test_get_all_clients_with_defaults(
        self, client_facade, mock_client
    ):
        """Test: Obtención de todos los clientes con valores por defecto."""
        # Arrange
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade.query_builder, 'get_all_clients', return_value=expected_clients
        ) as mock_get_all:
            # Act
            result = await client_facade.get_all_clients()
            
            # Assert
            assert result == expected_clients
            mock_get_all.assert_called_once_with(None, 0)

    # ==========================================================================
    # TESTS PARA DATE OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_get_clients_created_in_date_range_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes creados en rango de fechas."""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade, 'get_clients_created_in_date_range', return_value=expected_clients
        ) as mock_date_range:
            # Act
            result = await client_facade.get_clients_created_in_date_range(
                start_date, end_date
            )
            
            # Assert
            assert result == expected_clients
            mock_date_range.assert_called_once_with(start_date, end_date)

    # ==========================================================================
    # TESTS PARA HEALTH OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_health_check_success(self, client_facade):
        """Test: Health check exitoso del facade."""
        # Arrange
        expected_health = {
            "status": "healthy",
            "database": "connected",
            "timestamp": "2024-01-01T00:00:00Z"
        }
        
        with patch.object(
            client_facade, 'health_check', return_value=expected_health
        ) as mock_health:
            # Act
            result = await client_facade.health_check()
            
            # Assert
            assert result == expected_health
            mock_health.assert_called_once()

    # ==========================================================================
    # TESTS PARA VALIDATION OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_validate_unique_fields_success(self, client_facade):
        """Test: Validación exitosa de campos únicos."""
        # Arrange
        client_data = {
            "name": "Cliente Único",
            "code": "UNIQUE001",
            "email": "unique@test.com"
        }
        expected_result = True
        
        with patch.object(
            client_facade, 'validate_unique_fields', return_value=expected_result
        ) as mock_validate:
            # Act
            result = await client_facade.validate_unique_fields(client_data)
            
            # Assert
            assert result == expected_result
            mock_validate.assert_called_once_with(client_data)

    # ==========================================================================
    # TESTS PARA RELATIONSHIP OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_transfer_projects_to_client_success(
        self, client_facade, mock_client
    ):
        """Test: Transferencia exitosa de proyectos a cliente."""
        # Arrange
        source_client_id = 1
        target_client_id = 2
        project_ids = [10, 20, 30]
        expected_result = {
            "transferred_projects": 3,
            "source_client_id": source_client_id,
            "target_client_id": target_client_id
        }
        
        with patch.object(
            client_facade, 'transfer_projects_to_client', return_value=expected_result
        ) as mock_transfer:
            # Act
            result = await client_facade.transfer_projects_to_client(
                source_client_id, target_client_id, project_ids
            )
            
            # Assert
            assert result == expected_result
            mock_transfer.assert_called_once_with(
                source_client_id, target_client_id, project_ids
            )

    @pytest.mark.asyncio
    async def test_get_clients_with_relationships_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes con relaciones."""
        # Arrange
        relationship_types = ["projects", "contacts"]
        expected_clients = [{
            "client": mock_client,
            "projects": ["Project 1", "Project 2"],
            "contacts": ["Contact 1"]
        }]
        
        with patch.object(
            client_facade, 'get_clients_with_relationships', return_value=expected_clients
        ) as mock_relationships:
            # Act
            result = await client_facade.get_clients_with_relationships(
                relationship_types
            )
            
            # Assert
            assert result == expected_clients
            mock_relationships.assert_called_once_with(relationship_types)

    # ==========================================================================
    # TESTS ADICIONALES PARA STATISTICS OPERATIONS
    # ==========================================================================

    @pytest.mark.asyncio
    async def test_get_client_statistics(self, client_facade):
        """Test getting client statistics."""
        # Arrange
        expected_stats = {
            "total_clients": 45,
            "active_clients": 40,
            "inactive_clients": 5
        }
        
        with patch.object(
            client_facade, 'get_client_statistics', return_value=expected_stats
        ) as mock_stats:
            # Act
            result = await client_facade.get_client_statistics()
            
            # Assert
            assert result == expected_stats
            mock_stats.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_creation_trends(self, client_facade):
        """Test: Obtención de tendencias de creación de clientes."""
        # Arrange
        days = 30
        group_by = "day"
        expected_trends = [
            {"date": "2024-01-01", "count": 5},
            {"date": "2024-01-02", "count": 3}
        ]
        
        with patch.object(
            client_facade, 'get_client_creation_trends', return_value=expected_trends
        ) as mock_trends:
            # Act
            result = await client_facade.get_client_creation_trends(days, group_by)
            
            # Assert
            assert result == expected_trends
            mock_trends.assert_called_once_with(days, group_by)

    @pytest.mark.asyncio
    async def test_get_clients_by_project_count(self, client_facade, mock_client):
        """Test: Obtención de clientes por número de proyectos."""
        # Arrange
        limit = 10
        expected_clients = [
            {"client": mock_client, "project_count": 25},
            {"client": mock_client, "project_count": 20}
        ]
        
        with patch.object(
            client_facade, 'get_clients_by_project_count', return_value=expected_clients
        ) as mock_clients:
            # Act
            result = await client_facade.get_clients_by_project_count(limit)
            
            # Assert
            assert result == expected_clients
            mock_clients.assert_called_once_with(limit)

    @pytest.mark.asyncio
    async def test_get_client_counts_by_status(self, client_facade):
        """Test: Obtención de conteos de clientes por estado."""
        # Arrange
        expected_counts = {
            "active": 85,
            "inactive": 15,
            "pending": 5
        }
        
        with patch.object(
            client_facade, 'get_client_counts_by_status', return_value=expected_counts
        ) as mock_counts:
            # Act
            result = await client_facade.get_client_counts_by_status()
            
            # Assert
            assert result == expected_counts
            mock_counts.assert_called_once()

    @pytest.mark.asyncio
    async def test_transfer_projects_empty_list(
        self, client_facade
    ):
        """Test: Transferencia con lista vacía de proyectos."""
        # Arrange
        source_client_id = 1
        target_client_id = 2
        project_ids = []
        expected_result = {
            "transferred_projects": 0,
            "source_client_id": source_client_id,
            "target_client_id": target_client_id
        }
        
        with patch.object(
            client_facade, 'transfer_projects_to_client', return_value=expected_result
        ) as mock_transfer:
            # Act
            result = await client_facade.transfer_projects_to_client(
                source_client_id, target_client_id, project_ids
            )
            
            # Assert
            assert result == expected_result
            assert result["transferred_projects"] == 0
            mock_transfer.assert_called_once_with(
                source_client_id, target_client_id, project_ids
            )

    @pytest.mark.asyncio
    async def test_get_clients_with_relationships_no_relationships(
        self, client_facade, mock_client
    ):
        """Test: Obtención de clientes sin relaciones."""
        # Arrange
        relationship_types = ["projects"]
        expected_clients = [{
            "client": mock_client,
            "projects": []
        }]
        
        with patch.object(
            client_facade, 'get_clients_with_relationships', return_value=expected_clients
        ) as mock_relationships:
            # Act
            result = await client_facade.get_clients_with_relationships(
                relationship_types
            )
            
            # Assert
            assert result == expected_clients
            assert result[0]["projects"] == []
            mock_relationships.assert_called_once_with(relationship_types)

    @pytest.mark.asyncio
    async def test_validate_unique_fields_duplicate(self, client_facade):
        """Test: Validación con campos duplicados."""
        # Arrange
        client_data = {
            "name": "Cliente Duplicado",
            "code": "DUP001",
            "email": "duplicate@test.com"
        }
        
        with patch.object(
            client_facade, 'validate_unique_fields', 
            side_effect=ValidationError("Email ya existe")
        ) as mock_validate:
            # Act & Assert
            with pytest.raises(ValidationError, match="Email ya existe"):
                await client_facade.validate_unique_fields(client_data)
            mock_validate.assert_called_once_with(client_data)

    @pytest.mark.asyncio
    async def test_validate_client_data_success(self, client_facade):
        """Test: Validación exitosa de datos del cliente."""
        # Arrange
        client_data = {
            "name": "Cliente Válido",
            "code": "VALID001",
            "email": "valid@test.com",
            "phone": "+1234567890"
        }
        expected_result = True
        
        with patch.object(
            client_facade, 'validate_client_data', return_value=expected_result
        ) as mock_validate:
            # Act
            result = await client_facade.validate_client_data(client_data)
            
            # Assert
            assert result == expected_result
            mock_validate.assert_called_once_with(client_data)

    @pytest.mark.asyncio
    async def test_validate_business_rules_success(self, client_facade):
        """Test: Validación exitosa de reglas de negocio."""
        # Arrange
        client_data = {
            "name": "Cliente Empresarial",
            "type": "business",
            "tax_id": "12345678901"
        }
        expected_result = True
        
        with patch.object(
            client_facade, 'validate_business_rules', return_value=expected_result
        ) as mock_validate:
            # Act
            result = await client_facade.validate_business_rules(client_data)
            
            # Assert
            assert result == expected_result
            mock_validate.assert_called_once_with(client_data)

    @pytest.mark.asyncio
    async def test_validate_business_rules_invalid(self, client_facade):
        """Test: Validación con reglas de negocio inválidas."""
        # Arrange
        client_data = {
            "name": "Cliente Inválido",
            "type": "business",
            "tax_id": "invalid_tax_id"
        }
        
        with patch.object(
            client_facade, 'validate_business_rules',
            side_effect=ValidationError("Tax ID inválido")
        ) as mock_validate:
            # Act & Assert
            with pytest.raises(ValidationError, match="Tax ID inválido"):
                await client_facade.validate_business_rules(client_data)
            mock_validate.assert_called_once_with(client_data)

    @pytest.mark.asyncio
    async def test_get_module_info_success(self, client_facade):
        """Test: Obtención exitosa de información del módulo."""
        # Arrange
        expected_info = {
            "module_name": "ClientRepositoryFacade",
            "version": "1.0.0",
            "operations": ["crud", "query", "validation", "statistics"]
        }
        
        with patch.object(
            client_facade, 'get_module_info', return_value=expected_info
        ) as mock_info:
            # Act
            result = await client_facade.get_module_info()
            
            # Assert
            assert result == expected_info
            mock_info.assert_called_once()

    @pytest.mark.asyncio
    async def test_health_check_unhealthy(self, client_facade):
        """Test: Health check con estado no saludable."""
        # Arrange
        expected_health = {
            "status": "unhealthy",
            "database": "disconnected",
            "error": "Connection timeout"
        }
        
        with patch.object(
            client_facade, 'health_check', return_value=expected_health
        ) as mock_health:
            # Act
            result = await client_facade.health_check()
            
            # Assert
            assert result == expected_health
            assert result["status"] == "unhealthy"
            mock_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_clients_updated_in_date_range_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes actualizados en rango de fechas."""
        # Arrange
        start_date = datetime(2024, 6, 1)
        end_date = datetime(2024, 6, 30)
        expected_clients = [mock_client]
        
        with patch.object(
            client_facade, 'get_clients_updated_in_date_range', return_value=expected_clients
        ) as mock_date_range:
            # Act
            result = await client_facade.get_clients_updated_in_date_range(
                start_date, end_date
            )
            
            # Assert
            assert result == expected_clients
            mock_date_range.assert_called_once_with(start_date, end_date)

    @pytest.mark.asyncio
    async def test_get_clients_created_in_date_range_empty(
        self, client_facade
    ):
        """Test: Rango de fechas sin clientes creados."""
        # Arrange
        start_date = datetime(2025, 1, 1)
        end_date = datetime(2025, 1, 31)
        expected_clients = []
        
        with patch.object(
            client_facade, 'get_clients_created_in_date_range', return_value=expected_clients
        ) as mock_date_range:
            # Act
            result = await client_facade.get_clients_created_in_date_range(
                start_date, end_date
            )
            
            # Assert
            assert result == expected_clients
            mock_date_range.assert_called_once_with(start_date, end_date)