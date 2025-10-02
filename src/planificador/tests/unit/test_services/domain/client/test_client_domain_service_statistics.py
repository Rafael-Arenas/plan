"""Tests unitarios para las operaciones de estadísticas del ClientDomainService.

Este módulo contiene tests para validar el comportamiento de las operaciones
de estadísticas del servicio de dominio de clientes, incluyendo casos de éxito,
manejo de errores y casos límite.
"""

from typing import Any, Dict
from unittest.mock import AsyncMock

import pytest

from planificador.exceptions.base import BusinessLogicError
from planificador.schemas.client.client import ClientStatsResponse
from planificador.services.domain.client.client_domain_service import ClientDomainService


class TestClientDomainServiceStatistics:
    """Tests para operaciones de estadísticas del ClientDomainService."""

    # ==================== TESTS PARA get_client_statistics ====================

    @pytest.mark.asyncio
    async def test_get_client_statistics_success(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test exitoso para obtener estadísticas generales de clientes.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos de estadísticas esperados
        expected_stats = ClientStatsResponse(
            total_clients=100,
            active_clients=80,
            inactive_clients=20
        )
        
        # Configurar mock para retornar estadísticas
        client_domain_service.statistics.get_client_statistics.return_value = expected_stats
        
        # Ejecutar método
        result = await client_domain_service.get_client_statistics()
        
        # Verificar resultado
        assert result == expected_stats
        assert result.total_clients == 100
        assert result.active_clients == 80
        assert result.inactive_clients == 20
        client_domain_service.statistics.get_client_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_statistics_empty_data(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para estadísticas con datos vacíos.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar estadísticas vacías
        empty_stats = ClientStatsResponse(
            total_clients=0,
            active_clients=0,
            inactive_clients=0
        )
        
        client_domain_service.statistics.get_client_statistics.return_value = empty_stats
        
        # Ejecutar método
        result = await client_domain_service.get_client_statistics()
        
        # Verificar estadísticas vacías
        assert result.total_clients == 0
        assert result.active_clients == 0
        assert result.inactive_clients == 0
        client_domain_service.statistics.get_client_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_statistics_service_error(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para manejar errores al obtener estadísticas de clientes.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar mock para lanzar excepción
        client_domain_service.statistics.get_client_statistics.side_effect = BusinessLogicError(
            "Error al obtener estadísticas"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(BusinessLogicError, match="Error al obtener estadísticas"):
            await client_domain_service.get_client_statistics()
        
        client_domain_service.statistics.get_client_statistics.assert_called_once()

    # ==================== TESTS PARA count_clients_by_status ====================

    @pytest.mark.asyncio
    async def test_count_clients_by_status_success(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test exitoso para contar clientes por estado.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos esperados
        expected_counts = {
            "active": 75,
            "inactive": 25,
            "pending": 10
        }
        
        # Configurar mock
        client_domain_service.statistics.count_clients_by_status.return_value = expected_counts
        
        # Ejecutar método
        result = await client_domain_service.count_clients_by_status()
        
        # Verificar resultado
        assert result == expected_counts
        assert result["active"] == 75
        assert result["inactive"] == 25
        assert result["pending"] == 10
        client_domain_service.statistics.count_clients_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_clients_by_status_empty_data(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para conteo con datos vacíos.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos vacíos
        empty_counts = {}
        
        client_domain_service.statistics.count_clients_by_status.return_value = empty_counts
        
        # Ejecutar método
        result = await client_domain_service.count_clients_by_status()
        
        # Verificar resultado vacío
        assert result == {}
        assert len(result) == 0
        client_domain_service.statistics.count_clients_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_clients_by_status_service_error(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para manejar errores al contar clientes por estado.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar mock para lanzar excepción
        client_domain_service.statistics.count_clients_by_status.side_effect = BusinessLogicError(
            "Error al contar clientes por estado"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(BusinessLogicError, match="Error al contar clientes por estado"):
            await client_domain_service.count_clients_by_status()
        
        client_domain_service.statistics.count_clients_by_status.assert_called_once()

    # ==================== TESTS PARA get_client_growth_statistics ====================

    @pytest.mark.asyncio
    async def test_get_client_growth_statistics_success(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test exitoso para obtener estadísticas de crecimiento.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos esperados
        expected_growth = {
            "period_days": 30,
            "new_clients": 15,
            "growth_rate": 12.5,
            "previous_period_clients": 120,
            "current_period_clients": 135
        }
        
        # Configurar mock
        client_domain_service.statistics.get_client_growth_statistics.return_value = expected_growth
        
        # Ejecutar método con parámetro por defecto
        result = await client_domain_service.get_client_growth_statistics()
        
        # Verificar resultado
        assert result == expected_growth
        assert result["period_days"] == 30
        assert result["new_clients"] == 15
        assert result["growth_rate"] == 12.5
        client_domain_service.statistics.get_client_growth_statistics.assert_called_once_with(30)

    @pytest.mark.asyncio
    async def test_get_client_growth_statistics_custom_period(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para estadísticas de crecimiento con período personalizado.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos esperados para 60 días
        expected_growth = {
            "period_days": 60,
            "new_clients": 25,
            "growth_rate": 18.2,
            "previous_period_clients": 137,
            "current_period_clients": 162
        }
        
        client_domain_service.statistics.get_client_growth_statistics.return_value = expected_growth
        
        # Ejecutar método con período personalizado
        result = await client_domain_service.get_client_growth_statistics(days=60)
        
        # Verificar resultado
        assert result == expected_growth
        assert result["period_days"] == 60
        client_domain_service.statistics.get_client_growth_statistics.assert_called_once_with(60)

    @pytest.mark.asyncio
    async def test_get_client_growth_statistics_service_error(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para manejar errores al obtener estadísticas de crecimiento.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar mock para lanzar excepción
        client_domain_service.statistics.get_client_growth_statistics.side_effect = BusinessLogicError(
            "Error al obtener estadísticas de crecimiento"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(BusinessLogicError, match="Error al obtener estadísticas de crecimiento"):
            await client_domain_service.get_client_growth_statistics(days=30)
        
        client_domain_service.statistics.get_client_growth_statistics.assert_called_once_with(30)

    # ==================== TESTS PARA get_client_activity_metrics ====================

    @pytest.mark.asyncio
    async def test_get_client_activity_metrics_success(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test exitoso para obtener métricas de actividad.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos esperados
        expected_metrics = {
            "total_interactions": 450,
            "active_clients_last_30_days": 85,
            "average_interactions_per_client": 5.3,
            "most_active_clients": [
                {"client_id": "123", "name": "Cliente A", "interactions": 25},
                {"client_id": "456", "name": "Cliente B", "interactions": 20}
            ]
        }
        
        # Configurar mock
        client_domain_service.statistics.get_client_activity_metrics.return_value = expected_metrics
        
        # Ejecutar método
        result = await client_domain_service.get_client_activity_metrics()
        
        # Verificar resultado
        assert result == expected_metrics
        assert result["total_interactions"] == 450
        assert result["active_clients_last_30_days"] == 85
        assert len(result["most_active_clients"]) == 2
        client_domain_service.statistics.get_client_activity_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_activity_metrics_empty_data(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para métricas de actividad con datos vacíos.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar datos vacíos
        empty_metrics = {
            "total_interactions": 0,
            "active_clients_last_30_days": 0,
            "average_interactions_per_client": 0.0,
            "most_active_clients": []
        }
        
        client_domain_service.statistics.get_client_activity_metrics.return_value = empty_metrics
        
        # Ejecutar método
        result = await client_domain_service.get_client_activity_metrics()
        
        # Verificar resultado vacío
        assert result["total_interactions"] == 0
        assert result["active_clients_last_30_days"] == 0
        assert len(result["most_active_clients"]) == 0
        client_domain_service.statistics.get_client_activity_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_client_activity_metrics_service_error(
        self,
        client_domain_service: ClientDomainService
    ) -> None:
        """
        Test para manejar errores al obtener métricas de actividad.
        
        Args:
            client_domain_service: Servicio de dominio de clientes mockeado
        """
        # Configurar mock para lanzar excepción
        client_domain_service.statistics.get_client_activity_metrics.side_effect = BusinessLogicError(
            "Error al obtener métricas de actividad"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(BusinessLogicError, match="Error al obtener métricas de actividad"):
            await client_domain_service.get_client_activity_metrics()
        
        client_domain_service.statistics.get_client_activity_metrics.assert_called_once()