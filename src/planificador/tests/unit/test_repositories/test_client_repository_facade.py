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
            client_facade._crud_operations,
            "create_client",
            return_value=mock_client,
        ) as mock_create:
            # Act
            result = await client_facade.create_client(client_create)

            # Assert
            assert result == mock_client
            mock_create.assert_called_once_with(client_create.model_dump())

    # Test eliminado: create_client_with_pendulum_validation no existe en ClientRepositoryFacade

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


# Tests eliminados: create_client_with_full_validation no existe en ClientRepositoryFacade