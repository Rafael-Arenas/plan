"""Tests para schemas de cliente.

Este módulo contiene tests unitarios para validar los schemas Pydantic
relacionados con clientes: ClientBase, ClientCreate, ClientUpdate, Client y ClientWithProjects.
"""

import pytest
from typing import Dict, Any, List
from pydantic import ValidationError
from datetime import datetime

from planificador.schemas.client.client import (
    ClientBase,
    ClientCreate,
    ClientUpdate,
    Client,
    ClientWithProjects
)
from planificador.schemas.base.base import BaseSchema


class TestClientBase:
    """Tests para el schema ClientBase."""
    
    def test_valid_client_base_creation(self, valid_client_base_data: Dict[str, Any]):
        """Test: Creación válida de ClientBase con todos los campos.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        client = ClientBase(**valid_client_base_data)
        
        assert client.name == valid_client_base_data["name"]
        assert client.code == valid_client_base_data["code"]
        assert client.contact_person == valid_client_base_data["contact_person"]
        assert client.email == valid_client_base_data["email"]
        assert client.phone == valid_client_base_data["phone"]
        assert client.is_active == valid_client_base_data["is_active"]
        assert client.notes == valid_client_base_data["notes"]
    
    def test_minimal_client_base_creation(self, minimal_client_data: Dict[str, Any]):
        """Test: Creación de ClientBase con campos mínimos requeridos.
        
        Args:
            minimal_client_data: Fixture con datos mínimos
        """
        client = ClientBase(**minimal_client_data)
        
        assert client.name == minimal_client_data["name"]
        assert client.code == minimal_client_data["code"]
        # Verificar valores por defecto
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is True  # Valor por defecto
        assert client.notes is None
    
    def test_client_base_with_none_optionals(self, client_data_with_none_optionals: Dict[str, Any]):
        """Test: ClientBase con campos opcionales explícitamente None.
        
        Args:
            client_data_with_none_optionals: Fixture con campos opcionales None
        """
        client = ClientBase(**client_data_with_none_optionals)
        
        assert client.name == client_data_with_none_optionals["name"]
        assert client.code == client_data_with_none_optionals["code"]
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.notes is None
    
    def test_client_base_maximal_lengths(self, maximal_client_data: Dict[str, Any]):
        """Test: ClientBase con longitudes máximas permitidas.
        
        Args:
            maximal_client_data: Fixture con datos en longitud máxima
        """
        client = ClientBase(**maximal_client_data)
        
        assert len(client.name) == 100
        assert len(client.code) == 20
        assert len(client.contact_person) == 100
        assert len(client.phone) == 20
        assert len(client.notes) == 500
    
    def test_client_base_empty_name_validation_error(self, invalid_client_empty_name: Dict[str, Any]):
        """Test: Error de validación con nombre vacío.
        
        Args:
            invalid_client_empty_name: Fixture con nombre vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(**invalid_client_empty_name)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Verificar que hay error en el campo 'name'
        name_errors = [e for e in errors if e['loc'] == ('name',)]
        assert len(name_errors) > 0
    
    def test_client_base_empty_code_validation_error(self, invalid_client_short_code: Dict[str, Any]):
        """Test: Error de validación con código vacío.
        
        Args:
            invalid_client_short_code: Fixture con código vacío
        """
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(**invalid_client_short_code)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Verificar que hay error en el campo 'code'
        code_errors = [e for e in errors if e['loc'] == ('code',)]
        assert len(code_errors) > 0
    
    def test_client_base_invalid_email_validation_error(self, invalid_client_email: Dict[str, Any]):
        """Test: Error de validación con email inválido.
        
        Args:
            invalid_client_email: Fixture con email inválido
        """
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(**invalid_client_email)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Verificar que hay error en el campo 'email'
        email_errors = [e for e in errors if e['loc'] == ('email',)]
        assert len(email_errors) > 0
    
    def test_client_base_long_name_validation_error(self, invalid_client_long_name: Dict[str, Any]):
        """Test: Error de validación con nombre muy largo.
        
        Args:
            invalid_client_long_name: Fixture con nombre muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(**invalid_client_long_name)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Verificar que hay error de longitud en 'name'
        name_errors = [e for e in errors if e['loc'] == ('name',) and 'string_too_long' in e['type']]
        assert len(name_errors) > 0
    
    def test_client_base_long_code_validation_error(self, invalid_client_long_code: Dict[str, Any]):
        """Test: Error de validación con código muy largo.
        
        Args:
            invalid_client_long_code: Fixture con código muy largo
        """
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(**invalid_client_long_code)
        
        errors = exc_info.value.errors()
        assert len(errors) > 0
        # Verificar que hay error de longitud en 'code'
        code_errors = [e for e in errors if e['loc'] == ('code',) and 'string_too_long' in e['type']]
        assert len(code_errors) > 0


class TestClientCreate:
    """Tests para el schema ClientCreate."""
    
    def test_valid_client_create(self, valid_client_create_data: Dict[str, Any]):
        """Test: Creación válida de ClientCreate.
        
        Args:
            valid_client_create_data: Fixture con datos válidos para creación
        """
        client = ClientCreate(**valid_client_create_data)
        
        assert client.name == valid_client_create_data["name"]
        assert client.code == valid_client_create_data["code"]
        assert client.contact_person == valid_client_create_data["contact_person"]
        assert client.email == valid_client_create_data["email"]
        assert client.phone == valid_client_create_data["phone"]
        assert client.is_active == valid_client_create_data["is_active"]
        assert client.notes == valid_client_create_data["notes"]
    
    def test_client_create_minimal_data(self, minimal_client_data: Dict[str, Any]):
        """Test: ClientCreate con datos mínimos.
        
        Args:
            minimal_client_data: Fixture con datos mínimos
        """
        client = ClientCreate(**minimal_client_data)
        
        assert client.name == minimal_client_data["name"]
        assert client.code == minimal_client_data["code"]
        assert client.is_active is True  # Valor por defecto
    
    def test_client_create_inheritance_from_base(self, valid_client_create_data: Dict[str, Any]):
        """Test: ClientCreate hereda correctamente de ClientBase.
        
        Args:
            valid_client_create_data: Fixture con datos válidos
        """
        client = ClientCreate(**valid_client_create_data)
        
        # Verificar que es instancia de ClientBase
        assert isinstance(client, ClientBase)
        
        # Verificar que tiene todos los campos de ClientBase
        assert hasattr(client, 'name')
        assert hasattr(client, 'code')
        assert hasattr(client, 'contact_person')
        assert hasattr(client, 'email')
        assert hasattr(client, 'phone')
        assert hasattr(client, 'is_active')
        assert hasattr(client, 'notes')


class TestClientUpdate:
    """Tests para el schema ClientUpdate."""
    
    def test_valid_client_update(self, valid_client_update_data: Dict[str, Any]):
        """Test: Actualización válida de cliente.
        
        Args:
            valid_client_update_data: Fixture con datos válidos para actualización
        """
        client = ClientUpdate(**valid_client_update_data)
        
        assert client.name == valid_client_update_data["name"]
        assert client.contact_person == valid_client_update_data["contact_person"]
        assert client.email == valid_client_update_data["email"]
        assert client.is_active == valid_client_update_data["is_active"]
        assert client.notes == valid_client_update_data["notes"]
    
    def test_client_update_partial_data(self):
        """Test: ClientUpdate con datos parciales."""
        partial_data = {
            "name": "Updated Name Only"
        }
        
        client = ClientUpdate(**partial_data)
        
        assert client.name == "Updated Name Only"
        # Otros campos deben ser None (no especificados)
        assert client.code is None
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is None
        assert client.notes is None
    
    def test_client_update_empty_data(self):
        """Test: ClientUpdate con datos vacíos (todos opcionales)."""
        client = ClientUpdate()
        
        # Todos los campos deben ser None
        assert client.name is None
        assert client.code is None
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is None
        assert client.notes is None
    
    def test_client_update_inheritance_from_base(self, valid_client_update_data: Dict[str, Any]):
        """Test: ClientUpdate hereda correctamente de BaseSchema.
        
        Args:
            valid_client_update_data: Fixture con datos válidos
        """
        client = ClientUpdate(**valid_client_update_data)
        
        # Verificar que es instancia de BaseSchema
        assert isinstance(client, BaseSchema)
        # Verificar que tiene los campos esperados
        assert hasattr(client, 'name')
        assert hasattr(client, 'code')
        assert hasattr(client, 'contact_person')
        assert hasattr(client, 'email')
        assert hasattr(client, 'phone')
        assert hasattr(client, 'is_active')
        assert hasattr(client, 'notes')


class TestClient:
    """Tests para el schema Client (con campos de BD)."""
    
    def test_valid_client_with_db_fields(self, valid_client_data: Dict[str, Any]):
        """Test: Creación válida de Client con campos de base de datos.
        
        Args:
            valid_client_data: Fixture con datos válidos incluyendo campos de BD
        """
        client = Client(**valid_client_data)
        
        # Verificar campos heredados de ClientBase
        assert client.name == valid_client_data["name"]
        assert client.code == valid_client_data["code"]
        assert client.email == valid_client_data["email"]
        
        # Verificar campos específicos de BD
        assert client.id == valid_client_data["id"]
        
        # Verificar campos datetime (convertir strings a datetime para comparación)
        from datetime import datetime as dt
        expected_created_at = dt.fromisoformat(valid_client_data["created_at"])
        expected_updated_at = dt.fromisoformat(valid_client_data["updated_at"])
        assert client.created_at == expected_created_at
        assert client.updated_at == expected_updated_at
    
    def test_client_inheritance_from_base(self, valid_client_data: Dict[str, Any]):
        """Test: Client hereda correctamente de ClientBase.
        
        Args:
            valid_client_data: Fixture con datos válidos
        """
        client = Client(**valid_client_data)
        
        # Verificar que es instancia de ClientBase
        assert isinstance(client, ClientBase)
        
        # Verificar que tiene campos adicionales de BD
        assert hasattr(client, 'id')
        assert hasattr(client, 'created_at')
        assert hasattr(client, 'updated_at')
    
    def test_client_datetime_fields(self, valid_client_data: Dict[str, Any]):
        """Test: Campos datetime en Client.
        
        Args:
            valid_client_data: Fixture con datos válidos
        """
        client = Client(**valid_client_data)
        
        assert isinstance(client.created_at, datetime)
        assert isinstance(client.updated_at, datetime)


class TestClientWithProjects:
    """Tests para el schema ClientWithProjects."""
    
    def test_valid_client_with_empty_projects(self, valid_client_with_projects_data: Dict[str, Any]):
        """Test: ClientWithProjects con lista vacía de proyectos.
        
        Args:
            valid_client_with_projects_data: Fixture con datos válidos y proyectos vacíos
        """
        client = ClientWithProjects(**valid_client_with_projects_data)
        
        # Verificar campos heredados
        assert client.name == valid_client_with_projects_data["name"]
        assert client.id == valid_client_with_projects_data["id"]
        
        # Verificar lista de proyectos
        assert client.projects == []
        assert isinstance(client.projects, list)
    
    def test_client_with_projects_inheritance(self, valid_client_with_projects_data: Dict[str, Any]):
        """Test: ClientWithProjects hereda correctamente de Client.
        
        Args:
            valid_client_with_projects_data: Fixture con datos válidos
        """
        client = ClientWithProjects(**valid_client_with_projects_data)
        
        # Verificar que es instancia de Client y ClientBase
        assert isinstance(client, Client)
        assert isinstance(client, ClientBase)
        
        # Verificar que tiene campo adicional projects
        assert hasattr(client, 'projects')
    
    def test_client_with_projects_default_empty_list(self, valid_client_data: Dict[str, Any]):
        """Test: ClientWithProjects con lista por defecto vacía.
        
        Args:
            valid_client_data: Fixture con datos válidos sin campo projects
        """
        # No incluir 'projects' en los datos
        client = ClientWithProjects(**valid_client_data)
        
        # Debe tener lista vacía por defecto
        assert client.projects == []
        assert isinstance(client.projects, list)


class TestClientSchemasEdgeCases:
    """Tests para casos edge y validaciones especiales."""
    
    def test_email_variations_validation(self, email_variations: str):
        """Test: Validación de diferentes formatos de email.
        
        Args:
            email_variations: Fixture con email individual (válido o inválido)
        """
        # Lista de emails válidos (primeros 4 de la fixture)
        valid_emails = [
            "test@example.com",
            "test.name@example.co.uk", 
            "test_123@sub.example.com",
            "user+tag@domain.org"
        ]
        
        data = {"name": "Test", "code": "TC-001", "email": email_variations}
        
        if email_variations in valid_emails:
            # Email válido - debería funcionar
            client = ClientBase(**data)
            assert client.email == email_variations
        else:
            # Email inválido - debería fallar
            if email_variations:  # Skip empty string
                with pytest.raises(ValidationError):
                    ClientBase(**data)
    
    def test_all_length_validation_errors(self):
        """Test: Validación de errores de longitud en todos los campos."""
        base_data = {"name": "Test", "code": "TC-001"}
        
        # Test longitud excesiva en cada campo
        length_tests = [
            ("name", "A" * 101, 100),  # max_length=100
            ("code", "B" * 21, 20),    # max_length=20
            ("contact_person", "C" * 101, 100),  # max_length=100
            ("phone", "1" * 21, 20),   # max_length=20
            ("notes", "D" * 501, 500)  # max_length=500
        ]
        
        for field_name, long_value, max_length in length_tests:
            data = {**base_data, field_name: long_value}
            
            with pytest.raises(ValidationError) as exc_info:
                ClientBase(**data)
            
            errors = exc_info.value.errors()
            field_errors = [e for e in errors if e['loc'] == (field_name,)]
            assert len(field_errors) > 0
            assert 'string_too_long' in field_errors[0]['type']
    
    def test_required_fields_validation(self):
        """Test: Validación de campos requeridos."""
        # Test sin campo 'name'
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(code="TC-001")
        
        errors = exc_info.value.errors()
        name_errors = [e for e in errors if e['loc'] == ('name',)]
        assert len(name_errors) > 0
        assert 'missing' in name_errors[0]['type']
        
        # Test sin campo 'code'
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name="Test Client")
        
        errors = exc_info.value.errors()
        code_errors = [e for e in errors if e['loc'] == ('code',)]
        assert len(code_errors) > 0
        assert 'missing' in code_errors[0]['type']
        
        # Test sin ambos campos requeridos
        with pytest.raises(ValidationError) as exc_info:
            ClientBase()
        
        errors = exc_info.value.errors()
        assert len(errors) >= 2  # Al menos errores para 'name' y 'code'
    
    def test_empty_string_validation(self):
        """Test: Validación de strings vacíos en campos requeridos."""
        # Test name vacío
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name="", code="TC-001")
        
        errors = exc_info.value.errors()
        name_errors = [e for e in errors if e['loc'] == ('name',)]
        assert len(name_errors) > 0
        
        # Test code vacío
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name="Test", code="")
        
        errors = exc_info.value.errors()
        code_errors = [e for e in errors if e['loc'] == ('code',)]
        assert len(code_errors) > 0
    
    def test_whitespace_only_validation(self):
        """Test: Validación de campos con solo espacios en blanco."""
        # Pydantic permite strings con solo espacios por defecto
        # pero podemos verificar que se preservan
        client_with_spaces = ClientBase(name="   ", code="TC-001")
        assert client_with_spaces.name == "   "
        
        client_with_code_spaces = ClientBase(name="Test", code="   ")
        assert client_with_code_spaces.code == "   "
        
        # Test que strings completamente vacíos fallan por min_length
        with pytest.raises(ValidationError) as exc_info:
            ClientBase(name="", code="TC-001")
        
        errors = exc_info.value.errors()
        name_errors = [e for e in errors if e['loc'] == ('name',)]
        assert len(name_errors) > 0
        assert any('at least 1 character' in str(e.get('msg', '')) for e in name_errors)
    
    def test_special_characters_in_fields(self):
        """Test: Caracteres especiales en diferentes campos."""
        special_chars_data = {
            "name": "Test@Client#2024",
            "code": "TC-001_SPECIAL",
            "contact_person": "John O'Connor-Smith",
            "phone": "+1 (555) 123-4567",
            "notes": "Notas con: símbolos, números 123, y más!"
        }
        
        # Debería ser válido
        client = ClientBase(**special_chars_data)
        
        assert client.name == special_chars_data["name"]
        assert client.code == special_chars_data["code"]
        assert client.contact_person == special_chars_data["contact_person"]
        assert client.phone == special_chars_data["phone"]
        assert client.notes == special_chars_data["notes"]
    
    def test_numeric_strings_validation(self):
        """Test: Validación de strings que contienen solo números."""
        numeric_data = {
            "name": "12345",
            "code": "67890",
            "contact_person": "123456789",
            "phone": "1234567890"
        }
        
        # Debería ser válido (son strings)
        client = ClientBase(**numeric_data)
        
        assert client.name == "12345"
        assert client.code == "67890"
        assert client.contact_person == "123456789"
        assert client.phone == "1234567890"
    
    def test_mixed_case_email_validation(self):
        """Test: Validación de emails con diferentes casos."""
        test_cases = [
            ("Test@Example.COM", "Test@example.com"),
            ("USER.name@DOMAIN.org", "USER.name@domain.org"),
            ("MixedCase@example.Co.UK", "MixedCase@example.co.uk")
        ]

        for original_email, expected_email in test_cases:
            data = {"name": "Test", "code": "TC-001", "email": original_email}
            client = ClientBase(**data)
            # EmailStr normaliza solo el dominio a minúsculas
            assert client.email == expected_email
    
    def test_boolean_field_variations(self):
        """Test: Validación del campo booleano is_active."""
        base_data = {"name": "Test", "code": "TC-001"}
        
        # Test valores booleanos válidos
        for value in [True, False]:
            data = {**base_data, "is_active": value}
            client = ClientBase(**data)
            assert client.is_active == value
        
        # Test conversión de valores "truthy/falsy"
        truthy_values = [1, "true", "yes", "1"]
        falsy_values = [0, "false", "no", "0"]
        
        for value in truthy_values:
            data = {**base_data, "is_active": value}
            client = ClientBase(**data)
            assert client.is_active is True
        
        for value in falsy_values:
            data = {**base_data, "is_active": value}
            client = ClientBase(**data)
            assert client.is_active is False
        
        # Test que string vacío causa ValidationError
        with pytest.raises(ValidationError):
            data = {**base_data, "is_active": ""}
            ClientBase(**data)
    
    def test_string_field_whitespace_handling(self):
        """Test: Manejo de espacios en blanco en campos de texto."""
        # Test con espacios al inicio y final
        data = {
            "name": "  Test Client  ",
            "code": "  TC-001  ",
            "contact_person": "  John Doe  "
        }
        
        client = ClientBase(**data)
        
        # Pydantic debería mantener los espacios (no hace strip automático)
        assert client.name == "  Test Client  "
        assert client.code == "  TC-001  "
        assert client.contact_person == "  John Doe  "
    
    def test_unicode_characters_support(self):
        """Test: Soporte para caracteres Unicode."""
        data = {
            "name": "Cliente Ñoño 测试",
            "code": "TC-ÑÑ1",
            "contact_person": "José María",
            "notes": "Notas con émojis 🚀 y acentos"
        }
        
        client = ClientBase(**data)
        
        assert client.name == "Cliente Ñoño 测试"
        assert client.code == "TC-ÑÑ1"
        assert client.contact_person == "José María"
        assert client.notes == "Notas con émojis 🚀 y acentos"


class TestClientSchemasSerialization:
    """Tests para serialización y deserialización de schemas de cliente."""
    
    def test_client_base_to_dict(self, valid_client_base_data: Dict[str, Any]):
        """Test: Serialización de ClientBase a diccionario.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        client = ClientBase(**valid_client_base_data)
        client_dict = client.model_dump()
        
        # Verificar que todos los campos están presentes
        assert client_dict["name"] == valid_client_base_data["name"]
        assert client_dict["code"] == valid_client_base_data["code"]
        assert client_dict["contact_person"] == valid_client_base_data["contact_person"]
        assert client_dict["email"] == valid_client_base_data["email"]
        assert client_dict["phone"] == valid_client_base_data["phone"]
        assert client_dict["is_active"] == valid_client_base_data["is_active"]
        assert client_dict["notes"] == valid_client_base_data["notes"]
    
    def test_client_base_to_json(self, valid_client_base_data: Dict[str, Any]):
        """Test: Serialización de ClientBase a JSON.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        client = ClientBase(**valid_client_base_data)
        json_str = client.model_dump_json()
        
        # Verificar que es un string JSON válido
        assert isinstance(json_str, str)
        assert json_str.startswith('{')
        assert json_str.endswith('}')
        
        # Verificar que contiene los campos esperados
        assert '"name"' in json_str
        assert '"code"' in json_str
        assert '"is_active"' in json_str
    
    def test_client_from_dict_deserialization(self, valid_client_base_data: Dict[str, Any]):
        """Test: Deserialización de ClientBase desde diccionario.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        # Crear cliente desde diccionario
        client = ClientBase.model_validate(valid_client_base_data)
        
        assert client.name == valid_client_base_data["name"]
        assert client.code == valid_client_base_data["code"]
        assert client.email == valid_client_base_data["email"]
    
    def test_client_from_json_deserialization(self, valid_client_base_data: Dict[str, Any]):
        """Test: Deserialización de ClientBase desde JSON.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        import json
        
        # Convertir a JSON string
        json_str = json.dumps(valid_client_base_data)
        
        # Crear cliente desde JSON
        client = ClientBase.model_validate_json(json_str)
        
        assert client.name == valid_client_base_data["name"]
        assert client.code == valid_client_base_data["code"]
        assert client.email == valid_client_base_data["email"]
    
    def test_client_with_datetime_serialization(self, valid_client_data: Dict[str, Any]):
        """Test: Serialización de Client con campos datetime.
        
        Args:
            valid_client_data: Fixture con datos válidos incluyendo datetime
        """
        client = Client(**valid_client_data)
        client_dict = client.model_dump()
        
        # Verificar que los campos datetime están presentes
        assert "created_at" in client_dict
        assert "updated_at" in client_dict
        
        # Verificar que las fechas se serializan correctamente como objetos datetime
        assert isinstance(client_dict["created_at"], datetime)
        assert isinstance(client_dict["updated_at"], datetime)
        
        # Verificar que las fechas coinciden con los valores originales
        from datetime import datetime as dt
        expected_created_at = dt.fromisoformat(valid_client_data["created_at"])
        expected_updated_at = dt.fromisoformat(valid_client_data["updated_at"])
        assert client_dict["created_at"] == expected_created_at
        assert client_dict["updated_at"] == expected_updated_at
    
    def test_client_with_datetime_json_serialization(self, valid_client_data: Dict[str, Any]):
        """Test: Serialización JSON de Client con campos datetime.
        
        Args:
            valid_client_data: Fixture con datos válidos incluyendo datetime
        """
        client = Client(**valid_client_data)
        json_str = client.model_dump_json()
        
        # Verificar que es JSON válido
        assert isinstance(json_str, str)
        
        # Verificar que contiene campos datetime serializados
        assert '"created_at"' in json_str
        assert '"updated_at"' in json_str
    
    def test_client_with_projects_serialization(self, valid_client_with_projects_data: Dict[str, Any]):
        """Test: Serialización de ClientWithProjects.
        
        Args:
            valid_client_with_projects_data: Fixture con datos válidos y proyectos
        """
        client = ClientWithProjects(**valid_client_with_projects_data)
        client_dict = client.model_dump()
        
        # Verificar que el campo projects está presente
        assert "projects" in client_dict
        assert client_dict["projects"] == []
        assert isinstance(client_dict["projects"], list)
        
        # Verificar otros campos heredados
        assert client_dict["name"] == valid_client_with_projects_data["name"]
        assert client_dict["id"] == valid_client_with_projects_data["id"]
    
    def test_client_update_partial_serialization(self):
        """Test: Serialización de ClientUpdate con datos parciales."""
        partial_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        
        client = ClientUpdate(**partial_data)
        client_dict = client.model_dump()
        
        # Verificar campos especificados
        assert client_dict["name"] == "Updated Name"
        assert client_dict["email"] == "updated@example.com"
        
        # Verificar campos no especificados (deben ser None)
        assert client_dict["code"] is None
        assert client_dict["contact_person"] is None
        assert client_dict["phone"] is None
        assert client_dict["is_active"] is None
        assert client_dict["notes"] is None
    
    def test_client_update_exclude_none_serialization(self):
        """Test: Serialización de ClientUpdate excluyendo valores None."""
        partial_data = {
            "name": "Updated Name",
            "email": "updated@example.com"
        }
        
        client = ClientUpdate(**partial_data)
        client_dict = client.model_dump(exclude_none=True)
        
        # Solo deben estar presentes los campos no-None
        assert len(client_dict) == 2
        assert client_dict["name"] == "Updated Name"
        assert client_dict["email"] == "updated@example.com"
        
        # Verificar que campos None no están presentes
        assert "code" not in client_dict
        assert "contact_person" not in client_dict
        assert "phone" not in client_dict
        assert "is_active" not in client_dict
        assert "notes" not in client_dict
    
    def test_roundtrip_serialization_deserialization(self, valid_client_base_data: Dict[str, Any]):
        """Test: Serialización y deserialización completa (roundtrip).
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        # Crear cliente original
        original_client = ClientBase(**valid_client_base_data)
        
        # Serializar a diccionario
        client_dict = original_client.model_dump()
        
        # Deserializar de vuelta
        restored_client = ClientBase.model_validate(client_dict)
        
        # Verificar que son equivalentes
        assert original_client.name == restored_client.name
        assert original_client.code == restored_client.code
        assert original_client.contact_person == restored_client.contact_person
        assert original_client.email == restored_client.email
        assert original_client.phone == restored_client.phone
        assert original_client.is_active == restored_client.is_active
        assert original_client.notes == restored_client.notes
    
    def test_json_roundtrip_serialization_deserialization(self, valid_client_base_data: Dict[str, Any]):
        """Test: Serialización y deserialización JSON completa (roundtrip).
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        # Crear cliente original
        original_client = ClientBase(**valid_client_base_data)
        
        # Serializar a JSON
        json_str = original_client.model_dump_json()
        
        # Deserializar de vuelta
        restored_client = ClientBase.model_validate_json(json_str)
        
        # Verificar que son equivalentes
        assert original_client.name == restored_client.name
        assert original_client.code == restored_client.code
        assert original_client.email == restored_client.email
        assert original_client.is_active == restored_client.is_active
    
    def test_serialization_with_unicode_characters(self):
        """Test: Serialización con caracteres Unicode."""
        unicode_data = {
            "name": "Cliente Ñoño 测试",
            "code": "TC-ÑÑ1",
            "contact_person": "José María",
            "notes": "Notas con émojis 🚀 y acentos"
        }
        
        client = ClientBase(**unicode_data)
        
        # Test serialización a diccionario
        client_dict = client.model_dump()
        assert client_dict["name"] == "Cliente Ñoño 测试"
        assert client_dict["notes"] == "Notas con émojis 🚀 y acentos"
        
        # Test serialización a JSON
        json_str = client.model_dump_json()
        assert isinstance(json_str, str)
        
        # Test deserialización desde JSON
        restored_client = ClientBase.model_validate_json(json_str)
        assert restored_client.name == "Cliente Ñoño 测试"
        assert restored_client.notes == "Notas con émojis 🚀 y acentos"
    
    def test_serialization_field_aliases(self, valid_client_base_data: Dict[str, Any]):
        """Test: Serialización con alias de campos (si existen).
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        client = ClientBase(**valid_client_base_data)
        
        # Test serialización por alias (by_alias=True)
        client_dict_alias = client.model_dump(by_alias=True)
        
        # Test serialización normal
        client_dict_normal = client.model_dump(by_alias=False)
        
        # En este caso, como no hay alias definidos, deberían ser iguales
        assert client_dict_alias == client_dict_normal
    
    def test_model_copy_functionality(self, valid_client_base_data: Dict[str, Any]):
        """Test: Funcionalidad de copia de modelos.
        
        Args:
            valid_client_base_data: Fixture con datos válidos
        """
        original_client = ClientBase(**valid_client_base_data)
        
        # Crear copia exacta
        copied_client = original_client.model_copy()
        
        # Verificar que son equivalentes pero objetos diferentes
        assert original_client.name == copied_client.name
        assert original_client.code == copied_client.code
        assert original_client is not copied_client
        
        # Crear copia con modificaciones
        modified_client = original_client.model_copy(update={"name": "Modified Name"})
        
        assert modified_client.name == "Modified Name"
        assert modified_client.code == original_client.code  # Sin cambios
        assert original_client.name != modified_client.name  # Original sin cambios


