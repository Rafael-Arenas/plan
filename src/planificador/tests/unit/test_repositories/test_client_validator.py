"""Tests unitarios para ClientValidator.

Este módulo contiene tests para el validador de clientes,
validando todas las reglas de negocio y validaciones de formato
implementadas en la clase ClientValidator.

Autor: Sistema de Testing
Fecha: 21 de agosto de 2025
"""

import pytest
from unittest.mock import AsyncMock, MagicMock, patch
from datetime import datetime
from typing import Dict, Any

from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.database.repositories.client.client_validator import (
    ClientValidator,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate
from planificador.exceptions import (
    ValidationError,
    ConflictError,
)
from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
)


class TestClientValidator:
    """Tests para ClientValidator."""

    @pytest.fixture
    def mock_session(self):
        """Fixture para sesión mock de SQLAlchemy."""
        session = AsyncMock(spec=AsyncSession)
        return session

    @pytest.fixture
    def client_validator(self, mock_session):
        """Fixture para ClientValidator con dependencias mock."""
        return ClientValidator(session=mock_session)

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

    # Tests para validate_email_format
    def test_validate_email_format_valid_emails(
        self, client_validator
    ):
        """Test: Validación de emails válidos."""
        valid_emails = [
            "test@example.com",
            "user.name@domain.co.uk",
            "firstname+lastname@company.org",
            "user123@test-domain.com"
        ]
        
        for email in valid_emails:
            result = client_validator.validate_email_format(email)
            assert result is True, f"Email {email} debería ser válido"

    def test_validate_email_format_invalid_emails(
        self, client_validator
    ):
        """Test: Validación de emails con formato inválido."""
        invalid_emails = [
            "invalid-email",
            "@domain.com",
            "user@",
            "user.domain.com"
        ]
        
        for email in invalid_emails:
            result = client_validator.validate_email_format(email)
            assert result is False, f"Email {email} debería ser inválido"

    # Tests para validate_phone_format
    def test_validate_phone_format_valid_phones(
        self, client_validator
    ):
        """Test: Validación de teléfonos válidos."""
        valid_phones = [
            "+1234567890",
            "+56912345678",
            "+44207123456",
            "+33123456789"
        ]
        
        for phone in valid_phones:
            result = client_validator.validate_phone_format(phone)
            assert result is True, f"Teléfono {phone} debería ser válido"

    def test_validate_phone_format_invalid_phones(
        self, client_validator
    ):
        """Test: Validación de teléfonos con formato inválido."""
        invalid_phones = [
            "123",  # Muy corto (menos de 7 caracteres)
            "abcd1234",  # Contiene letras
            "+",  # Solo símbolo +
            "123456789012345678901"  # Muy largo (más de 20 caracteres)
        ]
        
        for phone in invalid_phones:
            result = client_validator.validate_phone_format(phone)
            assert result is False, f"Teléfono {phone} debería ser inválido"

    # Tests para validate_code_exists
    @pytest.mark.asyncio
    async def test_validate_code_exists_found(
        self, client_validator, mock_client
    ):
        """Test: Código de cliente existe en la base de datos."""
        # Arrange
        client_code = "TC001"
        mock_result = AsyncMock()
        mock_result.scalar_one_or_none.return_value = mock_client
        client_validator.session.execute.return_value = mock_result
        
        # Act
        result = await client_validator.validate_code_exists(client_code)
        
        # Assert
        assert result is True
        client_validator.session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_code_exists_found(
        self, client_validator
    ):
        """Test: Código de cliente encontrado."""
        # Arrange
        client_code = "CLI001"
        mock_client = MagicMock()
        
        # Mock de la sesión y resultado
        mock_result = MagicMock()
        mock_result.scalar_one_or_none.return_value = mock_client
        client_validator.session.execute = AsyncMock(return_value=mock_result)
        
        # Act
        result = await client_validator.validate_code_exists(client_code)
        
        # Assert
        assert result is True
        client_validator.session.execute.assert_called_once()

    @pytest.mark.asyncio
    async def test_validate_code_exists_sqlalchemy_error(
        self, client_validator
    ):
        """Test: Error de SQLAlchemy al validar código de cliente."""
        # Arrange
        client_code = "TC001"
        client_validator.session.execute.side_effect = SQLAlchemyError("DB Error")
        
        # Act & Assert
        with pytest.raises(Exception):  # Se espera conversión de error
            await client_validator.validate_code_exists(client_code)



    # Tests para validate_client_data
    def test_validate_client_data_success(
        self, client_validator, valid_client_data
    ):
        """Test: Validación exitosa de datos de cliente."""
        # Arrange - usar diccionario directamente
        client_data = valid_client_data.copy()
        
        # Act
        result = client_validator.validate_client_data(client_data)
        
        # Assert
        assert isinstance(result, dict)  # Retorna diccionario validado
        assert result["name"] == valid_client_data["name"]

    def test_validate_client_data_missing_required_field(
        self, client_validator
    ):
        """Test: Error por campo requerido faltante."""
        # Arrange - datos sin campo requerido
        client_data = {"description": "Test client"}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            client_validator.validate_client_data(client_data)
        
        assert "requerido" in str(exc_info.value).lower()

    def test_validate_client_data_invalid_email_format(
        self, client_validator, valid_client_data
    ):
        """Test: Error por formato de email inválido."""
        # Arrange
        client_data = valid_client_data.copy()
        client_data["email"] = "invalid-email"
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            client_validator.validate_client_data(client_data)
        
        assert "email" in str(exc_info.value).lower()

    def test_validate_client_data_invalid_phone_format(
        self, client_validator, valid_client_data
    ):
        """Test: Error por formato de teléfono inválido."""
        # Arrange
        client_data = valid_client_data.copy()
        client_data["phone"] = "invalid-phone"
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            client_validator.validate_client_data(client_data)
        
        assert "teléfono" in str(exc_info.value).lower()

    # Tests para validate_creation_business_day (método que sí existe)
    def test_validate_creation_business_day_success(
        self, client_validator
    ):
        """Test: Validación exitosa de día laborable."""
        with patch('planificador.database.repositories.client.client_validator.is_business_day') as mock_is_business:
            mock_is_business.return_value = True
            
            # Act
            result = client_validator.validate_creation_business_day(validate_business_day=True)
            
            # Assert
            assert result is None  # No se lanza excepción

    # Tests para validate_update_data
    @pytest.mark.asyncio
    async def test_validate_update_data_success(
        self, client_validator, mock_client
    ):
        """Test: Validación exitosa de datos de actualización."""
        # Arrange
        update_data = {"name": "Updated Name"}
        
        # Act
        result = client_validator.validate_update_data(update_data)
        
        # Assert
        assert result == update_data  # Retorna los datos validados

    @pytest.mark.asyncio
    async def test_validate_update_data_email_change(
        self, client_validator, mock_client
    ):
        """Test: Validación de cambio de email en actualización."""
        # Arrange
        update_data = {"email": "newemail@example.com"}
        
        # Act
        result = client_validator.validate_update_data(update_data)
        
        # Assert
        assert result["email"] == "newemail@example.com"  # Email validado

    @pytest.mark.asyncio
    async def test_validate_update_data_invalid_email(
        self, client_validator, mock_client
    ):
        """Test: Error por email inválido en actualización."""
        # Arrange
        update_data = {"email": "invalid-email"}
        
        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            client_validator.validate_update_data(update_data)
        
        assert "email" in str(exc_info.value).lower()

    # Tests para validate_creation_business_day
    def test_validate_business_day_weekday(
        self, client_validator
    ):
        """Test: Validación de día laboral (lunes a viernes)."""
        with patch('planificador.database.repositories.client.client_validator.is_business_day') as mock_is_business:
            mock_is_business.return_value = True
            
            # Act
            result = client_validator.validate_creation_business_day(validate_business_day=True)
            
            # Assert
            assert result is None  # No se lanza excepción
            mock_is_business.assert_called_once()

    def test_validate_business_day_weekend(
        self, client_validator
    ):
        """Test: Validación de día no laboral (fin de semana)."""
        with patch('planificador.database.repositories.client.client_validator.is_business_day') as mock_is_business:
            mock_is_business.return_value = False
            
            # Act & Assert
            with pytest.raises(ValidationError) as exc_info:
                client_validator.validate_creation_business_day(validate_business_day=True)
            
            assert "días laborables" in str(exc_info.value)