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
            client_facade.crud_ops, 'create_client', return_value=mock_client
        ) as mock_create:
            # Act
            result = await client_facade.create_client(client_create)
            
            # Assert
            assert result == mock_client
            mock_create.assert_called_once_with(client_create)

    # Test eliminado: create_client_with_pendulum_validation no existe en ClientRepositoryFacade

    @pytest.mark.asyncio
    async def test_get_client_by_id_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por ID."""
        # Arrange
        client_id = 1
        
        with patch.object(
            client_facade.crud_ops, 'get_client_by_id', return_value=mock_client
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
            client_facade.crud_ops, 'get_client_by_id', return_value=None
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

    # Tests para consultas especializadas
    @pytest.mark.asyncio
    async def test_get_client_by_name_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de cliente por nombre."""
        # Arrange
        client_name = "Test Client"
        
        with patch.object(
            client_facade.query_builder, 'get_by_name', return_value=mock_client
        ) as mock_get:
            # Act
            result = await client_facade.get_client_by_name(client_name)
            
            # Assert
            assert result == mock_client
            mock_get.assert_called_once_with(client_name)

    @pytest.mark.asyncio
    async def test_get_active_clients_success(
        self, client_facade, mock_client
    ):
        """Test: Obtención exitosa de clientes activos."""
        # Arrange
        active_clients = [mock_client]
        
        with patch.object(
            client_facade.query_builder,
            'get_active_clients',
            return_value=active_clients
        ) as mock_get:
            # Act
            result = await client_facade.get_active_clients()
            
            # Assert
            assert result == active_clients
            mock_get.assert_called_once()

    # Tests para validaciones
    # Test eliminado: validate_client_code no existe en ClientRepositoryFacade
    # El facade no expone métodos validate_client_code, solo validate_email_format

    @pytest.mark.asyncio
    async def test_validate_email_format_success(
        self, client_facade
    ):
        """Test: Validación exitosa de formato de email."""
        # Arrange
        email = "test@client.com"
        
        with patch.object(
            client_facade.validator,
            'validate_email_format',
            return_value=True
        ) as mock_validate:
            # Act
            result = await client_facade.validate_email_format(email)
            
            # Assert
            assert result is True
            mock_validate.assert_called_once_with(email)

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
            'get_client_counts_by_status',
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
            reason="Email ya existe"
        )
        
        with patch.object(
            client_facade.crud_ops,
            'create_client',
            side_effect=validation_error
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
        unexpected_error = Exception("Error inesperado")
        
        with patch.object(
            client_facade.crud_ops,
            'create_client',
            side_effect=unexpected_error
        ), patch.object(
            client_facade.exception_handler,
            'handle_unexpected_error',
            side_effect=RepositoryError(
                message="Error inesperado procesado",
                operation="create_client",
                entity_type="Client"
            )
        ) as mock_handler:
            # Act & Assert
            with pytest.raises(RepositoryError) as exc_info:
                await client_facade.create_client(client_create)
            
            assert "Error inesperado procesado" in str(exc_info.value)
            mock_handler.assert_called_once_with(
                error=unexpected_error,
                operation="create_client",
                additional_context={"client_data": client_create.model_dump()}
            )

    # Tests eliminados: create_client_with_full_validation no existe en ClientRepositoryFacade