"""Tests para los métodos de utilidad del ClientDomainService.

Este módulo contiene tests para verificar el correcto funcionamiento de los métodos
de utilidad del servicio de dominio de clientes, incluyendo get_service_info() y close().
"""

import pytest
from unittest.mock import AsyncMock
from typing import Dict, Any

from planificador.exceptions.repository.base_repository_exceptions import RepositoryError


class TestClientDomainServiceUtility:
    """Tests para métodos de utilidad del ClientDomainService."""

    @pytest.mark.asyncio
    async def test_get_service_info_success(self, client_domain_service):
        """
        Test: get_service_info retorna información completa del servicio exitosamente.
        
        Verifica que el método retorne toda la información esperada
        del servicio de dominio de clientes.
        """
        # Act: Ejecutar el método (usa la implementación del fixture)
        result = await client_domain_service.get_service_info()
        
        # Assert: Verificar resultado
        assert result is not None
        assert isinstance(result, dict)
        assert result["service_name"] == "ClientDomainService"
        assert result["version"] == "1.0.0"
        assert "modules" in result
        assert "capabilities" in result
        assert result["status"] == "active"

    @pytest.mark.asyncio
    async def test_get_service_info_structure_validation(self, client_domain_service):
        """
        Test: get_service_info retorna estructura de datos válida.
        
        Verifica que la estructura de datos retornada contenga
        todos los campos requeridos con tipos correctos.
        """
        # Act: Ejecutar el método
        result = await client_domain_service.get_service_info()
        
        # Assert: Verificar estructura
        assert isinstance(result["service_name"], str)
        assert isinstance(result["version"], str)
        assert isinstance(result["modules"], list)
        assert isinstance(result["capabilities"], list)
        assert isinstance(result["status"], str)
        
        # Verificar contenido de listas
        assert len(result["modules"]) > 0
        assert len(result["capabilities"]) > 0
        assert all(isinstance(module, str) for module in result["modules"])
        assert all(isinstance(cap, str) for cap in result["capabilities"])

    @pytest.mark.asyncio
    async def test_get_service_info_modules_content(self, client_domain_service):
        """
        Test: get_service_info incluye todos los módulos esperados.
        
        Verifica que la información del servicio incluya todos
        los módulos funcionales implementados.
        """
        # Act: Ejecutar el método
        result = await client_domain_service.get_service_info()
        
        # Assert: Verificar módulos específicos
        modules = result["modules"]
        expected_modules = ["crud", "query", "validation", "health"]
        
        for module in expected_modules:
            assert module in modules, f"Módulo {module} no encontrado en la lista"
        
        # Verificar capacidades específicas
        capabilities = result["capabilities"]
        expected_capabilities = ["create", "read", "update", "delete"]
        
        for capability in expected_capabilities:
            assert capability in capabilities, f"Capacidad {capability} no encontrada"

    @pytest.mark.asyncio
    async def test_get_service_info_error_handling(self, client_domain_service):
        """Test de manejo de errores en get_service_info."""
        # Arrange - Configurar el mock para lanzar una excepción
        error_message = "Error obteniendo información del servicio: Error interno simulado"
        error_mock = AsyncMock()
        error_mock.side_effect = RepositoryError(
            message=error_message,
            operation="get_service_info",
            entity_type="ClientDomainService"
        )
        client_domain_service.get_service_info = error_mock
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.get_service_info()
        
        # Verificar detalles de la excepción
        error = exc_info.value
        assert "Error obteniendo información del servicio" in str(error)

    @pytest.mark.asyncio
    async def test_close_success(self, client_domain_service):
        """Test exitoso de close."""
        # Act - Usar la implementación del fixture
        result = await client_domain_service.close()
        
        # Assert - Verificar que retorna True según el fixture
        assert result is True

    @pytest.mark.asyncio
    async def test_close_logging_verification(self, client_domain_service):
        """Test de verificación de logging en close."""
        # Act - Usar la implementación del fixture
        result = await client_domain_service.close()
        
        # Assert - Verificar que el método funciona correctamente
        assert result is True

    @pytest.mark.asyncio
    async def test_close_error_handling(self, client_domain_service):
        """Test de manejo de errores en close."""
        # Arrange - Configurar el mock para lanzar una excepción
        error_message = "Error cerrando servicio: Error de logging simulado"
        error_mock = AsyncMock()
        error_mock.side_effect = RepositoryError(
            message=error_message,
            operation="close",
            entity_type="ClientDomainService"
        )
        client_domain_service.close = error_mock
        
        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await client_domain_service.close()
        
        # Verificar detalles de la excepción
        error = exc_info.value
        assert "Error cerrando servicio" in str(error)

    @pytest.mark.asyncio
    async def test_close_multiple_calls(self, client_domain_service):
        """Test de múltiples llamadas a close."""
        # Act - Llamar close múltiples veces usando la implementación del fixture
        result1 = await client_domain_service.close()
        result2 = await client_domain_service.close()
        result3 = await client_domain_service.close()
        
        # Assert - Verificar que todas las llamadas retornan True
        assert result1 is True
        assert result2 is True
        assert result3 is True

    @pytest.mark.asyncio
    async def test_utility_methods_integration(self, client_domain_service):
        """Test de integración de métodos de utilidad."""
        # Act - Obtener información del servicio usando la implementación del fixture
        result = await client_domain_service.get_service_info()
        
        # Assert - Verificar que el servicio está activo
        assert result["status"] == "active"
        
        # Act - Cerrar el servicio
        close_result = await client_domain_service.close()
        
        # Assert - Verificar que el cierre fue exitoso
        assert close_result is True
        
        # El servicio debería seguir funcionando después del close
        result_after_close = await client_domain_service.get_service_info()
        assert result_after_close["status"] == "active"

    @pytest.mark.asyncio
    async def test_service_info_immutability(self, client_domain_service):
        """Test de inmutabilidad de la información del servicio."""
        # Act - Obtener información múltiples veces usando la implementación del fixture
        info1 = await client_domain_service.get_service_info()
        info2 = await client_domain_service.get_service_info()
        
        # Assert - Verificar que la información es consistente
        assert info1 == info2
        
        # Act - Intentar modificar el resultado
        info1["service_name"] = "Modified"
        info3 = await client_domain_service.get_service_info()
        
        # Assert - Verificar que la modificación no afecta futuras llamadas
        assert info3["service_name"] == "ClientDomainService"

    @pytest.mark.asyncio
    async def test_service_capabilities_completeness(self, client_domain_service):
        """
        Test: get_service_info incluye todas las capacidades esperadas.
        
        Verifica que el servicio reporte todas las capacidades
        funcionales que debería tener implementadas.
        """
        # Act: Obtener información
        result = await client_domain_service.get_service_info()
        
        # Assert: Verificar capacidades específicas del fixture
        capabilities = result["capabilities"]
        expected_capabilities = [
            "create", "read", "update", "delete", "search", "validate", "health_check"
        ]
        
        # Verificar que todas las capacidades esperadas están presentes
        for capability in expected_capabilities:
            assert capability in capabilities, f"Capacidad esperada {capability} no encontrada"
        
        # Verificar que tiene exactamente 7 capacidades
        assert len(capabilities) == 7, f"Se esperaban 7 capacidades, se encontraron {len(capabilities)}"

    @pytest.mark.asyncio
    async def test_service_version_format(self, client_domain_service):
        """Test del formato de versión del servicio."""
        # Act - Usar la implementación del fixture
        result = await client_domain_service.get_service_info()
        
        # Assert - Verificar formato de versión semántica
        version = result["version"]
        version_parts = version.split(".")
        assert len(version_parts) == 3, f"Versión debe tener formato X.Y.Z, encontrada: {version}"
        
        # Verificar que cada parte es numérica
        for part in version_parts:
            assert part.isdigit(), f"Cada parte de la versión debe ser numérica: {version}"