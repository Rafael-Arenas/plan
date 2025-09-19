"""Tests unitarios para StatusCodeRepositoryFacade."""

import pytest
from unittest.mock import AsyncMock, patch
from sqlalchemy.exc import SQLAlchemyError

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


class TestStatusCodeRepositoryFacadeCRUD:
    """Tests para operaciones CRUD del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_create_status_code_success(
        self, status_code_repository_facade, sample_status_code_data, sample_status_code
    ):
        """Test exitoso de creación de código de estado."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.create_status_code.return_value = sample_status_code

        # Act
        result = await facade.create_status_code(sample_status_code_data)

        # Assert
        assert result == sample_status_code
        facade._crud_module.create_status_code.assert_called_once_with(
            sample_status_code_data
        )

    @pytest.mark.asyncio
    async def test_create_status_code_validation_error(
        self, status_code_repository_facade, sample_status_code_data
    ):
        """Test de error de validación al crear código de estado."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.create_status_code.side_effect = ValidationError(
            message="Código ya existe",
            field="code",
            context={"operation": "create_status_code", "entity_type": "StatusCode"}
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.create_status_code(sample_status_code_data)
        
        assert "Código ya existe" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_create_status_code_repository_error(
        self, status_code_repository_facade, sample_status_code_data
    ):
        """Test de error de repositorio al crear código de estado."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.create_status_code.side_effect = RepositoryError(
            message="Error de base de datos",
            operation="create_status_code",
            entity_type="StatusCode"
        )

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await facade.create_status_code(sample_status_code_data)
        
        assert "Error de base de datos" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_by_id_success(
        self, status_code_repository_facade, sample_status_code
    ):
        """Test exitoso de obtención por ID."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 1
        facade._crud_module.get_status_code_by_id.return_value = sample_status_code

        # Act
        result = await facade.get_by_id(status_code_id)

        # Assert
        assert result == sample_status_code
        facade._crud_module.get_status_code_by_id.assert_called_once_with(
            status_code_id
        )

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, status_code_repository_facade):
        """Test de código de estado no encontrado por ID."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 999
        facade._crud_module.get_status_code_by_id.side_effect = NotFoundError(
            message="StatusCode no encontrado",
            resource_type="StatusCode",
            resource_id=status_code_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await facade.get_by_id(status_code_id)
        
        assert "StatusCode no encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_all_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de obtención de todos los códigos de estado."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.get_all_status_codes.return_value = sample_status_codes_list

        # Act
        result = await facade.get_all()

        # Assert
        assert result == sample_status_codes_list
        assert len(result) == 3
        facade._crud_module.get_all_status_codes.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_all_empty_list(self, status_code_repository_facade):
        """Test de obtención de lista vacía."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.get_all_status_codes.return_value = []

        # Act
        result = await facade.get_all()

        # Assert
        assert result == []
        facade._crud_module.get_all_status_codes.assert_called_once()

    @pytest.mark.asyncio
    async def test_update_status_code_success(
        self, status_code_repository_facade, sample_status_code, sample_update_data
    ):
        """Test exitoso de actualización de código de estado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 1
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

        # Act
        result = await facade.update_status_code(status_code_id, sample_update_data)

        # Assert
        assert result == updated_status_code
        facade._crud_module.update_status_code.assert_called_once_with(
            status_code_id, sample_update_data
        )

    @pytest.mark.asyncio
    async def test_update_status_code_not_found(
        self, status_code_repository_facade, sample_update_data
    ):
        """Test de actualización de código de estado no encontrado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 999
        facade._crud_module.update_status_code.side_effect = NotFoundError(
            message="StatusCode no encontrado",
            resource_type="StatusCode",
            resource_id=status_code_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await facade.update_status_code(status_code_id, sample_update_data)
        
        assert "StatusCode no encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_update_status_code_validation_error(
        self, status_code_repository_facade, sample_update_data
    ):
        """Test de error de validación al actualizar código de estado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 1
        facade._crud_module.update_status_code.side_effect = ValidationError(
            message="Datos inválidos",
            field="data",
            context={"operation": "update_status_code", "entity_type": "StatusCode"}
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.update_status_code(status_code_id, sample_update_data)
        
        assert "Datos inválidos" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_status_code_success(self, status_code_repository_facade):
        """Test exitoso de eliminación de código de estado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 1
        facade._crud_module.delete_status_code.return_value = True

        # Act
        result = await facade.delete_status_code(status_code_id)

        # Assert
        assert result is True
        facade._crud_module.delete_status_code.assert_called_once_with(status_code_id)

    @pytest.mark.asyncio
    async def test_delete_status_code_not_found(self, status_code_repository_facade):
        """Test de eliminación de código de estado no encontrado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 999
        facade._crud_module.delete_status_code.side_effect = NotFoundError(
            message="StatusCode no encontrado",
            resource_type="StatusCode",
            resource_id=status_code_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await facade.delete_status_code(status_code_id)
        
        assert "StatusCode no encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_delete_status_code_constraint_error(self, status_code_repository_facade):
        """Test de error de restricción al eliminar código de estado."""
        # Arrange
        facade = status_code_repository_facade
        status_code_id = 1
        facade._crud_module.delete_status_code.side_effect = RepositoryError(
            message="No se puede eliminar: tiene referencias",
            operation="delete_status_code",
            entity_type="StatusCode",
            entity_id=status_code_id
        )

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await facade.delete_status_code(status_code_id)
        
        assert "tiene referencias" in str(exc_info.value)


class TestStatusCodeRepositoryFacadeQueries:
    """Tests para operaciones de consulta del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_find_by_code_success(
        self, status_code_repository_facade, sample_status_code
    ):
        """Test exitoso de búsqueda por código."""
        # Arrange
        facade = status_code_repository_facade
        code = "WORK"
        facade._query_module.find_by_code.return_value = sample_status_code

        # Act
        result = await facade.find_by_code(code)

        # Assert
        assert result == sample_status_code
        facade._query_module.find_by_code.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_find_by_code_not_found(self, status_code_repository_facade):
        """Test de búsqueda por código no encontrado."""
        # Arrange
        facade = status_code_repository_facade
        code = "NONEXISTENT"
        facade._query_module.find_by_code.return_value = None

        # Act
        result = await facade.find_by_code(code)

        # Assert
        assert result is None
        facade._query_module.find_by_code.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_find_by_name_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de búsqueda por nombre."""
        # Arrange
        facade = status_code_repository_facade
        name = "Trabajo"
        facade._query_module.find_by_name.return_value = [sample_status_codes_list[0]]

        # Act
        result = await facade.find_by_name(name)

        # Assert
        assert len(result) == 1
        assert result[0].name == "Trabajo"
        facade._query_module.find_by_name.assert_called_once_with(name)

    @pytest.mark.asyncio
    async def test_find_by_text_search_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de búsqueda por texto."""
        # Arrange
        facade = status_code_repository_facade
        search_text = "trabajo"
        facade._query_module.find_by_text_search.return_value = sample_status_codes_list

        # Act
        result = await facade.find_by_text_search(search_text)

        # Assert
        assert result == sample_status_codes_list
        facade._query_module.find_by_text_search.assert_called_once_with(search_text)

    @pytest.mark.asyncio
    async def test_find_active_status_codes_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de búsqueda de códigos activos."""
        # Arrange
        facade = status_code_repository_facade
        active_codes = [code for code in sample_status_codes_list if code.is_active]
        facade._query_module.find_active_status_codes.return_value = active_codes

        # Act
        result = await facade.find_active_status_codes()

        # Assert
        assert result == active_codes
        assert all(code.is_active for code in result)
        facade._query_module.find_active_status_codes.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_inactive_status_codes_success(
        self, status_code_repository_facade
    ):
        """Test exitoso de búsqueda de códigos inactivos."""
        # Arrange
        facade = status_code_repository_facade
        inactive_codes = []
        facade._query_module.find_inactive_status_codes.return_value = inactive_codes

        # Act
        result = await facade.find_inactive_status_codes()

        # Assert
        assert result == inactive_codes
        facade._query_module.find_inactive_status_codes.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_codes_paginated_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de paginación de códigos de estado."""
        # Arrange
        facade = status_code_repository_facade
        page = 1
        page_size = 10
        paginated_result = {
            "items": sample_status_codes_list,
            "total": 3,
            "page": page,
            "page_size": page_size,
            "total_pages": 1
        }
        facade._query_module.get_status_codes_paginated.return_value = paginated_result

        # Act
        result = await facade.get_status_codes_paginated(page, page_size)

        # Assert
        assert result == paginated_result
        assert result["total"] == 3
        assert len(result["items"]) == 3
        facade._query_module.get_status_codes_paginated.assert_called_once_with(
            page, page_size
        )

    @pytest.mark.asyncio
    async def test_find_with_advanced_filters_success(
        self, status_code_repository_facade, sample_status_codes_list, sample_advanced_filters
    ):
        """Test exitoso de búsqueda con filtros avanzados."""
        # Arrange
        facade = status_code_repository_facade
        filtered_codes = [sample_status_codes_list[0], sample_status_codes_list[1]]
        facade._query_module.find_with_advanced_filters.return_value = filtered_codes

        # Act
        result = await facade.find_with_advanced_filters(sample_advanced_filters)

        # Assert
        assert result == filtered_codes
        assert len(result) == 2
        facade._query_module.find_with_advanced_filters.assert_called_once_with(
            sample_advanced_filters
        )

    @pytest.mark.asyncio
    async def test_get_ordered_status_codes_success(
        self, status_code_repository_facade, sample_status_codes_list
    ):
        """Test exitoso de obtención de códigos ordenados."""
        # Arrange
        facade = status_code_repository_facade
        order_by = "sort_order"
        ascending = True
        facade._query_module.get_ordered_status_codes.return_value = sample_status_codes_list

        # Act
        result = await facade.get_ordered_status_codes(order_by, ascending)

        # Assert
        assert result == sample_status_codes_list
        facade._query_module.get_ordered_status_codes.assert_called_once_with(
            order_by, ascending
        )


class TestStatusCodeRepositoryFacadeValidation:
    """Tests para operaciones de validación del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_validate_unique_code_success(self, status_code_repository_facade):
        """Test exitoso de validación de código único."""
        # Arrange
        facade = status_code_repository_facade
        code = "NEWCODE"
        facade._validation_module.validate_unique_code.return_value = True

        # Act
        result = await facade.validate_unique_code(code)

        # Assert
        assert result is True
        facade._validation_module.validate_unique_code.assert_called_once_with(code)

    @pytest.mark.asyncio
    async def test_validate_unique_code_duplicate(self, status_code_repository_facade):
        """Test de validación de código duplicado."""
        # Arrange
        facade = status_code_repository_facade
        code = "WORK"
        facade._validation_module.validate_unique_code.side_effect = ValidationError(
            message="El código ya existe",
            field="code",
            value=code,
            context={"operation": "validate_unique_code", "entity_type": "StatusCode"}
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.validate_unique_code(code)
        
        assert "El código ya existe" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_validate_status_code_data_success(
        self, status_code_repository_facade, sample_status_code_data
    ):
        """Test exitoso de validación de datos."""
        # Arrange
        facade = status_code_repository_facade
        facade._validation_module.validate_status_code_data.return_value = True

        # Act
        result = await facade.validate_status_code_data(sample_status_code_data)

        # Assert
        assert result is True
        facade._validation_module.validate_status_code_data.assert_called_once_with(
            sample_status_code_data
        )

    @pytest.mark.asyncio
    async def test_validate_status_code_data_invalid(
        self, status_code_repository_facade, sample_validation_errors
    ):
        """Test de validación de datos inválidos."""
        # Arrange
        facade = status_code_repository_facade
        invalid_data = {"code": "", "name": ""}
        facade._validation_module.validate_status_code_data.side_effect = ValidationError(
            message="Datos inválidos",
            field="data",
            context={"operation": "validate_status_code_data", "entity_type": "StatusCode"}
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await facade.validate_status_code_data(invalid_data)
        
        assert "Datos inválidos" in str(exc_info.value)


class TestStatusCodeRepositoryFacadeStatistics:
    """Tests para operaciones de estadísticas del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_get_status_code_statistics_success(
        self, status_code_repository_facade, sample_statistics
    ):
        """Test exitoso de obtención de estadísticas."""
        # Arrange
        facade = status_code_repository_facade
        facade._statistics_module.get_status_code_statistics.return_value = sample_statistics

        # Act
        result = await facade.get_status_code_statistics()

        # Assert
        assert result == sample_statistics
        assert result["total_count"] == 10
        assert result["active_count"] == 8
        facade._statistics_module.get_status_code_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_distribution_analysis_success(
        self, status_code_repository_facade
    ):
        """Test exitoso de análisis de distribución."""
        # Arrange
        facade = status_code_repository_facade
        distribution_data = {
            "billable_productive": 5,
            "billable_non_productive": 1,
            "non_billable_productive": 2,
            "non_billable_non_productive": 2
        }
        facade._statistics_module.get_status_distribution_analysis.return_value = distribution_data

        # Act
        result = await facade.get_status_distribution_analysis()

        # Assert
        assert result == distribution_data
        facade._statistics_module.get_status_distribution_analysis.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_status_code_health_check_success(
        self, status_code_repository_facade, sample_health_check_result
    ):
        """Test exitoso de health check."""
        # Arrange
        facade = status_code_repository_facade
        facade._statistics_module.get_status_code_health_check.return_value = sample_health_check_result

        # Act
        result = await facade.get_status_code_health_check()

        # Assert
        assert result == sample_health_check_result
        assert result["facade"] == "healthy"
        assert result["session"] == "connected"
        facade._statistics_module.get_status_code_health_check.assert_called_once()


class TestStatusCodeRepositoryFacadeErrorHandling:
    """Tests para manejo de errores del repositorio de códigos de estado."""

    @pytest.mark.asyncio
    async def test_sqlalchemy_error_handling(self, status_code_repository_facade):
        """Test de manejo de errores de SQLAlchemy."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.get_status_code_by_id.side_effect = SQLAlchemyError("Database error")

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await facade.get_by_id(1)
        
        assert "Database error" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_unexpected_error_handling(self, status_code_repository_facade):
        """Test de manejo de errores inesperados."""
        # Arrange
        facade = status_code_repository_facade
        facade._crud_module.get_all_status_codes.side_effect = Exception("Unexpected error")

        # Act & Assert
        with pytest.raises(RepositoryError) as exc_info:
            await facade.get_all()
        
        assert "Unexpected error" in str(exc_info.value)