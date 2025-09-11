"""Tests unitarios para ClientQueryBuilder.

Este módulo contiene tests para el constructor de consultas de clientes,
validando todas las funcionalidades de búsqueda, filtrado y ordenamiento
implementadas en la clase ClientQueryBuilder.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import List, Dict, Any, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, and_, or_

from planificador.database.repositories.client.client_query_builder import (
    ClientQueryBuilder,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientFilter, ClientSort
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
)
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError


class TestClientQueryBuilder:
    """Tests para ClientQueryBuilder."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def client_query_builder(self, mock_session):
        """Fixture para ClientQueryBuilder con dependencias mock."""
        return ClientQueryBuilder(session=mock_session)

    @pytest.fixture
    def mock_clients(self) -> List[Client]:
        """Fixture para lista de clientes mock."""
        clients = [
            Client(
                id=1,
                name="Client A",
                code="CA001",
                email="clienta@example.com",
                phone="+1234567890",
                contact_person="John Doe",
                is_active=True,
                notes="Cliente activo",
                created_at=datetime(2024, 1, 1),
                updated_at=datetime(2024, 1, 1)
            ),
            Client(
                id=2,
                name="Client B",
                code="CB002",
                email="clientb@example.com",
                phone="+1234567891",
                contact_person="Jane Smith",
                is_active=False,
                notes="Cliente inactivo",
                created_at=datetime(2024, 2, 1),
                updated_at=datetime(2024, 2, 1)
            ),
            Client(
                id=3,
                name="Test Client",
                code="TC003",
                email="test@example.com",
                phone="+1234567892",
                contact_person="Bob Johnson",
                is_active=True,
                notes="Cliente de prueba",
                created_at=datetime(2024, 3, 1),
                updated_at=datetime(2024, 3, 1)
            )
        ]
        return clients

    @pytest.fixture
    def client_filter(self) -> ClientFilter:
        """Fixture para filtros de cliente."""
        return ClientFilter(
            name="Test",
            code="TC",
            email="test@",
            is_active=True,
            contact_person="Bob"
        )

    @pytest.fixture
    def client_sort(self) -> ClientSort:
        """Fixture para ordenamiento de cliente."""
        return ClientSort(
            field="name",
            direction="asc"
        )

    # Tests para get_by_name
    @pytest.mark.asyncio
    async def test_get_by_name_success(
        self, client_query_builder
    ):
        """Test: Búsqueda exitosa de cliente por nombre."""
        # Arrange
        name = "Test Client"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Client(name=name)
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        client = await client_query_builder.get_by_name(name)
        
        # Assert
        assert client is not None
        assert client.name == name

    @pytest.mark.asyncio
    async def test_get_by_code_success(
        self, client_query_builder
    ):
        """Test: Búsqueda exitosa de cliente por código."""
        # Arrange
        code = "TEST001"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = Client(code=code)
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        client = await client_query_builder.get_by_code(code)
        
        # Assert
        assert client is not None
        assert client.code == code

    # Tests para code_exists
    @pytest.mark.asyncio
    async def test_code_exists_found(
        self, client_query_builder
    ):
        """Test: Código de cliente existe."""
        # Arrange
        code = "TEST001"
        mock_result = MagicMock()
        mock_result.scalar.return_value = 1  # count > 0
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await client_query_builder.code_exists(code)
        
        # Assert
        assert result is True

    @pytest.mark.asyncio
    async def test_code_exists_not_found(
        self, client_query_builder
    ):
        """Test: Código de cliente no existe."""
        # Arrange
        code = "NONEXISTENT"
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0  # count = 0
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await client_query_builder.code_exists(code)
        
        # Assert
        assert result is False

    @pytest.mark.asyncio
    async def test_search_with_advanced_filters(
        self, client_query_builder
    ):
        """Test: Búsqueda avanzada con múltiples filtros."""
        # Arrange
        mock_clients = [Client(name="Test Client", is_active=True)]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_clients
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        clients = await client_query_builder.search_with_advanced_filters(
            name_pattern="Test",
            is_active=True
        )
        
        # Assert
        assert len(clients) == 1
        assert clients[0].name == "Test Client"

    @pytest.mark.asyncio
    async def test_find_clients_with_contact_info(
        self, client_query_builder
    ):
        """Test: Búsqueda de clientes con información de contacto."""
        # Arrange
        mock_clients = [Client(name="Client with Contact", email="test@example.com")]
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_clients
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        clients = await client_query_builder.find_clients_with_contact_info()
        
        # Assert
        assert len(clients) == 1
        assert clients[0].email == "test@example.com"

    # Tests eliminados: apply_sorting
    # Este método no existe en la implementación real de ClientQueryBuilder

    # Tests para apply_pagination
    # Tests eliminados: apply_pagination
    # Este método no existe en la implementación real de ClientQueryBuilder

    # Tests eliminados: build_search_query
    # Este método no existe en la implementación real de ClientQueryBuilder

    # Tests eliminados: execute_query
    # Este método no existe en la implementación real de ClientQueryBuilder

    # Tests eliminados: count_query_results y build_complex_query
    # Estos métodos no existen en la implementación real de ClientQueryBuilder

    # Tests para name_exists
    @pytest.mark.asyncio
    async def test_name_exists_found(
        self, client_query_builder, mock_clients
    ):
        """Test: Nombre de cliente existe."""
        # Arrange
        name = "Test Client"
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 1  # count > 0
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await client_query_builder.name_exists(name)
        
        # Assert
        assert result is True
        client_query_builder.session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_name_exists_not_found(
        self, client_query_builder
    ):
        """Test: Nombre de cliente no existe."""
        # Arrange
        name = "Nonexistent Client"
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0  # count = 0
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await client_query_builder.name_exists(name)
        
        # Assert
        assert result is False
        client_query_builder.session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_name_exists_sqlalchemy_error(
        self, client_query_builder
    ):
        """Test: Error de SQLAlchemy al verificar nombre."""
        # Arrange
        name = "Test Client"
        client_query_builder.session.execute.side_effect = SQLAlchemyError(
            "Database error"
        )
        
        # Act & Assert
        with pytest.raises(Exception):  # Se espera conversión de error
            await client_query_builder.name_exists(name)

    # Tests para get_active_clients
    @pytest.mark.asyncio
    async def test_get_active_clients(
        self, client_query_builder
    ):
        """Test: Obtención de clientes activos."""
        # Arrange
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        client_query_builder.session.execute.return_value = mock_result
        
        # Act
        clients = await client_query_builder.get_active_clients()
        
        # Assert
        assert isinstance(clients, list)

    # Tests para search_clients_by_text
    @pytest.mark.asyncio
    async def test_search_clients_by_text(
        self, client_query_builder
    ):
        """Test: Búsqueda de clientes por texto."""
        # Arrange
        search_text = "test"
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        client_query_builder.session.execute.return_value = mock_result
        
        # Act
        clients = await client_query_builder.search_clients_by_text(search_text)
        
        # Assert
        assert isinstance(clients, list)

    # Tests para get_clients_by_filters
    @pytest.mark.asyncio
    async def test_get_clients_by_filters(
        self, client_query_builder
    ):
        """Test: Obtención de clientes por filtros."""
        # Arrange
        filters = {"is_active": True}
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = []
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        client_query_builder.session.execute.return_value = mock_result
        
        # Act
        clients = await client_query_builder.get_clients_by_filters(filters)
        
        # Assert
        assert isinstance(clients, list)

    # Tests para name_exists con exclude_id
    @pytest.mark.asyncio
    async def test_name_exists_with_exclude_id(
        self, client_query_builder
    ):
        """Test: Verificación de nombre existente excluyendo un ID."""
        # Arrange
        name = "Test Client"
        exclude_id = 1
        mock_result = MagicMock()
        mock_result.scalar_one.return_value = 0  # count = 0
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        exists = await client_query_builder.name_exists(name, exclude_id)
        
        # Assert
        assert exists is False

    # Test adicional para get_by_name con casos edge
    @pytest.mark.asyncio
    async def test_get_by_name_not_found(
        self, client_query_builder
    ):
        """Test: Búsqueda de cliente por nombre no encontrado."""
        # Arrange
        name = "Nonexistent Client"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        client = await client_query_builder.get_by_name(name)
        
        # Assert
        assert client is None

    # Test para get_by_code con casos edge
    @pytest.mark.asyncio
    async def test_get_by_code_not_found(
        self, client_query_builder
    ):
        """Test: Búsqueda de cliente por código no encontrado."""
        # Arrange
        code = "NONEXISTENT"
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = None
        client_query_builder.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        client = await client_query_builder.get_by_code(code)
        
        # Assert
        assert client is None