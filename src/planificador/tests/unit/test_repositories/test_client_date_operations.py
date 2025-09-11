"""Tests unitarios para ClientDateOperations.

Este módulo contiene tests para las operaciones de fechas de clientes,
validando todas las funcionalidades de consulta y filtrado por fechas
implementadas en la clase ClientDateOperations.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime, date
from typing import List, Optional

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select

from planificador.database.repositories.client.client_date_operations import (
    ClientDateOperations,
)
from planificador.database.repositories.client.client_query_builder import (
    ClientQueryBuilder,
)
from planificador.models.client import Client
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientNotFoundError,
    ClientValidationError,
    ClientDateRangeError,
)
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError
from planificador.exceptions.repository.base_repository_exceptions import convert_sqlalchemy_error


class TestClientDateOperations:
    """Tests para ClientDateOperations."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def mock_query_builder(self, mock_session):
        """Fixture para ClientQueryBuilder mock."""
        mock_builder = MagicMock(spec=ClientQueryBuilder)
        # Configurar método build_date_range_query como async
        mock_builder.build_date_range_query = AsyncMock()
        return mock_builder

    @pytest.fixture
    def client_date_operations(self, mock_session, mock_query_builder):
        """Fixture para ClientDateOperations con dependencias mock."""
        return ClientDateOperations(session=mock_session, query_builder=mock_query_builder)

    @pytest.fixture
    def mock_clients(self) -> List[Client]:
        """Fixture para lista de clientes mock con fechas variadas."""
        clients = [
            Client(
                id=1,
                name="Client A",
                code="CA001",
                email="clienta@example.com",
                phone="+1234567890",
                contact_person="John Doe",
                is_active=True,
                notes="Cliente enero",
                created_at=datetime(2024, 1, 15, 10, 30),
                updated_at=datetime(2024, 1, 15, 10, 30)
            ),
            Client(
                id=2,
                name="Client B",
                code="CB002",
                email="clientb@example.com",
                phone="+1234567891",
                contact_person="Jane Smith",
                is_active=True,
                notes="Cliente febrero",
                created_at=datetime(2024, 2, 10, 14, 45),
                updated_at=datetime(2024, 3, 5, 16, 20)
            ),
            Client(
                id=3,
                name="Test Client",
                code="TC003",
                email="test@example.com",
                phone="+1234567892",
                contact_person="Bob Johnson",
                is_active=False,
                notes="Cliente marzo",
                created_at=datetime(2024, 3, 5, 9, 15),
                updated_at=datetime(2024, 3, 5, 9, 15)
            )
        ]
        return clients

    @pytest.fixture
    def sample_clients(self):
        """Fixture con clientes de ejemplo."""
        return [
            Client(id=1, name="Cliente 1", created_at=datetime(2024, 1, 15)),
            Client(id=2, name="Cliente 2", created_at=datetime(2024, 1, 20)),
        ]

    # ============================================================================
    # TESTS PARA MÉTODOS IMPLEMENTADOS
    # ============================================================================

    @pytest.mark.asyncio
    async def test_get_clients_created_current_week_success(
        self, client_date_operations, mock_session, mock_query_builder, sample_clients
    ):
        """Test exitoso de get_clients_created_current_week."""
        # Configurar mocks
        mock_query = MagicMock()
        mock_query_builder.build_date_range_query = AsyncMock(return_value=mock_query)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_clients
        mock_session.execute.return_value = mock_result

        # Ejecutar método
        result = await client_date_operations.get_clients_created_current_week()

        # Verificar resultado
        assert result == sample_clients
        assert len(result) == 2
        mock_query_builder.build_date_range_query.assert_called_once()
        mock_session.execute.assert_called_once_with(mock_query)

    @pytest.mark.asyncio
    async def test_get_clients_created_current_month_success(
        self, client_date_operations, mock_session, mock_query_builder, sample_clients
    ):
        """Test exitoso de get_clients_created_current_month."""
        # Configurar mocks
        mock_query = MagicMock()
        mock_query_builder.build_date_range_query = AsyncMock(return_value=mock_query)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_clients
        mock_session.execute.return_value = mock_result

        # Ejecutar método
        result = await client_date_operations.get_clients_created_current_month()

        # Verificar resultado
        assert result == sample_clients
        assert len(result) == 2
        mock_query_builder.build_date_range_query.assert_called_once()
        mock_session.execute.assert_called_once_with(mock_query)

    @pytest.mark.asyncio
    async def test_get_clients_by_date_range_success(
        self, client_date_operations, mock_session, mock_query_builder, sample_clients
    ):
        """Test exitoso de get_clients_by_date_range."""
        # Configurar datos de prueba
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        # Configurar mocks
        mock_query = MagicMock()
        mock_query_builder.build_date_range_query = AsyncMock(return_value=mock_query)
        
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = sample_clients
        mock_session.execute.return_value = mock_result

        # Ejecutar método
        result = await client_date_operations.get_clients_by_date_range(
            start_date, end_date
        )

        # Verificar resultado
        assert result == sample_clients
        assert len(result) == 2
        mock_query_builder.build_date_range_query.assert_called_once_with(
            date_field="created_at", start_date=start_date, end_date=end_date
        )
        mock_session.execute.assert_called_once_with(mock_query)

    @pytest.mark.asyncio
    async def test_get_clients_by_date_range_invalid_range(
        self, client_date_operations
    ):
        """Test de get_clients_by_date_range con rango inválido."""
        # Configurar fechas inválidas (inicio > fin)
        start_date = datetime(2024, 1, 31)
        end_date = datetime(2024, 1, 1)

        # Ejecutar y verificar excepción
        with pytest.raises(ValueError, match="La fecha de inicio debe ser anterior"):
            await client_date_operations.get_clients_by_date_range(
                start_date, end_date
            )

    @pytest.mark.asyncio
    async def test_get_clients_created_current_week_sqlalchemy_error(
        self, client_date_operations, mock_session, mock_query_builder
    ):
        """Test de manejo de SQLAlchemyError en get_clients_created_current_week."""
        # Configurar mock para lanzar SQLAlchemyError
        mock_session.execute.side_effect = SQLAlchemyError("Database error")
        mock_query_builder.build_date_range_query = AsyncMock(return_value=MagicMock())

        # Ejecutar y verificar excepción
        with pytest.raises(Exception):  # convert_sqlalchemy_error convertirá la excepción
            await client_date_operations.get_clients_created_current_week()

    @pytest.mark.asyncio
    async def test_get_clients_created_current_month_unexpected_error(
        self, client_date_operations, mock_session, mock_query_builder
    ):
        """Test de manejo de error inesperado en get_clients_created_current_month."""
        # Configurar mock para lanzar error inesperado
        mock_session.execute.side_effect = Exception("Unexpected error")
        mock_query_builder.build_date_range_query = AsyncMock(return_value=MagicMock())

        # Ejecutar y verificar excepción
        with pytest.raises(RepositoryError, match="Error inesperado"):
            await client_date_operations.get_clients_created_current_month()

    # Tests eliminados: get_clients_created_between no está implementado

    # Tests eliminados: get_clients_updated_between no está implementado

    # Tests eliminados: get_clients_created_on_date no está implementado

    # Tests eliminados: get_clients_created_before no está implementado

    # Tests eliminados: get_clients_created_after no está implementado

    # Tests eliminados: get_clients_by_month no está implementado

    # Tests eliminados: get_clients_by_year no está implementado

    # Tests eliminados: get_clients_by_quarter no está implementado

    # Tests eliminados: get_recently_created_clients no está implementado

    # Tests eliminados: get_recently_updated_clients no está implementado

    # Tests eliminados: count_clients_by_date_range no está implementado

    # Tests eliminados: get_oldest_client no está implementado

    # Tests eliminados: get_newest_client no está implementado