class TestClientSchemasOptionalFields:
    """Tests para validación de campos opcionales y valores por defecto."""
    
    def test_client_base_with_minimal_required_fields(self):
        """Test: Creación de ClientBase solo con campos requeridos."""
        minimal_data = {
            "name": "Cliente Mínimo",
            "code": "MIN-01"
        }
        
        client = ClientBase(**minimal_data)
        
        # Verificar campos requeridos
        assert client.name == "Cliente Mínimo"
        assert client.code == "MIN-01"
        
        # Verificar valores por defecto de campos opcionales
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is True  # Valor por defecto
        assert client.notes is None
    
    def test_client_base_optional_fields_none(self):
        """Test: Campos opcionales explícitamente establecidos como None."""
        data_with_none = {
            "name": "Cliente Test",
            "code": "TEST-01",
            "contact_person": None,
            "email": None,
            "phone": None,
            "notes": None
        }
        
        client = ClientBase(**data_with_none)
        
        assert client.name == "Cliente Test"
        assert client.code == "TEST-01"
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.notes is None
        assert client.is_active is True  # Valor por defecto
    
    def test_client_base_is_active_default_value(self):
        """Test: Valor por defecto del campo is_active."""
        data_without_is_active = {
            "name": "Cliente Default",
            "code": "DEF-01"
        }
        
        client = ClientBase(**data_without_is_active)
        
        # is_active debe tener valor por defecto True
        assert client.is_active is True
    
    def test_client_base_is_active_explicit_false(self):
        """Test: Establecer is_active explícitamente como False."""
        data_with_false = {
            "name": "Cliente Inactivo",
            "code": "INA-01",
            "is_active": False
        }
        
        client = ClientBase(**data_with_false)
        
        assert client.is_active is False
    
    def test_client_create_with_minimal_fields(self):
        """Test: ClientCreate solo con campos mínimos requeridos."""
        minimal_data = {
            "name": "Nuevo Cliente",
            "code": "NEW-01"
        }
        
        client = ClientCreate(**minimal_data)
        
        assert client.name == "Nuevo Cliente"
        assert client.code == "NEW-01"
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is True
        assert client.notes is None
    
    def test_client_update_all_fields_none(self):
        """Test: ClientUpdate con todos los campos como None (actualización vacía)."""
        empty_update = {}
        
        client = ClientUpdate(**empty_update)
        
        # Todos los campos deben ser None por defecto
        assert client.name is None
        assert client.code is None
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.is_active is None
        assert client.notes is None
    
    def test_client_update_partial_fields(self):
        """Test: ClientUpdate con solo algunos campos especificados."""
        partial_update = {
            "name": "Nombre Actualizado",
            "is_active": False
        }
        
        client = ClientUpdate(**partial_update)
        
        # Campos especificados
        assert client.name == "Nombre Actualizado"
        assert client.is_active is False
        
        # Campos no especificados deben ser None
        assert client.code is None
        assert client.contact_person is None
        assert client.email is None
        assert client.phone is None
        assert client.notes is None
    
    def test_client_update_explicit_none_values(self):
        """Test: ClientUpdate con valores None explícitos."""
        explicit_none_update = {
            "contact_person": None,
            "email": None,
            "notes": None
        }
        
        client = ClientUpdate(**explicit_none_update)
        
        assert client.contact_person is None
        assert client.email is None
        assert client.notes is None
        
        # Otros campos también deben ser None
        assert client.name is None
        assert client.code is None
        assert client.phone is None
        assert client.is_active is None
    
    def test_client_with_datetime_fields_present(self, valid_client_data: Dict[str, Any]):
        """Test: Client con campos datetime requeridos.
        
        Args:
            valid_client_data: Fixture con datos válidos incluyendo datetime
        """
        client = Client(**valid_client_data)
        
        # Verificar que los campos datetime están presentes
        assert client.created_at is not None
        assert client.updated_at is not None
        assert client.id is not None
        
        # Verificar que son del tipo correcto
        from datetime import datetime
        assert isinstance(client.created_at, datetime)
        assert isinstance(client.updated_at, datetime)
        assert isinstance(client.id, int)
    
    def test_client_with_projects_empty_list_default(self, valid_client_with_projects_data: Dict[str, Any]):
        """Test: ClientWithProjects con lista de proyectos vacía por defecto.
        
        Args:
            valid_client_with_projects_data: Fixture con datos válidos
        """
        client = ClientWithProjects(**valid_client_with_projects_data)
        
        # Verificar que projects es una lista vacía por defecto
        assert client.projects == []
        assert isinstance(client.projects, list)
        assert len(client.projects) == 0
    
    def test_optional_string_fields_empty_vs_none(self):
        """Test: Diferencia entre campos string vacíos y None."""
        # Test con string vacío para campos que lo permiten
        data_with_empty_strings = {
            "name": "Cliente Test",
            "code": "TEST-01",
            "contact_person": "",
            "phone": "",
            "notes": ""
        }
        
        client_empty = ClientBase(**data_with_empty_strings)
        
        # Strings vacíos deben ser preservados (no convertidos a None)
        assert client_empty.contact_person == ""
        assert client_empty.phone == ""
        assert client_empty.notes == ""
        
        # Test que email vacío causa ValidationError
        with pytest.raises(ValidationError):
            data_with_empty_email = {
                "name": "Cliente Test",
                "code": "TEST-01",
                "email": ""
            }
            ClientBase(**data_with_empty_email)
        
        # Test con None explícito
        data_with_none = {
            "name": "Cliente Test",
            "code": "TEST-01",
            "contact_person": None,
            "email": None,
            "phone": None,
            "notes": None
        }
        
        client_none = ClientBase(**data_with_none)
        
        assert client_none.contact_person is None
        assert client_none.email is None
        assert client_none.phone is None
        assert client_none.notes is None
    
    def test_boolean_field_variations(self):
        """Test: Variaciones del campo booleano is_active."""
        # Test con True explícito
        client_true = ClientBase(name="Test", code="T1", is_active=True)
        assert client_true.is_active is True
        
        # Test con False explícito
        client_false = ClientBase(name="Test", code="T2", is_active=False)
        assert client_false.is_active is False
        
        # Test sin especificar (valor por defecto)
        client_default = ClientBase(name="Test", code="T3")
        assert client_default.is_active is True
    
    def test_field_order_independence(self):
        """Test: El orden de los campos no afecta la creación."""
        # Orden normal
        data_normal = {
            "name": "Cliente Orden",
            "code": "ORD-01",
            "contact_person": "Juan Pérez",
            "email": "juan@example.com",
            "phone": "+1234567890",
            "is_active": True,
            "notes": "Notas del cliente"
        }
        
        # Orden diferente
        data_reordered = {
            "is_active": True,
            "notes": "Notas del cliente",
            "email": "juan@example.com",
            "name": "Cliente Orden",
            "phone": "+1234567890",
            "code": "ORD-01",
            "contact_person": "Juan Pérez"
        }
        
        client_normal = ClientBase(**data_normal)
        client_reordered = ClientBase(**data_reordered)
        
        # Ambos clientes deben ser equivalentes
        assert client_normal.name == client_reordered.name
        assert client_normal.code == client_reordered.code
        assert client_normal.contact_person == client_reordered.contact_person
        assert client_normal.email == client_reordered.email
        assert client_normal.phone == client_reordered.phone
        assert client_normal.is_active == client_reordered.is_active
        assert client_normal.notes == client_reordered.notes
    
    def test_optional_fields_with_edge_values(self):
        """Test: Campos opcionales con valores límite."""
        # Test con datos mínimos
        minimal_data = {
            "name": "A",
            "code": "A"
        }
        minimal_client = ClientBase(**minimal_data)
        assert minimal_client.name == "A"
        assert minimal_client.code == "A"
        assert minimal_client.contact_person is None
        
        # Test con datos máximos
        maximal_data = {
            "name": "A" * 100,  # Máximo permitido
            "code": "A" * 20,   # Máximo permitido
            "notes": "A" * 500  # Máximo permitido
        }
        maximal_client = ClientBase(**maximal_data)
        assert len(maximal_client.name) == 100
        assert len(maximal_client.code) == 20
        assert len(maximal_client.notes) == 500
    
    def test_client_update_preserves_unspecified_fields_concept(self):
        """Test: Concepto de que ClientUpdate preserva campos no especificados."""
        # Simular datos originales de un cliente
        original_data = {
            "name": "Cliente Original",
            "code": "ORIG-01",
            "contact_person": "Persona Original",
            "email": "original@example.com",
            "phone": "+1111111111",
            "is_active": True,
            "notes": "Notas originales"
        }
        
        # Actualización parcial
        update_data = {
            "name": "Cliente Actualizado",
            "email": "actualizado@example.com"
        }
        
        client_update = ClientUpdate(**update_data)
        
        # Solo los campos especificados en la actualización deben tener valores
        assert client_update.name == "Cliente Actualizado"
        assert client_update.email == "actualizado@example.com"
        
        # Los campos no especificados deben ser None (indicando "no cambiar")
        assert client_update.code is None
        assert client_update.contact_person is None
        assert client_update.phone is None
        assert client_update.is_active is None
        assert client_update.notes is None


