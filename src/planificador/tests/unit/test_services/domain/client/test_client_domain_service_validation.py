# src/planificador/tests/services/domain/client/test_client_domain_service_validation.py

"""Tests para las operaciones de validación del ClientDomainService.

Este módulo contiene tests unitarios para validar las operaciones de validación
del servicio de dominio de clientes, incluyendo validación de creación,
actualización, reglas de negocio y unicidad de email."""

import pytest
from uuid import uuid4
from unittest.mock import AsyncMock

from planificador.services.domain.client.client_domain_service import ClientDomainService
from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.exceptions.base import BusinessLogicError


class TestClientDomainServiceValidation:
    """Tests para las operaciones de validación del ClientDomainService."""

    @pytest.fixture
    def sample_client_create(self) -> ClientCreate:
        """Fixture para datos de creación de cliente válidos."""
        return ClientCreate(
            name="Cliente Test",
            code="TEST001",
            email="test@example.com",
            is_active=True,
            notes="Cliente de prueba"
        )

    @pytest.fixture
    def sample_client_update(self) -> ClientUpdate:
        """Fixture para datos de actualización de cliente válidos."""
        return ClientUpdate(
            name="Cliente Actualizado",
            email="updated@example.com",
            is_active=False,
            notes="Cliente actualizado"
        )

    # ==================== TESTS PARA validate_client_creation ====================

    async def test_validate_client_creation_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test exitoso de validación de creación de cliente."""
        # Arrange
        expected_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "field_validations": {
                "name": {"is_valid": True, "errors": []},
                "email": {"is_valid": True, "errors": []},
                "code": {"is_valid": True, "errors": []}
            }
        }
        
        client_domain_service.validation.validate_client_creation.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_client_creation(sample_client_create)

        # Assert
        assert result == expected_validation
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        client_domain_service.validation.validate_client_creation.assert_called_once_with(
            sample_client_create
        )

    async def test_validate_client_creation_validation_errors(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test de validación de creación con errores de validación."""
        # Arrange
        validation_with_errors = {
            "is_valid": False,
            "errors": [
                "El email 'test@example.com' ya está en uso",
                "El código 'TEST001' ya existe"
            ],
            "warnings": [],
            "field_validations": {
                "name": {"is_valid": True, "errors": []},
                "email": {"is_valid": False, "errors": ["Email ya en uso"]},
                "code": {"is_valid": False, "errors": ["Código ya existe"]}
            }
        }
        
        client_domain_service.validation.validate_client_creation.return_value = validation_with_errors

        # Act
        result = await client_domain_service.validate_client_creation(sample_client_create)

        # Assert
        assert result == validation_with_errors
        assert result["is_valid"] is False
        assert len(result["errors"]) == 2
        assert "El email 'test@example.com' ya está en uso" in result["errors"]
        assert "El código 'TEST001' ya existe" in result["errors"]

    async def test_validate_client_creation_service_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test de validación de creación con error de servicio."""
        # Arrange
        client_domain_service.validation.validate_client_creation.side_effect = BusinessLogicError(
            message="Error en validación de creación"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.validate_client_creation(sample_client_create)
        
        assert "Error en validación de creación" in str(exc_info.value)
        client_domain_service.validation.validate_client_creation.assert_called_once_with(
            sample_client_create
        )

    # ==================== TESTS PARA validate_client_update ====================

    async def test_validate_client_update_success(
        self,
        client_domain_service: ClientDomainService,
        sample_client_update: ClientUpdate
    ):
        """Test exitoso de validación de actualización de cliente."""
        # Arrange
        client_id = uuid4()
        expected_validation = {
            "is_valid": True,
            "errors": [],
            "warnings": [],
            "changes_detected": ["name", "email", "is_active"],
            "field_validations": {
                "name": {"is_valid": True, "errors": []},
                "email": {"is_valid": True, "errors": []}
            }
        }
        
        client_domain_service.validation.validate_client_update.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_client_update(client_id, sample_client_update)

        # Assert
        assert result == expected_validation
        assert result["is_valid"] is True
        assert len(result["errors"]) == 0
        assert "name" in result["changes_detected"]
        assert "email" in result["changes_detected"]
        client_domain_service.validation.validate_client_update.assert_called_once_with(
            client_id, sample_client_update
        )

    async def test_validate_client_update_validation_errors(
        self,
        client_domain_service: ClientDomainService,
        sample_client_update: ClientUpdate
    ):
        """Test de validación de actualización con errores de validación."""
        # Arrange
        client_id = uuid4()
        validation_with_errors = {
            "is_valid": False,
            "errors": [
                "El email 'updated@example.com' ya está en uso por otro cliente",
                "Cliente no encontrado"
            ],
            "warnings": [],
            "changes_detected": ["email"],
            "field_validations": {
                "email": {"is_valid": False, "errors": ["Email ya en uso"]}
            }
        }
        
        client_domain_service.validation.validate_client_update.return_value = validation_with_errors

        # Act
        result = await client_domain_service.validate_client_update(client_id, sample_client_update)

        # Assert
        assert result == validation_with_errors
        assert result["is_valid"] is False
        assert len(result["errors"]) == 2
        assert "El email 'updated@example.com' ya está en uso por otro cliente" in result["errors"]

    async def test_validate_client_update_service_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_update: ClientUpdate
    ):
        """Test de validación de actualización con error de servicio."""
        # Arrange
        client_id = uuid4()
        client_domain_service.validation.validate_client_update.side_effect = BusinessLogicError(
            message="Error en validación de actualización"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.validate_client_update(client_id, sample_client_update)
        
        assert "Error en validación de actualización" in str(exc_info.value)
        client_domain_service.validation.validate_client_update.assert_called_once_with(
            client_id, sample_client_update
        )

    # ==================== TESTS PARA validate_business_rules ====================

    async def test_validate_business_rules_success_create(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test exitoso de validación de reglas de negocio para creación."""
        # Arrange
        expected_validation = {
            "is_valid": True,
            "rules_checked": ["name_not_empty", "email_format", "active_client_completeness"],
            "violations": [],
            "warnings": []
        }
        
        client_domain_service.validation.validate_business_rules.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_business_rules(sample_client_create)

        # Assert
        assert result == expected_validation
        assert result["is_valid"] is True
        assert len(result["violations"]) == 0
        assert "name_not_empty" in result["rules_checked"]
        client_domain_service.validation.validate_business_rules.assert_called_once_with(
            sample_client_create
        )

    async def test_validate_business_rules_success_update(
        self,
        client_domain_service: ClientDomainService,
        sample_client_update: ClientUpdate
    ):
        """Test exitoso de validación de reglas de negocio para actualización."""
        # Arrange
        expected_validation = {
            "is_valid": True,
            "rules_checked": ["name_not_empty", "email_format"],
            "violations": [],
            "warnings": ["Cliente activo sin código configurado"]
        }
        
        client_domain_service.validation.validate_business_rules.return_value = expected_validation

        # Act
        result = await client_domain_service.validate_business_rules(sample_client_update)

        # Assert
        assert result == expected_validation
        assert result["is_valid"] is True
        assert len(result["violations"]) == 0
        assert len(result["warnings"]) == 1
        client_domain_service.validation.validate_business_rules.assert_called_once_with(
            sample_client_update
        )

    async def test_validate_business_rules_violations(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test de validación de reglas de negocio con violaciones."""
        # Arrange
        validation_with_violations = {
            "is_valid": False,
            "rules_checked": ["name_not_empty", "email_format"],
            "violations": [
                "El nombre del cliente no puede estar vacío",
                "Formato de email inválido"
            ],
            "warnings": []
        }
        
        client_domain_service.validation.validate_business_rules.return_value = validation_with_violations

        # Act
        result = await client_domain_service.validate_business_rules(sample_client_create)

        # Assert
        assert result == validation_with_violations
        assert result["is_valid"] is False
        assert len(result["violations"]) == 2
        assert "El nombre del cliente no puede estar vacío" in result["violations"]

    async def test_validate_business_rules_service_error(
        self,
        client_domain_service: ClientDomainService,
        sample_client_create: ClientCreate
    ):
        """Test de validación de reglas de negocio con error de servicio."""
        # Arrange
        client_domain_service.validation.validate_business_rules.side_effect = BusinessLogicError(
            message="Error en validación de reglas de negocio"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.validate_business_rules(sample_client_create)
        
        assert "Error en validación de reglas de negocio" in str(exc_info.value)

    # ==================== TESTS PARA validate_email_uniqueness ====================

    async def test_validate_email_uniqueness_unique_email(
        self,
        client_domain_service: ClientDomainService
    ):
        """Test de validación de unicidad de email - email único."""
        # Arrange
        email = "unique@example.com"
        expected_result = {
            "email": email,
            "is_unique": True,
            "conflicting_client_id": None,
            "exclude_client_id": None
        }
        
        client_domain_service.validation.validate_email_uniqueness.return_value = expected_result

        # Act
        result = await client_domain_service.validate_email_uniqueness(email)

        # Assert
        assert result == expected_result
        assert result["is_unique"] is True
        assert result["conflicting_client_id"] is None
        client_domain_service.validation.validate_email_uniqueness.assert_called_once_with(
            email, None
        )

    async def test_validate_email_uniqueness_duplicate_email(
        self,
        client_domain_service: ClientDomainService
    ):
        """Test de validación de unicidad de email - email duplicado."""
        # Arrange
        email = "duplicate@example.com"
        conflicting_id = uuid4()
        expected_result = {
            "email": email,
            "is_unique": False,
            "conflicting_client_id": conflicting_id,
            "exclude_client_id": None
        }
        
        client_domain_service.validation.validate_email_uniqueness.return_value = expected_result

        # Act
        result = await client_domain_service.validate_email_uniqueness(email)

        # Assert
        assert result == expected_result
        assert result["is_unique"] is False
        assert result["conflicting_client_id"] == conflicting_id

    async def test_validate_email_uniqueness_with_exclusion(
        self,
        client_domain_service: ClientDomainService
    ):
        """Test de validación de unicidad de email con exclusión de cliente."""
        # Arrange
        email = "test@example.com"
        exclude_id = uuid4()
        expected_result = {
            "email": email,
            "is_unique": True,
            "conflicting_client_id": None,
            "exclude_client_id": exclude_id
        }
        
        client_domain_service.validation.validate_email_uniqueness.return_value = expected_result

        # Act
        result = await client_domain_service.validate_email_uniqueness(email, exclude_id)

        # Assert
        assert result == expected_result
        assert result["is_unique"] is True
        assert result["exclude_client_id"] == exclude_id
        client_domain_service.validation.validate_email_uniqueness.assert_called_once_with(
            email, exclude_id
        )

    async def test_validate_email_uniqueness_service_error(
        self,
        client_domain_service: ClientDomainService
    ):
        """Test de validación de unicidad de email con error de servicio."""
        # Arrange
        email = "error@example.com"
        client_domain_service.validation.validate_email_uniqueness.side_effect = BusinessLogicError(
            message="Error en validación de unicidad de email"
        )

        # Act & Assert
        with pytest.raises(BusinessLogicError) as exc_info:
            await client_domain_service.validate_email_uniqueness(email)
        
        assert "Error en validación de unicidad de email" in str(exc_info.value)
        client_domain_service.validation.validate_email_uniqueness.assert_called_once_with(
            email, None
        )