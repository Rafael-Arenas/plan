"""Tests unitarios para ClientCRUDOperations.

Este módulo contiene tests para las operaciones CRUD especializadas
de clientes, validando la funcionalidad de creación, lectura,
actualizacion y eliminación.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError, IntegrityError

from planificador.database.repositories.client.client_crud_operations import (
    ClientCRUDOperations,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
)
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError


class TestClientCRUDOperations:
    """Tests para ClientCRUDOperations."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def mock_validator(self):
        """Fixture para validador mock."""
        validator = AsyncMock()
        return validator

    @pytest.fixture
    def crud_operations(self, mock_session, mock_validator):
        """Fixture para ClientCRUDOperations con dependencias mock."""
        return ClientCRUDOperations(
            session=mock_session,
            validator=mock_validator
        )

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

    # Tests para create_client
    @pytest.mark.asyncio
    async def test_create_client_success(
        self, crud_operations, valid_client_data, mock_client
    ):
        """Test: Creación exitosa de cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)
        crud_operations.validator.validate_client_data.return_value = None
        crud_operations.session.add = MagicMock()
        crud_operations.session.commit = AsyncMock()
        crud_operations.session.refresh = AsyncMock()
        
        # Mock del cliente creado
        crud_operations.session.add.side_effect = lambda obj: setattr(obj, 'id', 1)
        
        # Act
        with patch('planificador.database.repositories.client.client_crud_operations.Client') as MockClient:
            MockClient.return_value = mock_client
            result = await crud_operations.create_client(client_create)
        
        # Assert
        assert result is mock_client
        crud_operations.validator.validate_client_data.assert_called_once_with(
            client_create
        )
        MockClient.assert_called_once_with(**client_create.model_dump())
        crud_operations.session.add.assert_called_once_with(mock_client)
        crud_operations.session.commit.assert_called_once()
        crud_operations.session.refresh.assert_called_once_with(mock_client)

    @pytest.mark.asyncio
    async def test_create_client_validation_error(
        self, crud_operations, valid_client_data
    ):
        """Test: Error de validación al crear cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)
        validation_error = ClientValidationError(
            field="code",
            value="TC001",
            reason="Código ya existe"
        )
        crud_operations.validator.validate_client_data.side_effect = validation_error
        
        # Act & Assert
        with pytest.raises(ClientValidationError) as exc_info:
            await crud_operations.create_client(client_create)
        
        assert "Código ya existe" in str(exc_info.value)
        crud_operations.validator.validate_client_data.assert_called_once_with(
            client_create
        )

    @pytest.mark.asyncio
    async def test_create_client_sqlalchemy_error(
        self, crud_operations, valid_client_data
    ):
        """Test: Error de SQLAlchemy al crear cliente."""
        # Arrange
        client_create = ClientCreate(**valid_client_data)
        crud_operations.validator.validate_client_data.return_value = None
        crud_operations.session.add = MagicMock()
        crud_operations.session.commit = AsyncMock(
            side_effect=IntegrityError("statement", "params", "orig")
        )
        crud_operations.session.rollback = AsyncMock()
        
        # Act & Assert
        with patch('planificador.database.repositories.client.client_crud_operations.Client'):
            with pytest.raises(Exception):  # Se espera conversión de error
                await crud_operations.create_client(client_create)
        
        crud_operations.session.rollback.assert_called_once()

    # Tests para create_client_with_date_validation
    @pytest.mark.asyncio
    async def test_create_client_with_date_validation_success(
        self, crud_operations, valid_client_data, mock_client
    ):
        """Test: Creación exitosa con validación de fechas."""
        # Arrange
        crud_operations.validator.validate_client_data.return_value = None
        crud_operations.session.add = MagicMock()
        crud_operations.session.commit = AsyncMock()
        crud_operations.session.refresh = AsyncMock()
        
        # Mock del método _validate_dates_with_pendulum
        with patch.object(crud_operations, '_validate_dates_with_pendulum', return_value=valid_client_data):
            with patch('planificador.database.repositories.client.client_crud_operations.Client') as MockClient:
                MockClient.return_value = mock_client
                result = await crud_operations.create_client_with_date_validation(
                    valid_client_data
                )
        
        # Assert
        assert result is mock_client
        crud_operations.validator.validate_client_data.assert_called_once_with(
            valid_client_data
        )
        MockClient.assert_called_once_with(**valid_client_data)
        crud_operations.session.add.assert_called_once_with(mock_client)
        crud_operations.session.commit.assert_called_once()
        crud_operations.session.refresh.assert_called_once_with(mock_client)

    # Tests para get_client_by_id
    @pytest.mark.asyncio
    async def test_get_client_by_id_success(
        self, crud_operations, mock_client
    ):
        """Test: Obtención exitosa de cliente por ID."""
        # Arrange
        client_id = 1
        crud_operations.session.get.return_value = mock_client
        
        # Act
        result = await crud_operations.get_client_by_id(client_id)
        
        # Assert
        assert result == mock_client
        crud_operations.session.get.assert_called_once_with(Client, client_id)

    @pytest.mark.asyncio
    async def test_get_client_by_id_not_found(
        self, crud_operations
    ):
        """Test: Cliente no encontrado por ID."""
        # Arrange
        client_id = 999
        crud_operations.session.get.return_value = None
        
        # Act
        result = await crud_operations.get_client_by_id(client_id)
        
        # Assert
        assert result is None
        crud_operations.session.get.assert_called_once_with(Client, client_id)

    @pytest.mark.asyncio
    async def test_get_client_by_id_sqlalchemy_error(
        self, crud_operations
    ):
        """Test: Error de SQLAlchemy al obtener cliente por ID."""
        # Arrange
        client_id = 1
        crud_operations.session.get.side_effect = SQLAlchemyError("DB Error")
        
        # Act & Assert
        with pytest.raises(Exception):  # Se espera conversión de error
            await crud_operations.get_client_by_id(client_id)

    # Tests para update_client
    @pytest.mark.asyncio
    async def test_update_client_success(
        self, crud_operations, mock_client
    ):
        """Test: Actualización exitosa de cliente."""
        # Arrange
        client_id = 1
        update_data = ClientUpdate(name="Updated Client")
        
        # Mock get_client_by_id para encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=mock_client
        ):
            crud_operations.validator.validate_client_update_data.return_value = None
            crud_operations.session.flush = AsyncMock()
            crud_operations.session.refresh = AsyncMock()
            
            # Act
            result = await crud_operations.update_client(client_id, update_data)
            
            # Assert
            assert result == mock_client
            assert mock_client.name == "Updated Client"
            crud_operations.validator.validate_client_update_data.assert_called_once_with(
                {'name': 'Updated Client'}, client_id
            )

    @pytest.mark.asyncio
    async def test_update_client_not_found(
        self, crud_operations
    ):
        """Test: Error al actualizar cliente no encontrado."""
        # Arrange
        client_id = 999
        update_data = ClientUpdate(name="Updated Client")
        
        # Mock get_client_by_id para no encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=None
        ):
            # Act & Assert
            with pytest.raises(ClientNotFoundError) as exc_info:
                await crud_operations.update_client(client_id, update_data)
            
            assert f"Cliente con ID '{client_id}' no encontrado durante operación 'update_client'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_client_validation_error(
        self, crud_operations, mock_client
    ):
        """Test: Error de validación al actualizar cliente."""
        # Arrange
        client_id = 1
        update_data = ClientUpdate(email="test@example.com")
        validation_error = ClientValidationError(
            field="email",
            value="test@example.com",
            reason="Email ya existe en el sistema"
        )
        
        # Mock get_client_by_id para encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=mock_client
        ):
            crud_operations.validator.validate_client_update_data.side_effect = validation_error
            
            # Act & Assert
            with pytest.raises(ClientValidationError) as exc_info:
                await crud_operations.update_client(client_id, update_data)
            
            assert "Email ya existe en el sistema" in str(exc_info.value)

    # Tests para delete_client
    @pytest.mark.asyncio
    async def test_delete_client_success(
        self, crud_operations, mock_client
    ):
        """Test: Eliminación exitosa de cliente."""
        # Arrange
        client_id = 1
        
        # Mock get_client_by_id para encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=mock_client
        ):
            crud_operations.session.delete = Mock()
            crud_operations.session.commit = AsyncMock()
            crud_operations.validator.validate_client_deletion = AsyncMock()
            
            # Act
            result = await crud_operations.delete_client(client_id)
            
            # Assert
            assert result is True
            crud_operations.session.delete.assert_called_once_with(mock_client)
            crud_operations.session.commit.assert_called_once()

    @pytest.mark.asyncio
    async def test_delete_client_not_found(
        self, crud_operations
    ):
        """Test: Error al eliminar cliente no encontrado."""
        # Arrange
        client_id = 999
        
        # Mock get_client_by_id para no encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=None
        ):
            crud_operations.validator.validate_client_deletion = AsyncMock()
            
            # Act & Assert
            with pytest.raises(ClientNotFoundError) as exc_info:
                await crud_operations.delete_client(client_id)
            
            assert f"Cliente con ID '{client_id}' no encontrado durante operación 'delete_client'" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_client_sqlalchemy_error(
        self, crud_operations, mock_client
    ):
        """Test: Error de SQLAlchemy al eliminar cliente."""
        # Arrange
        client_id = 1
        
        # Mock get_client_by_id para encontrar el cliente
        with patch.object(
            crud_operations, 'get_client_by_id', return_value=mock_client
        ):
            crud_operations.session.delete = Mock()
            crud_operations.session.commit = AsyncMock(
                side_effect=SQLAlchemyError("DB Error")
            )
            crud_operations.session.rollback = AsyncMock()
            crud_operations.validator.validate_client_deletion = AsyncMock()
            
            # Act & Assert
            with pytest.raises(Exception):  # Se espera conversión de error
                await crud_operations.delete_client(client_id)
            
            crud_operations.session.rollback.assert_called_once()