class TestClientSerializationDeserialization:
    """Tests de serialización y deserialización para Client y ClientWithProjects."""
    
    def test_client_serialization_to_dict(self):
        """Test: Serialización de Client a diccionario."""
        client_data = {
            "id": 1,
            "name": "Test Client",
            "code": "TC-001",
            "contact_person": "John Doe",
            "email": "john@testclient.com",
            "phone": "+1234567890",
            "is_active": True,
            "notes": "Test notes",
            "created_at": datetime(2024, 1, 15, 10, 30, 0),
            "updated_at": datetime(2024, 1, 15, 11, 30, 0)
        }
        
        client = Client(**client_data)
        serialized = client.model_dump()
        
        # Verificar que todos los campos están presentes
        assert serialized["id"] == 1
        assert serialized["name"] == "Test Client"
        assert serialized["code"] == "TC-001"
        assert serialized["contact_person"] == "John Doe"
        assert serialized["email"] == "john@testclient.com"
        assert serialized["phone"] == "+1234567890"
        assert serialized["is_active"] is True
        assert serialized["notes"] == "Test notes"
        assert isinstance(serialized["created_at"], datetime)
        assert isinstance(serialized["updated_at"], datetime)
    
    def test_client_deserialization_from_dict(self):
        """Test: Deserialización de Client desde diccionario."""
        client_dict = {
            "id": 2,
            "name": "Another Client",
            "code": "AC-002",
            "contact_person": "Jane Smith",
            "email": "jane@anotherclient.com",
            "phone": "+0987654321",
            "is_active": False,
            "notes": "Another test notes",
            "created_at": "2024-01-16T09:15:00",
            "updated_at": "2024-01-16T10:15:00"
        }
        
        client = Client(**client_dict)
        
        # Verificar que la deserialización fue correcta
        assert client.id == 2
        assert client.name == "Another Client"
        assert client.code == "AC-002"
        assert client.contact_person == "Jane Smith"
        assert client.email == "jane@anotherclient.com"
        assert client.phone == "+0987654321"
        assert client.is_active is False
        assert client.notes == "Another test notes"
        assert isinstance(client.created_at, datetime)
        assert isinstance(client.updated_at, datetime)
    
    def test_client_json_serialization(self):
        """Test: Serialización de Client a JSON."""
        client_data = {
            "id": 3,
            "name": "JSON Client",
            "code": "JC-003",
            "contact_person": None,
            "email": None,
            "phone": None,
            "is_active": True,
            "notes": None,
            "created_at": datetime(2024, 1, 17, 14, 45, 0),
            "updated_at": datetime(2024, 1, 17, 15, 45, 0)
        }
        
        client = Client(**client_data)
        json_str = client.model_dump_json()
        
        # Verificar que es una cadena JSON válida
        assert isinstance(json_str, str)
        assert '"id":3' in json_str
        assert '"name":"JSON Client"' in json_str
        assert '"code":"JC-003"' in json_str
        assert '"is_active":true' in json_str
    
    def test_client_json_deserialization(self):
        """Test: Deserialización de Client desde JSON."""
        json_str = '''{
            "id": 4,
            "name": "From JSON Client",
            "code": "FJC-004",
            "contact_person": "Bob Wilson",
            "email": "bob@fromjson.com",
            "phone": "+1122334455",
            "is_active": true,
            "notes": "Created from JSON",
            "created_at": "2024-01-18T08:30:00",
            "updated_at": "2024-01-18T09:30:00"
        }'''
        
        client = Client.model_validate_json(json_str)
        
        # Verificar que la deserialización desde JSON fue correcta
        assert client.id == 4
        assert client.name == "From JSON Client"
        assert client.code == "FJC-004"
        assert client.contact_person == "Bob Wilson"
        assert client.email == "bob@fromjson.com"
        assert client.phone == "+1122334455"
        assert client.is_active is True
        assert client.notes == "Created from JSON"
        assert isinstance(client.created_at, datetime)
        assert isinstance(client.updated_at, datetime)
    
    def test_client_with_projects_serialization(self):
        """Test: Serialización de ClientWithProjects."""
        # Simular datos de proyecto (sin importar el schema real)
        mock_project_data = {
            "id": 1,
            "name": "Test Project",
            "code": "TP-001",
            "description": "A test project"
        }
        
        client_data = {
            "id": 5,
            "name": "Client With Projects",
            "code": "CWP-005",
            "contact_person": "Alice Brown",
            "email": "alice@clientwithprojects.com",
            "phone": "+5566778899",
            "is_active": True,
            "notes": "Client with associated projects",
            "created_at": datetime(2024, 1, 19, 12, 0, 0),
            "updated_at": datetime(2024, 1, 19, 13, 0, 0),
            "projects": []  # Lista vacía por defecto
        }
        
        client_with_projects = ClientWithProjects(**client_data)
        serialized = client_with_projects.model_dump()
        
        # Verificar que todos los campos están presentes
        assert serialized["id"] == 5
        assert serialized["name"] == "Client With Projects"
        assert serialized["code"] == "CWP-005"
        assert serialized["projects"] == []
        assert isinstance(serialized["created_at"], datetime)
        assert isinstance(serialized["updated_at"], datetime)
    
    def test_client_with_projects_empty_list_default(self):
        """Test: ClientWithProjects tiene lista vacía por defecto."""
        client_data = {
            "id": 6,
            "name": "Default Projects Client",
            "code": "DPC-006",
            "created_at": datetime(2024, 1, 20, 16, 0, 0),
            "updated_at": datetime(2024, 1, 20, 17, 0, 0)
        }
        
        client_with_projects = ClientWithProjects(**client_data)
        
        # Verificar que projects es una lista vacía por defecto
        assert client_with_projects.projects == []
        assert isinstance(client_with_projects.projects, list)
    
    def test_client_serialization_with_none_values(self):
        """Test: Serialización de Client con valores None."""
        client_data = {
            "id": 7,
            "name": "Minimal Client",
            "code": "MC-007",
            "contact_person": None,
            "email": None,
            "phone": None,
            "is_active": True,
            "notes": None,
            "created_at": datetime(2024, 1, 21, 10, 0, 0),
            "updated_at": datetime(2024, 1, 21, 11, 0, 0)
        }
        
        client = Client(**client_data)
        serialized = client.model_dump()
        
        # Verificar que los valores None se preservan en la serialización
        assert serialized["contact_person"] is None
        assert serialized["email"] is None
        assert serialized["phone"] is None
        assert serialized["notes"] is None
        assert serialized["is_active"] is True
    
    def test_client_serialization_exclude_none(self):
        """Test: Serialización de Client excluyendo valores None."""
        client_data = {
            "id": 8,
            "name": "Exclude None Client",
            "code": "ENC-008",
            "contact_person": None,
            "email": "exclude@none.com",
            "phone": None,
            "is_active": False,
            "notes": None,
            "created_at": datetime(2024, 1, 22, 14, 30, 0),
            "updated_at": datetime(2024, 1, 22, 15, 30, 0)
        }
        
        client = Client(**client_data)
        serialized = client.model_dump(exclude_none=True)
        
        # Verificar que los valores None fueron excluidos
        assert "contact_person" not in serialized
        assert "phone" not in serialized
        assert "notes" not in serialized
        # Verificar que los valores no-None están presentes
        assert serialized["email"] == "exclude@none.com"
        assert serialized["is_active"] is False
        assert "id" in serialized
        assert "name" in serialized
        assert "code" in serialized
    
    def test_client_round_trip_serialization(self):
        """Test: Serialización y deserialización completa (round-trip)."""
        original_data = {
            "id": 9,
            "name": "Round Trip Client",
            "code": "RTC-009",
            "contact_person": "Charlie Davis",
            "email": "charlie@roundtrip.com",
            "phone": "+9988776655",
            "is_active": True,
            "notes": "Testing round-trip serialization",
            "created_at": datetime(2024, 1, 23, 9, 15, 0),
            "updated_at": datetime(2024, 1, 23, 10, 15, 0)
        }
        
        # Crear cliente original
        original_client = Client(**original_data)
        
        # Serializar a JSON
        json_str = original_client.model_dump_json()
        
        # Deserializar desde JSON
        restored_client = Client.model_validate_json(json_str)
        
        # Verificar que el cliente restaurado es idéntico al original
        assert restored_client.id == original_client.id
        assert restored_client.name == original_client.name
        assert restored_client.code == original_client.code
        assert restored_client.contact_person == original_client.contact_person
        assert restored_client.email == original_client.email
        assert restored_client.phone == original_client.phone
        assert restored_client.is_active == original_client.is_active
        assert restored_client.notes == original_client.notes
        assert restored_client.created_at == original_client.created_at
        assert restored_client.updated_at == original_client.updated_at