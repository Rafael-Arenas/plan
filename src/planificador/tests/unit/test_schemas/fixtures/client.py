"""Fixtures para los esquemas de Client."""

from typing import Any, Dict, List
import uuid
import pytest


@pytest.fixture
def valid_client_base_data() -> Dict[str, Any]:
    """Datos válidos para ClientBase schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ClientBase
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "name": f"Test Client {unique_id}",
        "code": f"TC-{unique_id}",
        "contact_person": "John Doe",
        "email": f"contact-{unique_id.lower()}@testclient.com",
        "phone": "+1234567890",
        "is_active": True,
        "notes": "Cliente de prueba para testing de schemas"
    }


@pytest.fixture
def valid_client_create_data(valid_client_base_data) -> Dict[str, Any]:
    """Datos válidos para ClientCreate schema.
    
    Args:
        valid_client_base_data: Datos base del cliente
        
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ClientCreate
    """
    return valid_client_base_data.copy()


@pytest.fixture
def valid_client_update_data() -> Dict[str, Any]:
    """Datos válidos para ClientUpdate schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ClientUpdate
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    return {
        "name": f"Updated Client {unique_id}",
        "contact_person": "Jane Smith",
        "email": f"updated-{unique_id.lower()}@testclient.com",
        "is_active": False,
        "notes": "Cliente actualizado para testing"
    }


@pytest.fixture
def valid_client_data() -> Dict[str, Any]:
    """Datos válidos para Client schema (con campos de BD).
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para Client
    """
    unique_id = str(uuid.uuid4())[:8].upper()
    now = "2024-01-01T10:00:00"
    return {
        "id": 1,
        "name": f"Test Client {unique_id}",
        "code": f"TC-{unique_id}",
        "contact_person": "John Doe",
        "email": f"contact-{unique_id.lower()}@testclient.com",
        "phone": "+1234567890",
        "is_active": True,
        "notes": "Cliente de prueba para testing",
        "created_at": now,
        "updated_at": now
    }


@pytest.fixture
def valid_client_with_projects_data(valid_client_data) -> Dict[str, Any]:
    """Datos válidos para ClientWithProjects schema.
    
    Args:
        valid_client_data: Datos base del cliente
        
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ClientWithProjects
    """
    data = valid_client_data.copy()
    data["projects"] = []
    return data


@pytest.fixture
def invalid_client_empty_name() -> Dict[str, Any]:
    """Datos inválidos: nombre vacío.
    
    Returns:
        Dict[str, Any]: Diccionario con nombre vacío
    """
    return {
        "name": "",  # Nombre vacío - inválido
        "code": "TC-12345",
        "email": "test@example.com"
    }


@pytest.fixture
def invalid_client_short_code() -> Dict[str, Any]:
    """Datos inválidos: código muy corto.
    
    Returns:
        Dict[str, Any]: Diccionario con código muy corto
    """
    return {
        "name": "Test Client",
        "code": "",  # Código vacío - inválido
        "email": "test@example.com"
    }


@pytest.fixture
def invalid_client_email() -> Dict[str, Any]:
    """Datos inválidos: email con formato incorrecto.
    
    Returns:
        Dict[str, Any]: Diccionario con email inválido
    """
    return {
        "name": "Test Client",
        "code": "TC-12345",
        "email": "invalid-email-format"  # Email inválido
    }


@pytest.fixture
def invalid_client_long_name() -> Dict[str, Any]:
    """Datos inválidos: nombre excede longitud máxima.
    
    Returns:
        Dict[str, Any]: Diccionario con nombre muy largo
    """
    return {
        "name": "A" * 101,  # Excede max_length=100
        "code": "TC-12345",
        "email": "test@example.com"
    }


@pytest.fixture
def invalid_client_long_code() -> Dict[str, Any]:
    """Datos inválidos: código excede longitud máxima.
    
    Returns:
        Dict[str, Any]: Diccionario con código muy largo
    """
    return {
        "name": "Test Client",
        "code": "A" * 21,  # Excede max_length=20
        "email": "test@example.com"
    }


@pytest.fixture
def invalid_client_long_phone() -> Dict[str, Any]:
    """Datos inválidos: teléfono excede longitud máxima.
    
    Returns:
        Dict[str, Any]: Diccionario con teléfono muy largo
    """
    return {
        "name": "Test Client",
        "code": "TC-12345",
        "phone": "1" * 21,  # Excede max_length=20
        "email": "test@example.com"
    }


@pytest.fixture
def invalid_client_long_notes() -> Dict[str, Any]:
    """Datos inválidos: notas exceden longitud máxima.
    
    Returns:
        Dict[str, Any]: Diccionario con notas muy largas
    """
    return {
        "name": "Test Client",
        "code": "TC-12345",
        "notes": "A" * 501,  # Excede max_length=500
        "email": "test@example.com"
    }


@pytest.fixture
def minimal_client_data() -> Dict[str, Any]:
    """Datos mínimos requeridos para crear un cliente.
    
    Returns:
        Dict[str, Any]: Diccionario con campos mínimos requeridos
    """
    return {
        "name": "A",  # Mínimo: 1 carácter
        "code": "A"   # Mínimo: 1 carácter
    }


@pytest.fixture
def maximal_client_data() -> Dict[str, Any]:
    """Datos con longitudes máximas permitidas.
    
    Returns:
        Dict[str, Any]: Diccionario con campos en longitud máxima
    """
    return {
        "name": "A" * 100,  # Máximo: 100 caracteres
        "code": "A" * 20,   # Máximo: 20 caracteres
        "contact_person": "B" * 100,  # Máximo: 100 caracteres
        "email": "test@example.com",
        "phone": "1" * 20,   # Máximo: 20 caracteres
        "is_active": True,
        "notes": "C" * 500  # Máximo: 500 caracteres
    }


@pytest.fixture
def client_data_with_none_optionals() -> Dict[str, Any]:
    """Datos con campos opcionales como None.
    
    Returns:
        Dict[str, Any]: Diccionario con campos opcionales en None
    """
    return {
        "name": "Test Client",
        "code": "TC-12345",
        "contact_person": None,
        "email": None,
        "phone": None,
        "notes": None
    }


@pytest.fixture
def multiple_valid_clients_data() -> List[Dict[str, Any]]:
    """Lista de múltiples datos válidos de clientes.
    
    Returns:
        List[Dict[str, Any]]: Lista con datos de múltiples clientes
    """
    return [
        {
            "name": f"Client {i}",
            "code": f"TC-{i:03d}",
            "contact_person": f"Contact {i}",
            "email": f"client{i}@test.com",
            "phone": f"+123456789{i}",
            "is_active": i % 2 == 0,  # Alternar activo/inactivo
            "notes": f"Notas del cliente {i}"
        }
        for i in range(1, 4)
    ]


@pytest.fixture(params=[
    "test@example.com",
    "test.name@example.co.uk", 
    "test_123@sub.example.com",
    "user+tag@domain.org",  # 4 emails válidos
    "invalid-email",  # Sin @
    "@domain.com",  # Sin parte local
    "user@",  # Sin dominio
    "user..name@domain.com",  # Doble punto
    ""  # Email vacío
])
def email_variations(request) -> str:
    """Variaciones de correos electrónicos válidos e inválidos.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        str: Correo electrónico para testing
    """
    return request.param