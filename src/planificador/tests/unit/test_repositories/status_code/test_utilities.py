"""Tests adicionales para métodos de utilidad y casos edge del StatusCodeRepositoryFacade."""

import pytest
from unittest.mock import AsyncMock, patch
from typing import Dict, Any, List

from planificador.exceptions.base import (
    ValidationError,
    NotFoundError,
)
from planificador.exceptions.repository import (
    RepositoryError,
    RepositoryValidationError,
    StatusCodeRepositoryError,
    StatusCodeNotFoundError,
    StatusCodeValidationError,
    StatusCodeStatisticsError,
)
from planificador.models.status_code import StatusCode


class TestStatusCodeRepositoryFacadeUtilities:
    """Tests para métodos de utilidad del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_health_check_all_healthy(
        self, status_code_repository_facade, sample_health_check_result
    ):
        """Test de health check con todos los componentes saludables."""
        # Arrange
        facade = status_code_repository_facade
        facade._statistics_module.get_status_code_health_check.return_value = sample_health_check_result

        # Act
        result = await facade.get_status_code_health_check()

        # Assert
        assert result["facade"] == "healthy"
        assert result["session"] == "connected"
        assert all(
            status == "healthy" 
            for status in result["modules"].values()
        )

    @pytest.mark.asyncio
    async def test_health_check_with_issues(self, status_code_repository_facade):
        """Test de health check con problemas en algunos módulos."""
        # Arrange
        facade = status_code_repository_facade
        unhealthy_result = {
            "facade": "degraded",
            "session": "connected",
            "modules": {
                "crud": "healthy",
                "query": "error",
                "validation": "healthy",
                "statistics": "warning"
            }
        }
        facade._statistics_module.get_status_code_health_check.return_value = unhealthy_result

        # Act
        result = await facade.get_status_code_health_check()

        # Assert
        assert result["facade"] == "degraded"
        assert result["modules"]["query"] == "error"
        assert result["modules"]["statistics"] == "warning"

    @pytest.mark.asyncio
    async def test_get_display_order_metrics_success(self, status_code_repository_facade):
        """Test exitoso de métricas de orden de visualización."""
        # Arrange
        facade = status_code_repository_facade
        metrics_data = {
            "min_order": 1,
            "max_order": 10,
            "gaps": [4, 7],
            "duplicates": [],
            "total_items": 8
        }
        facade._statistics_module.get_display_order_metrics.return_value = metrics_data

        # Act
        result = await facade.get_display_order_metrics()

        # Assert
        assert result == metrics_data
        assert result["min_order"] == 1
        assert result["max_order"] == 10
        assert len(result["gaps"]) == 2
        facade._statistics_module.get_display_order_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_usage_performance_metrics_success(self, status_code_repository_facade):
        """Test exitoso de métricas de rendimiento de uso."""
        # Arrange
        facade = status_code_repository_facade
        performance_data = {
            "most_used_codes": ["WORK", "MEET", "BREAK"],
            "least_used_codes": ["ADMIN", "TRAIN"],
            "usage_frequency": {
                "WORK": 150,
                "MEET": 89,
                "BREAK": 45
            },
            "performance_score": 85.5
        }
        facade._statistics_module.get_usage_performance_metrics.return_value = performance_data

        # Act
        result = await facade.get_usage_performance_metrics()

        # Assert
        assert result == performance_data
        assert result["performance_score"] == 85.5
        assert "WORK" in result["most_used_codes"]
        facade._statistics_module.get_usage_performance_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_data_integrity_report_success(self, status_code_repository_facade):
        """Test exitoso de reporte de integridad de datos."""
        # Arrange
        facade = status_code_repository_facade
        integrity_data = {
            "total_records": 10,
            "valid_records": 9,
            "invalid_records": 1,
            "integrity_score": 90.0,
            "issues": [
                {
                    "type": "missing_color",
                    "count": 1,
                    "severity": "warning"
                }
            ]
        }
        facade._statistics_module.get_data_integrity_report.return_value = integrity_data

        # Act
        result = await facade.get_data_integrity_report()

        # Assert
        assert result == integrity_data
        assert result["integrity_score"] == 90.0
        assert len(result["issues"]) == 1
        facade._statistics_module.get_data_integrity_report.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_display_order_conflicts_success(self, status_code_repository_facade):
        """Test exitoso de validación de conflictos de orden."""
        # Arrange
        facade = status_code_repository_facade
        sort_order = 5
        facade._validation_module.validate_display_order_conflicts.return_value = True

        # Act
        result = await facade.validate_display_order_conflicts(sort_order)

        # Assert
        assert result is True
        facade._validation_module.validate_display_order_conflicts.assert_called_once_with(
            sort_order
        )

    @pytest.mark.asyncio
    async def test_validate_display_order_conflicts_duplicate(self, status_code_repository_facade):
        """Test de validación de orden duplicado."""
        # Arrange
        facade = status_code_repository_facade
        sort_order = 1
        facade._validation_module.validate_display_order_conflicts.side_effect = ValidationError(
            message="El orden de visualización ya existe",
            field="display_order",
            value=sort_order
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.validate_display_order_conflicts(sort_order)
        
        assert "orden de visualización ya existe" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_default_status_rules_success(self, status_code_repository_facade):
        """Test exitoso de validación de reglas de estado por defecto."""
        # Arrange
        facade = status_code_repository_facade
        status_data = {
            "code": "DEFAULT",
            "is_active": True,
            "is_billable": True,
            "is_productive": True
        }
        facade._validation_module.validate_default_status_rules.return_value = True

        # Act
        result = await facade.validate_default_status_rules(status_data)

        # Assert
        assert result is True
        facade._validation_module.validate_default_status_rules.assert_called_once_with(
            status_data
        )

    @pytest.mark.asyncio
    async def test_validate_default_status_rules_violation(self, status_code_repository_facade):
        """Test de violación de reglas de estado por defecto."""
        # Arrange
        facade = status_code_repository_facade
        invalid_status_data = {
            "code": "INVALID",
            "is_active": False,
            "is_billable": False,
            "is_productive": False
        }
        facade._validation_module.validate_default_status_rules.side_effect = ValidationError(
            message="Estado por defecto debe ser activo y productivo",
            field="is_active",
            value=False
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.validate_default_status_rules(invalid_status_data)
        
        assert "debe ser activo y productivo" in str(exc_info.value)


class TestStatusCodeRepositoryFacadeEdgeCases:
    """Tests para casos edge y situaciones límite."""

    @pytest.mark.asyncio
    async def test_find_by_display_order_range_success(self, status_code_repository_facade):
        """Test exitoso de búsqueda por rango de orden."""
        # Arrange
        facade = status_code_repository_facade
        min_order = 1
        max_order = 5
        expected_codes = [
            StatusCode(id=1, code="WORK", name="Trabajo", sort_order=1),
            StatusCode(id=2, code="MEET", name="Reunión", sort_order=3),
        ]
        facade._query_module.find_by_display_order_range.return_value = expected_codes

        # Act
        result = await facade.find_by_display_order_range(min_order, max_order)

        # Assert
        assert result == expected_codes
        assert len(result) == 2
        facade._query_module.find_by_display_order_range.assert_called_once_with(
            min_order, max_order
        )

    @pytest.mark.asyncio
    async def test_find_by_display_order_range_empty(self, status_code_repository_facade):
        """Test de búsqueda por rango sin resultados."""
        # Arrange
        facade = status_code_repository_facade
        min_order = 100
        max_order = 200
        facade._query_module.find_by_display_order_range.return_value = []

        # Act
        result = await facade.find_by_display_order_range(min_order, max_order)

        # Assert
        assert result == []
        facade._query_module.find_by_display_order_range.assert_called_once_with(
            min_order, max_order
        )

    @pytest.mark.asyncio
    async def test_find_default_status_codes_success(self, status_code_repository_facade):
        """Test exitoso de búsqueda de códigos por defecto."""
        # Arrange
        facade = status_code_repository_facade
        default_codes = [
            StatusCode(id=1, code="WORK", name="Trabajo", is_active=True),
            StatusCode(id=2, code="BREAK", name="Descanso", is_active=True),
        ]
        facade._query_module.find_default_status_codes.return_value = default_codes

        # Act
        result = await facade.find_default_status_codes()

        # Assert
        assert result == default_codes
        assert len(result) == 2
        facade._query_module.find_default_status_codes.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_unique_name_success(self, status_code_repository_facade):
        """Test exitoso de validación de nombre único."""
        # Arrange
        facade = status_code_repository_facade
        name = "Nuevo Estado"
        facade._validation_module.validate_unique_name.return_value = True

        # Act
        result = await facade.validate_unique_name(name)

        # Assert
        assert result is True
        facade._validation_module.validate_unique_name.assert_called_once_with(name)

    @pytest.mark.asyncio
    async def test_validate_unique_name_duplicate(self, status_code_repository_facade):
        """Test de validación de nombre duplicado."""
        # Arrange
        facade = status_code_repository_facade
        name = "Trabajo"
        facade._validation_module.validate_unique_name.side_effect = ValidationError(
            message="El nombre ya existe",
            field="name",
            value=name
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.validate_unique_name(name)
        
        assert "El nombre ya existe" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_pagination_edge_cases(self, status_code_repository_facade):
        """Test de casos edge en paginación."""
        # Arrange
        facade = status_code_repository_facade
        
        # Caso: página 0
        page_zero_result = {
            "items": [],
            "total": 0,
            "page": 0,
            "page_size": 10,
            "total_pages": 0
        }
        facade._query_module.get_status_codes_paginated.return_value = page_zero_result

        # Act
        result = await facade.get_status_codes_paginated(0, 10)

        # Assert
        assert result["page"] == 0
        assert result["total"] == 0
        assert len(result["items"]) == 0

    @pytest.mark.asyncio
    async def test_large_page_size_handling(self, status_code_repository_facade):
        """Test de manejo de tamaño de página grande."""
        # Arrange
        facade = status_code_repository_facade
        large_page_result = {
            "items": [],
            "total": 5,
            "page": 1,
            "page_size": 1000,
            "total_pages": 1
        }
        facade._query_module.get_status_codes_paginated.return_value = large_page_result

        # Act
        result = await facade.get_status_codes_paginated(1, 1000)

        # Assert
        assert result["page_size"] == 1000
        assert result["total_pages"] == 1

    @pytest.mark.asyncio
    async def test_empty_search_text_handling(self, status_code_repository_facade):
        """Test de manejo de texto de búsqueda vacío."""
        # Arrange
        facade = status_code_repository_facade
        facade._query_module.find_by_text_search.return_value = []

        # Act
        result = await facade.find_by_text_search("")

        # Assert
        assert result == []
        facade._query_module.find_by_text_search.assert_called_once_with("")

    @pytest.mark.asyncio
    async def test_null_filters_handling(self, status_code_repository_facade):
        """Test de manejo de filtros nulos."""
        # Arrange
        facade = status_code_repository_facade
        null_filters = {}
        facade._query_module.find_with_advanced_filters.return_value = []

        # Act
        result = await facade.find_with_advanced_filters(null_filters)

        # Assert
        assert result == []
        facade._query_module.find_with_advanced_filters.assert_called_once_with(
            null_filters
        )


class TestStatusCodeRepositoryFacadeIntegration:
    """Tests de integración y flujos completos."""

    @pytest.mark.asyncio
    async def test_complete_crud_workflow(
        self, 
        status_code_repository_facade, 
        sample_status_code_data,
        sample_status_code,
        sample_update_data
    ):
        """Test de flujo completo CRUD."""
        facade = status_code_repository_facade
        
        # Create
        facade._crud_module.create_status_code.return_value = sample_status_code
        created = await facade.create_status_code(sample_status_code_data)
        assert created == sample_status_code
        
        # Read
        facade._crud_module.get_status_code_by_id.return_value = sample_status_code
        retrieved = await facade.get_by_id(1)
        assert retrieved == sample_status_code
        
        # Update
        updated_status_code = StatusCode(
            id=sample_status_code.id,
            code=sample_update_data.get('code', sample_status_code.code),
            name=sample_update_data.get('name', sample_status_code.name),
            description=sample_update_data.get('description', sample_status_code.description),
            color=sample_update_data.get('color', sample_status_code.color),
            icon=sample_update_data.get('icon', sample_status_code.icon),
            is_billable=sample_update_data.get('is_billable', sample_status_code.is_billable),
            is_productive=sample_update_data.get('is_productive', sample_status_code.is_productive),
            requires_approval=sample_update_data.get('requires_approval', sample_status_code.requires_approval),
            is_active=sample_update_data.get('is_active', sample_status_code.is_active),
            sort_order=sample_update_data.get('sort_order', sample_status_code.sort_order)
        )
        facade._crud_module.update_status_code.return_value = updated_status_code
        updated = await facade.update_status_code(1, sample_update_data)
        assert updated == updated_status_code
        
        # Delete
        facade._crud_module.delete_status_code.return_value = True
        deleted = await facade.delete_status_code(1)
        assert deleted is True

    @pytest.mark.asyncio
    async def test_validation_before_creation_workflow(
        self, 
        status_code_repository_facade, 
        sample_status_code_data,
        sample_status_code
    ):
        """Test de flujo de validación antes de creación."""
        facade = status_code_repository_facade
        
        # Validar código único
        facade._validation_module.validate_unique_code.return_value = True
        code_valid = await facade.validate_unique_code(sample_status_code_data["code"])
        assert code_valid is True
        
        # Validar datos
        facade._validation_module.validate_status_code_data.return_value = True
        data_valid = await facade.validate_status_code_data(sample_status_code_data)
        assert data_valid is True
        
        # Crear después de validación
        facade._crud_module.create_status_code.return_value = sample_status_code
        created = await facade.create_status_code(sample_status_code_data)
        assert created == sample_status_code

    @pytest.mark.asyncio
    async def test_search_and_filter_workflow(
        self, 
        status_code_repository_facade, 
        sample_status_codes_list,
        sample_advanced_filters
    ):
        """Test de flujo de búsqueda y filtrado."""
        facade = status_code_repository_facade
        
        # Búsqueda por texto
        facade._query_module.find_by_text_search.return_value = sample_status_codes_list
        text_results = await facade.find_by_text_search("trabajo")
        assert len(text_results) == 3
        
        # Filtros avanzados
        filtered_results = [sample_status_codes_list[0], sample_status_codes_list[1]]
        facade._query_module.find_with_advanced_filters.return_value = filtered_results
        advanced_results = await facade.find_with_advanced_filters(sample_advanced_filters)
        assert len(advanced_results) == 2
        
        # Paginación de resultados
        paginated_result = {
            "items": filtered_results,
            "total": 2,
            "page": 1,
            "page_size": 10,
            "total_pages": 1
        }
        facade._query_module.get_status_codes_paginated.return_value = paginated_result
        paginated = await facade.get_status_codes_paginated(1, 10)
        assert paginated["total"] == 2