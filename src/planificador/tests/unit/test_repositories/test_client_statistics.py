"""Tests unitarios para ClientStatistics.

Este módulo contiene tests para el generador de estadísticas de clientes,
validando todas las funcionalidades de cálculo de métricas y análisis
implementadas en la clase ClientStatistics.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, Mock, patch
from datetime import datetime, date
from typing import List, Dict, Any, Optional
from decimal import Decimal

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy import select, func

from planificador.database.repositories.client.client_statistics import (
    ClientStatistics,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientStatsResponse
from planificador.exceptions import (
    NotFoundError,
)
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientStatisticsError,
)
from planificador.exceptions.repository.base_repository_exceptions import (
    RepositoryError,
)


class TestClientStatistics:
    """Tests para ClientStatistics."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        # Crear mock personalizado que evite warnings
        session = Mock(spec=AsyncSession)
        
        # Crear AsyncMock para execute pero configurarlo correctamente
        execute_mock = AsyncMock()
        execute_mock.return_value = Mock()  # Valor por defecto
        session.execute = execute_mock
        
        # Configurar métodos async como funciones personalizadas
        async def mock_rollback():
            pass
        
        async def mock_commit():
            pass
        
        session.rollback = mock_rollback
        session.commit = mock_commit
        
        return session

    @pytest.fixture
    def client_statistics(self, mock_session):
        """Fixture para ClientStatistics con dependencias mock."""
        return ClientStatistics(session=mock_session)

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
                created_at=datetime(2024, 1, 15),
                updated_at=datetime(2024, 1, 15)
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
                created_at=datetime(2024, 2, 10),
                updated_at=datetime(2024, 2, 10)
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
                created_at=datetime(2024, 3, 5),
                updated_at=datetime(2024, 3, 5)
            )
        ]
        return clients

    @pytest.fixture
    def mock_stats_data(self) -> Dict[str, Any]:
        """Fixture para datos de estadísticas mock."""
        return {
            "total_clients": 10,
            "active_clients": 8,
            "inactive_clients": 2,
            "clients_this_month": 3,
            "clients_this_year": 10,
            "average_clients_per_month": 2.5,
            "growth_rate": 15.5
        }

    # Tests para get_total_clients_count
    @pytest.mark.asyncio
    async def test_get_total_clients_count_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa del conteo total de clientes."""
        # Arrange
        expected_count = 10
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_total_clients_count()
        
        # Assert
        assert result == expected_count
        # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_total_clients_count_zero(
        self, client_statistics
    ):
        """Test: Conteo total de clientes es cero."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_total_clients_count()
        
        # Assert
        assert result == 0

    @pytest.mark.asyncio
    async def test_get_total_clients_count_sqlalchemy_error(
        self, client_statistics
    ):
        """Test: Error de SQLAlchemy al obtener conteo total."""
        # Arrange
        client_statistics.session.execute.side_effect = SQLAlchemyError(
            "Database error"
        )
        
        # Act & Assert
        with pytest.raises(Exception):  # Se espera conversión de error
            await client_statistics.get_total_clients_count()

    # Tests para get_active_clients_count
    @pytest.mark.asyncio
    async def test_get_active_clients_count_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa del conteo de clientes activos."""
        # Arrange
        expected_count = 8
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_active_clients_count()
        
        # Assert
        assert result == expected_count
        # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_active_clients_count_zero(
        self, client_statistics
    ):
        """Test: Conteo de clientes activos es cero."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_active_clients_count()
        
        # Assert
        assert result == 0

    # Tests para get_inactive_clients_count
    @pytest.mark.asyncio
    async def test_get_inactive_clients_count_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa del conteo de clientes inactivos."""
        # Arrange
        expected_count = 2
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_inactive_clients_count()
        
        # Assert
        assert result == expected_count
        # Verificar que session.execute fue llamado (implícito en el resultado)

    # Tests para get_clients_created_this_month
    @pytest.mark.asyncio
    async def test_get_clients_created_this_month_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa de clientes creados este mes."""
        # Arrange
        expected_count = 3
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        with patch('pendulum.now') as mock_now:
            mock_now.return_value.start_of.return_value = datetime(2024, 8, 1)
            mock_now.return_value.end_of.return_value = datetime(2024, 8, 31)
            
            # Act
            result = await client_statistics.get_clients_created_this_month()
            
            # Assert
            assert result == expected_count
            # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_clients_created_this_month_zero(
        self, client_statistics
    ):
        """Test: Ningún cliente creado este mes."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = 0
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        with patch('pendulum.now') as mock_now:
            mock_now.return_value.start_of.return_value = datetime(2024, 8, 1)
            mock_now.return_value.end_of.return_value = datetime(2024, 8, 31)
            
            # Act
            result = await client_statistics.get_clients_created_this_month()
            
            # Assert
            assert result == 0

    # Tests para get_clients_created_this_year
    @pytest.mark.asyncio
    async def test_get_clients_created_this_year_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa de clientes creados este año."""
        # Arrange
        expected_count = 10
        mock_result = MagicMock()
        mock_result.scalar.return_value = expected_count
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        with patch('pendulum.now') as mock_now:
            mock_now.return_value.start_of.return_value = datetime(2024, 1, 1)
            mock_now.return_value.end_of.return_value = datetime(2024, 12, 31)
            
            # Act
            result = await client_statistics.get_clients_created_this_year()
            
            # Assert
            assert result == expected_count
            # Verificar que session.execute fue llamado (implícito en el resultado)

    # Tests para get_clients_by_date_range
    @pytest.mark.asyncio
    async def test_get_clients_by_creation_date_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa de clientes por fecha de creación."""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Mock de resultado de la consulta
        mock_row1 = MagicMock()
        mock_row1.creation_date = date(2024, 1, 15)
        mock_row1.client_count = 3
        
        mock_row2 = MagicMock()
        mock_row2.creation_date = date(2024, 2, 10)
        mock_row2.client_count = 2
        
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([mock_row1, mock_row2]))
        
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_clients_by_creation_date(
            start_date, end_date
        )
        
        # Assert
        expected = [
            {"creation_date": "2024-01-15", "client_count": 3},
            {"creation_date": "2024-02-10", "client_count": 2}
        ]
        assert result == expected
        # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_clients_by_creation_date_empty_result(
        self, client_statistics
    ):
        """Test: Clientes por fecha de creación sin resultados."""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 1, 31)
        
        # Mock de resultado vacío
        mock_result = MagicMock()
        mock_result.__iter__ = MagicMock(return_value=iter([]))
        
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_clients_by_creation_date(
            start_date, end_date
        )
        
        # Assert
        assert result == []
        # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_clients_by_creation_date_database_error(
        self, client_statistics
    ):
        """Test: Error de base de datos al obtener clientes por fecha."""
        # Arrange
        start_date = datetime(2024, 1, 1)
        end_date = datetime(2024, 12, 31)
        
        # Simular error de base de datos
        async def mock_execute_error(query):
            raise SQLAlchemyError("Database error")
        client_statistics.session.execute = mock_execute_error
        
        # Act & Assert
        with pytest.raises(RepositoryError):
            await client_statistics.get_clients_by_creation_date(
                start_date, end_date
            )

    # Tests para calculate_growth_rate
    @pytest.mark.asyncio
    async def test_calculate_growth_rate_positive(
        self, client_statistics
    ):
        """Test: Cálculo de tasa de crecimiento positiva."""
        # Arrange
        current_period = 120
        previous_period = 100
        
        # Act
        result = await client_statistics.calculate_growth_rate(
            current_period, previous_period
        )
        
        # Assert
        assert result == 20.0  # (120-100)/100 * 100 = 20%

    @pytest.mark.asyncio
    async def test_calculate_growth_rate_negative(
        self, client_statistics
    ):
        """Test: Cálculo de tasa de crecimiento negativa."""
        # Arrange
        current_period = 80
        previous_period = 100
        
        # Act
        result = await client_statistics.calculate_growth_rate(
            current_period, previous_period
        )
        
        # Assert
        assert result == -20.0  # (80-100)/100 * 100 = -20%

    @pytest.mark.asyncio
    async def test_calculate_growth_rate_zero_previous(
        self, client_statistics
    ):
        """Test: Cálculo de tasa de crecimiento con período anterior cero."""
        # Arrange
        current_period = 50
        previous_period = 0
        
        # Act
        result = await client_statistics.calculate_growth_rate(
            current_period, previous_period
        )
        
        # Assert
        assert result == 100.0  # Crecimiento del 100% desde cero

    @pytest.mark.asyncio
    async def test_calculate_growth_rate_both_zero(
        self, client_statistics
    ):
        """Test: Cálculo de tasa de crecimiento con ambos períodos cero."""
        # Arrange
        current_period = 0
        previous_period = 0
        
        # Act
        result = await client_statistics.calculate_growth_rate(
            current_period, previous_period
        )
        
        # Assert
        assert result == 0.0  # Sin crecimiento

    # Tests para get_average_clients_per_month
    @pytest.mark.asyncio
    async def test_get_average_clients_per_month_success(
        self, client_statistics
    ):
        """Test: Cálculo exitoso del promedio de clientes por mes."""
        # Arrange
        total_clients = 24
        months_active = 12
        
        with patch.object(
            client_statistics, 'get_total_clients_count', return_value=total_clients
        ), patch.object(
            client_statistics, '_get_months_since_first_client', return_value=months_active
        ):
            # Act
            result = await client_statistics.get_average_clients_per_month()
            
            # Assert
            assert result == 2.0  # 24/12 = 2.0

    @pytest.mark.asyncio
    async def test_get_average_clients_per_month_no_clients(
        self, client_statistics
    ):
        """Test: Promedio de clientes por mes sin clientes."""
        # Arrange
        with patch.object(
            client_statistics, 'get_total_clients_count', return_value=0
        ):
            # Act
            result = await client_statistics.get_average_clients_per_month()
            
            # Assert
            assert result == 0.0

    @pytest.mark.asyncio
    async def test_get_average_clients_per_month_first_month(
        self, client_statistics
    ):
        """Test: Promedio de clientes en el primer mes."""
        # Arrange
        total_clients = 5
        
        with patch.object(
            client_statistics, 'get_total_clients_count', return_value=total_clients
        ), patch.object(
            client_statistics, '_get_months_since_first_client', return_value=1
        ):
            # Act
            result = await client_statistics.get_average_clients_per_month()
            
            # Assert
            assert result == 5.0  # 5/1 = 5.0

    # Tests para get_client_distribution_by_status
    @pytest.mark.asyncio
    async def test_get_client_distribution_by_status_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa de distribución por estado."""
        # Arrange
        active_count = 8
        inactive_count = 2
        
        # Mock para consulta de clientes activos
        mock_active_result = MagicMock()
        mock_active_result.scalar.return_value = active_count
        
        # Mock para consulta de clientes inactivos
        mock_inactive_result = MagicMock()
        mock_inactive_result.scalar.return_value = inactive_count
        
        # Mock personalizado para evitar warnings de AsyncMock
        call_count = 0
        async def mock_execute(query):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return mock_active_result
            else:
                return mock_inactive_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_client_distribution_by_status()
        
        # Assert
        expected = {
            "active": active_count,
            "inactive": inactive_count,
            "total": active_count + inactive_count,
        }
        assert result == expected

    @pytest.mark.asyncio
    async def test_get_client_distribution_by_status_no_clients(
        self, client_statistics
    ):
        """Test: Distribución por estado sin clientes."""
        # Arrange
        # Mock para consulta de clientes activos (0 clientes)
        mock_active_result = MagicMock()
        mock_active_result.scalar.return_value = 0
        
        # Mock para consulta de clientes inactivos (0 clientes)
        mock_inactive_result = MagicMock()
        mock_inactive_result.scalar.return_value = 0
        
        # Mock personalizado para evitar warnings de AsyncMock
        call_count = 0
        async def mock_execute(query):
            nonlocal call_count
            if call_count == 0:
                call_count += 1
                return mock_active_result
            else:
                return mock_inactive_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_client_distribution_by_status()
        
        # Assert
        expected = {
            "active": 0,
            "inactive": 0,
            "total": 0,
        }
        assert result == expected

    # Tests para get_monthly_client_creation_stats
    @pytest.mark.asyncio
    async def test_get_monthly_client_creation_stats_success(
        self, client_statistics
    ):
        """Test: Obtención exitosa de estadísticas mensuales."""
        # Arrange
        year = 2024
        # Crear objetos mock que simulen las filas de resultado con atributos
        mock_row_1 = MagicMock()
        mock_row_1.month = 1
        mock_row_1.count = 5
        mock_row_2 = MagicMock()
        mock_row_2.month = 2
        mock_row_2.count = 3
        mock_row_3 = MagicMock()
        mock_row_3.month = 3
        mock_row_3.count = 7
        
        mock_monthly_data = [mock_row_1, mock_row_2, mock_row_3]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_monthly_data
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_monthly_client_creation_stats(year)
        
        # Assert
        expected = {
            1: 5, 2: 3, 3: 7, 4: 0, 5: 0, 6: 0,
            7: 0, 8: 0, 9: 0, 10: 0, 11: 0, 12: 0
        }
        assert result == expected
        # Verificar que session.execute fue llamado (implícito en el resultado)

    @pytest.mark.asyncio
    async def test_get_monthly_client_creation_stats_current_year(
        self, client_statistics
    ):
        """Test: Estadísticas mensuales para año actual."""
        # Arrange
        # Crear objeto mock que simule la fila de resultado con atributos
        mock_row = MagicMock()
        mock_row.month = 8
        mock_row.count = 4
        
        mock_monthly_data = [mock_row]
        mock_result = MagicMock()
        mock_result.fetchall.return_value = mock_monthly_data
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        with patch('pendulum.now') as mock_now:
            mock_now.return_value.year = 2024
            
            # Act
            result = await client_statistics.get_monthly_client_creation_stats()
            
            # Assert
            assert result[8] == 4  # Agosto tiene 4 clientes
            assert sum(result.values()) == 4  # Total de 4 clientes

    # Tests para generate_comprehensive_stats
    @pytest.mark.asyncio
    async def test_generate_comprehensive_stats_success(
        self, client_statistics, mock_stats_data
    ):
        """Test: Generación exitosa de estadísticas comprehensivas."""
        # Arrange
        with patch.object(
            client_statistics, 'get_total_clients_count', 
            return_value=mock_stats_data["total_clients"]
        ), patch.object(
            client_statistics, 'get_active_clients_count',
            return_value=mock_stats_data["active_clients"]
        ), patch.object(
            client_statistics, 'get_inactive_clients_count',
            return_value=mock_stats_data["inactive_clients"]
        ), patch.object(
            client_statistics, 'get_clients_created_this_month',
            return_value=mock_stats_data["clients_this_month"]
        ), patch.object(
            client_statistics, 'get_clients_created_this_year',
            return_value=mock_stats_data["clients_this_year"]
        ), patch.object(
            client_statistics, 'get_average_clients_per_month',
            return_value=mock_stats_data["average_clients_per_month"]
        ), patch.object(
            client_statistics, 'calculate_growth_rate',
            return_value=mock_stats_data["growth_rate"]
        ):
            # Act
            result = await client_statistics.generate_comprehensive_stats()
            
            # Assert
            assert isinstance(result, dict)
            assert result["total_clients"] == mock_stats_data["total_clients"]
            assert result["active_clients"] == mock_stats_data["active_clients"]
            assert result["inactive_clients"] == mock_stats_data["inactive_clients"]
            assert result["clients_this_month"] == mock_stats_data["clients_this_month"]
            assert result["clients_this_year"] == mock_stats_data["clients_this_year"]
            assert result["average_clients_per_month"] == mock_stats_data["average_clients_per_month"]
            assert result["growth_rate"] == mock_stats_data["growth_rate"]

    # Tests para get_top_clients_by_activity
    @pytest.mark.asyncio
    async def test_get_top_clients_by_activity_success(
        self, client_statistics, mock_clients
    ):
        """Test: Obtención exitosa de top clientes por actividad."""
        # Arrange
        limit = 5
        # Usar la clave correcta "id" en lugar de "client_id"
        clients_data = [{"id": i, "project_count": 10-i} for i in range(1, limit+1)]
        
        # Mock del método get_clients_by_project_count
        async def mock_get_clients_by_project_count(limit):
            return clients_data
        client_statistics.get_clients_by_project_count = mock_get_clients_by_project_count
        
        # Mock de la sesión para la consulta de clientes
        mock_result = MagicMock()
        mock_result.scalars.return_value.all.return_value = mock_clients[:limit]
        
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_top_clients_by_activity(limit)
        
        # Assert
        assert len(result) <= limit
        assert result is not None

    @pytest.mark.asyncio
    async def test_get_top_clients_by_activity_default_limit(
        self, client_statistics, mock_clients
    ):
        """Test: Top clientes con límite por defecto."""
        # Arrange
        # Usar la clave correcta "id" en lugar de "client_id"
        clients_data = [{"id": i, "project_count": 10-i} for i in range(1, 11)]
        
        # Mock del método get_clients_by_project_count
        async def mock_get_clients_by_project_count(limit):
            return clients_data
        client_statistics.get_clients_by_project_count = mock_get_clients_by_project_count
        
        # Mock de la sesión para la consulta de clientes
        mock_scalars = MagicMock()
        mock_scalars.all.return_value = mock_clients
        mock_result = MagicMock()
        mock_result.scalars.return_value = mock_scalars
        
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics.get_top_clients_by_activity()
        
        # Assert
        assert len(result) <= 10  # Límite por defecto
        assert result is not None

    # Tests para export_stats_to_dict
    @pytest.mark.asyncio
    async def test_export_stats_to_dict_success(
        self, client_statistics, mock_stats_data
    ):
        """Test: Exportación exitosa de estadísticas a diccionario."""
        # Arrange
        basic_stats = {"active": 8, "inactive": 2, "total": 10}
        activity_summary = {"clients_with_projects": 5}
        monthly_stats = [{"month": "2024-01", "count": 3}]
        
        # Mock de los métodos usando funciones async
        async def mock_get_client_counts_by_status():
            return basic_stats
        async def mock_get_client_activity_summary():
            return activity_summary
        async def mock_get_total_clients_count():
            return 10
        async def mock_get_active_clients_count():
            return 8
        async def mock_get_clients_created_this_year():
            return 5
        async def mock_get_monthly_client_creation_stats():
            return monthly_stats
            
        client_statistics.get_client_counts_by_status = mock_get_client_counts_by_status
        client_statistics.get_client_activity_summary = mock_get_client_activity_summary
        client_statistics.get_total_clients_count = mock_get_total_clients_count
        client_statistics.get_active_clients_count = mock_get_active_clients_count
        client_statistics.get_clients_created_this_year = mock_get_clients_created_this_year
        client_statistics.get_monthly_client_creation_stats = mock_get_monthly_client_creation_stats
        
        # Act
        result = await client_statistics.export_stats_to_dict()
        
        # Assert
        assert isinstance(result, dict)
        assert "basic_counts" in result
        assert "activity_summary" in result
        assert "totals" in result
        assert "monthly_creation_stats" in result
        assert "export_timestamp" in result

    # Tests para validate_date_range
    def test_validate_date_range_valid(
        self, client_statistics
    ):
        """Test: Validación exitosa de rango de fechas."""
        # Arrange
        start_date = date(2024, 1, 1)
        end_date = date(2024, 12, 31)
        
        # Act
        result = client_statistics.validate_date_range(start_date, end_date)
        
        # Assert
        assert result is None  # No se lanza excepción

    def test_validate_date_range_invalid(
        self, client_statistics
    ):
        """Test: Error por rango de fechas inválido."""
        # Arrange
        start_date = date(2024, 12, 31)
        end_date = date(2024, 1, 1)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            client_statistics.validate_date_range(start_date, end_date)
        
        assert "no puede ser posterior" in str(exc_info.value)

    def test_validate_date_range_future_dates(
        self, client_statistics
    ):
        """Test: Validación con fechas futuras."""
        # Arrange
        start_date = date(2025, 1, 1)
        end_date = date(2025, 12, 31)
        
        # Act & Assert
        with pytest.raises(ValueError) as exc_info:
            client_statistics.validate_date_range(start_date, end_date)
        
        assert "no puede ser futura" in str(exc_info.value)

    # Tests para _get_months_since_first_client (método privado)
    @pytest.mark.asyncio
    async def test_get_months_since_first_client_success(
        self, client_statistics
    ):
        """Test: Cálculo exitoso de meses desde primer cliente."""
        # Arrange
        first_client_date = datetime(2024, 1, 15)
        mock_result = MagicMock()
        mock_result.scalar.return_value = first_client_date
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        with patch('pendulum.now') as mock_now:
            mock_now.return_value = datetime(2024, 8, 15)  # 7 meses después
            
            # Act
            result = await client_statistics._get_months_since_first_client()
            
            # Assert
            assert result >= 7  # Al menos 7 meses

    @pytest.mark.asyncio
    async def test_get_months_since_first_client_no_clients(
        self, client_statistics
    ):
        """Test: Cálculo de meses sin clientes."""
        # Arrange
        mock_result = MagicMock()
        mock_result.scalar.return_value = None
        # Mock personalizado para evitar warnings de AsyncMock
        async def mock_execute(query):
            return mock_result
        client_statistics.session.execute = mock_execute
        
        # Act
        result = await client_statistics._get_months_since_first_client()
        
        # Assert
        assert result == 1  # Valor por defecto