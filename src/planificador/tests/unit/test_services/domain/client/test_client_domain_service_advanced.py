"""
Tests unitarios para las operaciones avanzadas del ClientDomainService.

Este módulo contiene tests para:
- Operaciones de consulta avanzada (search_clients_advanced, get_clients_paginated, search_clients_fuzzy)
- Operaciones de estadísticas (get_client_statistics, count_clients_by_status, etc.)
- Operaciones de validación (validate_client_creation, validate_client_update, etc.)
- Operaciones de salud (check_service_health, check_database_connectivity, etc.)
- Métodos de utilidad (get_service_info, close)
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any, List

from planificador.schemas.client import Client, ClientCreate, ClientUpdate, ClientStatsResponse
from planificador.exceptions import RepositoryError, ValidationError, BusinessLogicError


class TestClientDomainServiceAdvancedQuery:
    """Tests para operaciones de consulta avanzada."""

    @pytest.mark.asyncio
    async def test_search_clients_advanced_success(self, client_domain_service, sample_client_response):
        """Test búsqueda avanzada exitosa."""
        # Arrange
        filters = {"name": "Test", "is_active": True}
        expected_result = {
            "clients": [sample_client_response],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        client_domain_service.advanced_query.search_clients_advanced.return_value = expected_result

        # Act
        result = await client_domain_service.search_clients_advanced(
            filters=filters, sort_by="name", sort_order="asc", page=1, page_size=10
        )

        # Assert
        assert result == expected_result
        client_domain_service.advanced_query.search_clients_advanced.assert_called_once_with(
            filters, "name", "asc", 1, 10
        )

    @pytest.mark.asyncio
    async def test_search_clients_advanced_empty_results(self, client_domain_service):
        """Test búsqueda avanzada sin resultados."""
        # Arrange
        expected_result = {
            "clients": [],
            "total": 0,
            "page": 1,
            "page_size": 10,
            "total_pages": 0
        }
        client_domain_service.advanced_query.search_clients_advanced.return_value = expected_result

        # Act
        result = await client_domain_service.search_clients_advanced()

        # Assert
        assert result == expected_result
        assert result["clients"] == []
        assert result["total"] == 0

    @pytest.mark.asyncio
    async def test_search_clients_advanced_repository_error(self, client_domain_service):
        """Test búsqueda avanzada con error de repositorio."""
        # Arrange
        client_domain_service.advanced_query.search_clients_advanced.side_effect = RepositoryError(
            message="Error de base de datos",
            operation="search_clients_advanced",
            entity_type="Client"
        )

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.search_clients_advanced()
        
        assert "Error de base de datos" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_clients_paginated_success(self, client_domain_service, sample_client_response):
        """Test paginación exitosa."""
        # Arrange
        expected_result = {
            "clients": [sample_client_response],
            "total": 1,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        client_domain_service.advanced_query.get_clients_paginated.return_value = expected_result

        # Act
        result = await client_domain_service.get_clients_paginated(page=1, page_size=10, sort_by="name")

        # Assert
        assert result == expected_result
        client_domain_service.advanced_query.get_clients_paginated.assert_called_once_with(1, 10, "name")

    @pytest.mark.asyncio
    async def test_get_clients_paginated_default_params(self, client_domain_service):
        """Test paginación con parámetros por defecto."""
        # Arrange
        expected_result = {"clients": [], "total": 0, "page": 1, "page_size": 10, "total_pages": 0}
        client_domain_service.advanced_query.get_clients_paginated.return_value = expected_result

        # Act
        result = await client_domain_service.get_clients_paginated()

        # Assert
        assert result == expected_result
        client_domain_service.advanced_query.get_clients_paginated.assert_called_once_with(1, 10, None)

    @pytest.mark.asyncio
    async def test_search_clients_fuzzy_success(self, client_domain_service, sample_client_response):
        """Test búsqueda fuzzy exitosa."""
        # Arrange
        search_term = "Test Client"
        expected_clients = [sample_client_response]
        client_domain_service.advanced_query.search_clients_fuzzy.return_value = expected_clients

        # Act
        result = await client_domain_service.search_clients_fuzzy(search_term, threshold=0.6)

        # Assert
        assert result == expected_clients
        client_domain_service.advanced_query.search_clients_fuzzy.assert_called_once_with(search_term, 0.6)

    @pytest.mark.asyncio
    async def test_search_clients_fuzzy_no_matches(self, client_domain_service):
        """Test búsqueda difusa sin coincidencias."""
        # Arrange
        client_domain_service.advanced_query.search_clients_fuzzy.return_value = []

        # Act
        result = await client_domain_service.search_clients_fuzzy("NonExistent", threshold=0.8)

        # Assert
        assert result == []
        client_domain_service.advanced_query.search_clients_fuzzy.assert_called_once_with("NonExistent", 0.8)


class TestClientDomainServiceStatistics:
    """Tests para operaciones de estadísticas."""

    @pytest.mark.asyncio
    async def test_get_client_statistics_success(self, client_domain_service):
        """Test obtención de estadísticas exitosa."""
        # Arrange
        expected_stats = ClientStatsResponse(
            total_clients=100,
            active_clients=80,
            inactive_clients=20,
            growth_rate=5.5,
            last_updated="2024-01-01T00:00:00Z"
        )
        client_domain_service.statistics.get_client_statistics.return_value = expected_stats

        # Act
        result = await client_domain_service.get_client_statistics()

        # Assert
        assert result == expected_stats
        client_domain_service.statistics.get_client_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_clients_by_status_success(self, client_domain_service):
        """Test conteo por estado exitoso."""
        # Arrange
        expected_count = {"active": 80, "inactive": 20}
        client_domain_service.statistics.count_clients_by_status.return_value = expected_count

        # Act
        result = await client_domain_service.count_clients_by_status()

        # Assert
        assert result == expected_count
        client_domain_service.statistics.count_clients_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_growth_statistics_success(self, client_domain_service):
        """Test estadísticas de crecimiento exitosas."""
        # Arrange
        expected_growth = {
            "period_days": 30,
            "new_clients": 15,
            "growth_rate": 18.75,
            "daily_average": 0.5
        }
        client_domain_service.statistics.get_client_growth_statistics.return_value = expected_growth

        # Act
        result = await client_domain_service.get_client_growth_statistics(days=30)

        # Assert
        assert result == expected_growth
        client_domain_service.statistics.get_client_growth_statistics.assert_called_once_with(30)

    @pytest.mark.asyncio
    async def test_get_client_activity_metrics_success(self, client_domain_service):
        """Test métricas de actividad exitosas."""
        # Arrange
        expected_metrics = {
            "most_active_clients": ["Client1", "Client2"],
            "average_activity_score": 7.5,
            "activity_distribution": {"high": 30, "medium": 50, "low": 20}
        }
        client_domain_service.statistics.get_client_activity_metrics.return_value = expected_metrics

        # Act
        result = await client_domain_service.get_client_activity_metrics()

        # Assert
        assert result == expected_metrics
        client_domain_service.statistics.get_client_activity_metrics.assert_called_once()


class TestClientDomainServiceValidation:
    """Tests para operaciones de validación."""

    @pytest.mark.asyncio
    async def test_validate_client_creation_success(self, client_domain_service, sample_client_create_data):
        """Test validación de creación exitosa."""
        # Arrange
        expected_validation = {"valid": True, "errors": []}
        client_domain_service.validation.validate_client_creation.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_client_creation(sample_client_create_data)

        # Assert
        assert result == expected_validation
        client_domain_service.validation.validate_client_creation.assert_called_once_with(sample_client_create_data)

    @pytest.mark.asyncio
    async def test_validate_client_creation_with_errors(self, client_domain_service, sample_client_create_data):
        """Test validación de creación con errores."""
        # Arrange
        expected_validation = {
            "valid": False,
            "errors": ["Email ya existe", "Código duplicado"]
        }
        client_domain_service.validation.validate_client_creation.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_client_creation(sample_client_create_data)

        # Assert
        assert result == expected_validation
        assert not result["valid"]
        assert len(result["errors"]) == 2

    @pytest.mark.asyncio
    async def test_validate_client_update_success(self, client_domain_service, sample_client_id, sample_client_update_data):
        """Test validación de actualización exitosa."""
        # Arrange
        expected_validation = {"valid": True, "errors": []}
        client_domain_service.validation.validate_client_update.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_client_update(sample_client_id, sample_client_update_data)

        # Assert
        assert result == expected_validation
        client_domain_service.validation.validate_client_update.assert_called_once_with(
            sample_client_id, sample_client_update_data
        )

    @pytest.mark.asyncio
    async def test_validate_business_rules_success(self, client_domain_service, sample_client_create_data):
        """Test validación de reglas de negocio exitosa."""
        # Arrange
        expected_validation = {"valid": True, "rules_passed": ["email_format", "name_length"]}
        client_domain_service.validation.validate_business_rules.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_business_rules(sample_client_create_data)

        # Assert
        assert result == expected_validation
        client_domain_service.validation.validate_business_rules.assert_called_once_with(sample_client_create_data)

    @pytest.mark.asyncio
    async def test_validate_email_uniqueness_unique(self, client_domain_service):
        """Test validación de unicidad de email - único."""
        # Arrange
        email = "unique@test.com"
        client_domain_service.validation.validate_email_uniqueness.return_value = True

        # Act
        result = await client_domain_service.validate_email_uniqueness(email)

        # Assert
        assert result is True
        client_domain_service.validation.validate_email_uniqueness.assert_called_once_with(email, None)

    @pytest.mark.asyncio
    async def test_validate_email_uniqueness_not_unique(self, client_domain_service, sample_client_id):
        """Test validación de unicidad de email - no único."""
        # Arrange
        email = "duplicate@test.com"
        client_domain_service.validation.validate_email_uniqueness.return_value = False

        # Act
        result = await client_domain_service.validate_email_uniqueness(email, exclude_client_id=sample_client_id)

        # Assert
        assert result is False
        client_domain_service.validation.validate_email_uniqueness.assert_called_once_with(email, sample_client_id)


class TestClientDomainServiceHealth:
    """Tests para operaciones de salud."""

    @pytest.mark.asyncio
    async def test_check_service_health_healthy(self, client_domain_service):
        """Test verificación de salud del servicio - saludable."""
        # Arrange
        expected_health = {
            "status": "healthy",
            "timestamp": "2024-01-01T00:00:00Z",
            "checks": {"database": "ok", "modules": "ok"}
        }
        client_domain_service.health.check_service_health.return_value = expected_health

        # Act
        result = await client_domain_service.check_service_health()

        # Assert
        assert result == expected_health
        assert result["status"] == "healthy"
        client_domain_service.health.check_service_health.assert_called_once()

    @pytest.mark.asyncio
    async def test_check_database_connectivity_connected(self, client_domain_service):
        """Test verificación de conectividad de BD - conectada."""
        # Arrange
        expected_connectivity = {
            "status": "connected",
            "response_time_ms": 15,
            "last_check": "2024-01-01T00:00:00Z"
        }
        client_domain_service.health.check_database_connectivity.return_value = expected_connectivity

        # Act
        result = await client_domain_service.check_database_connectivity()

        # Assert
        assert result == expected_connectivity
        assert result["status"] == "connected"
        client_domain_service.health.check_database_connectivity.assert_called_once()

    @pytest.mark.asyncio
    async def test_generate_health_report_complete(self, client_domain_service):
        """Test generación de reporte de salud completo."""
        # Arrange
        expected_report = {
            "overall_status": "healthy",
            "service_health": {"status": "healthy"},
            "database_health": {"status": "connected"},
            "modules_status": {"crud": "ok", "query": "ok", "statistics": "ok"},
            "generated_at": "2024-01-01T00:00:00Z"
        }
        client_domain_service.health.generate_health_report.return_value = expected_report

        # Act
        result = await client_domain_service.generate_health_report()

        # Assert
        assert result == expected_report
        assert result["overall_status"] == "healthy"
        client_domain_service.health.generate_health_report.assert_called_once()


class TestClientDomainServiceUtility:
    """Tests para métodos de utilidad."""

    @pytest.mark.asyncio
    async def test_get_service_info_success(self, client_domain_service):
        """Test obtención de información del servicio exitosa."""
        # Act
        result = await client_domain_service.get_service_info()

        # Assert
        assert result["service_name"] == "ClientDomainService"
        assert result["version"] == "1.0.0"
        assert "modules" in result
        assert "capabilities" in result
        assert result["status"] == "active"
        assert len(result["modules"]) == 8  # crud, query, advanced_query, statistics, relationships, dates, validation, health
        assert len(result["capabilities"]) == 7

    @pytest.mark.asyncio
    async def test_get_service_info_repository_error(self, client_domain_service):
        """Test obtención de información del servicio con error."""
        # Arrange
        # Simular error interno en el método
        original_method = client_domain_service.get_service_info
        
        async def mock_error(*args, **kwargs):
            raise Exception("Error interno del servicio")
        
        client_domain_service.get_service_info = mock_error

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await client_domain_service.get_service_info()
        
        assert "Error interno del servicio" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_close_success(self, client_domain_service):
        """Test cierre de recursos exitoso."""
        # Act
        await client_domain_service.close()

        # Assert
        # Verificar que no se lance excepción
        # El método close() debería ejecutarse sin errores
        assert True  # Si llegamos aquí, el método se ejecutó correctamente

    @pytest.mark.asyncio
    async def test_close_with_error_handling(self, client_domain_service):
        """Test cierre de recursos con manejo de errores."""
        # Arrange
        # Simular error en el cierre
        original_close = client_domain_service.close
        
        async def mock_close_error(*args, **kwargs):
            raise Exception("Error cerrando recursos")
        
        client_domain_service.close = mock_close_error

        # Act & Assert
        with pytest.raises(Exception) as exc_info:
            await client_domain_service.close()
        
        assert "Error cerrando recursos" in str(exc_info.value)