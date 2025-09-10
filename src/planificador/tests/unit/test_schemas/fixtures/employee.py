"""Fixtures para los esquemas de Employee."""

from typing import Any, Dict
from datetime import date, datetime

import pytest


@pytest.fixture
def valid_employee_base_data() -> Dict[str, Any]:
    """Datos base válidos para Employee.
    
    Returns:
        Dict[str, Any]: Diccionario con datos base de empleado
    """
    return {
        "first_name": "Juan",
        "last_name": "Pérez",
        "employee_code": "EMP-001",
        "email": "juan.perez@example.com",
        "phone": "123456789",
        "position": "Desarrollador",
        "department": "Tecnología",
        "hire_date": date(2023, 1, 15),
        "status": "active"
    }


@pytest.fixture
def valid_employee_create_data(valid_employee_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para EmployeeCreate.
    
    Args:
        valid_employee_base_data: Fixture con datos base de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con datos para crear un empleado
    """
    data = valid_employee_base_data.copy()
    data["hire_date"] = "2023-01-15"
    return data


@pytest.fixture
def valid_employee_update_data() -> Dict[str, Any]:
    """Datos válidos para EmployeeUpdate.
    
    Returns:
        Dict[str, Any]: Diccionario con datos para actualizar un empleado
    """
    return {
        "first_name": "Juan",
        "last_name": "Pérez",
        "email": "juan.perez@empresa.com",
        "phone": "+56912345678",
        "position": "Senior Developer",
        "department": "Desarrollo",
        "status": "active"
    }


@pytest.fixture
def valid_employee_data(valid_employee_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para Employee.
    
    Args:
        valid_employee_base_data: Fixture con datos base de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con datos de empleado
    """
    data = valid_employee_base_data.copy()
    data["id"] = 1
    data["created_at"] = datetime(2023, 1, 15, 9, 0, 0)
    data["updated_at"] = datetime(2023, 1, 15, 9, 0, 0)
    return data


@pytest.fixture
def invalid_employee_empty_first_name(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: nombre vacío.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con nombre vacío
    """
    data = valid_employee_create_data.copy()
    data["first_name"] = ""
    return data


@pytest.fixture
def invalid_employee_empty_last_name(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: apellido vacío.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con apellido vacío
    """
    data = valid_employee_create_data.copy()
    data["last_name"] = ""
    return data


@pytest.fixture
def invalid_employee_empty_code(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: código vacío.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con código vacío
    """
    data = valid_employee_create_data.copy()
    data["employee_code"] = ""
    return data


@pytest.fixture
def invalid_employee_invalid_email(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: email incorrecto.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con email inválido
    """
    data = valid_employee_create_data.copy()
    data["email"] = "email-invalido"
    return data


@pytest.fixture
def invalid_employee_long_first_name(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: nombre demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con nombre muy largo
    """
    data = valid_employee_create_data.copy()
    data["first_name"] = "a" * 51
    return data


@pytest.fixture
def invalid_employee_long_last_name(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: apellido demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con apellido muy largo
    """
    data = valid_employee_create_data.copy()
    data["last_name"] = "a" * 51
    return data


@pytest.fixture
def invalid_employee_long_code(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: código demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con código muy largo
    """
    data = valid_employee_create_data.copy()
    data["employee_code"] = "a" * 21
    return data


@pytest.fixture
def invalid_employee_long_phone(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: teléfono demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con teléfono muy largo
    """
    data = valid_employee_create_data.copy()
    data["phone"] = "1" * 21
    return data


@pytest.fixture
def invalid_employee_long_position(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: cargo demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con cargo muy largo
    """
    data = valid_employee_create_data.copy()
    data["position"] = "a" * 101
    return data


@pytest.fixture
def invalid_employee_long_department(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: departamento demasiado largo.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con departamento muy largo
    """
    data = valid_employee_create_data.copy()
    data["department"] = "a" * 101
    return data


@pytest.fixture
def minimal_employee_data() -> Dict[str, Any]:
    """Datos mínimos para crear un empleado.
    
    Returns:
        Dict[str, Any]: Diccionario con datos mínimos de empleado
    """
    return {
        "first_name": "Ana",
        "last_name": "García",
        "employee_code": "EMP-002",
        "email": "ana.garcia@example.com",
        "hire_date": "2023-02-01"
    }


@pytest.fixture
def maximal_employee_data() -> Dict[str, Any]:
    """Datos máximos para crear un empleado.
    
    Returns:
        Dict[str, Any]: Diccionario con todos los campos de empleado
    """
    return {
        "first_name": "Maximiliano",
        "last_name": "De la Cruz y Rodríguez",
        "employee_code": "EMP-MAX-001-EXT",
        "email": "maximiliano.delacruzyrodriguez@example.com",
        "phone": "+34-91-123-4567-890",
        "position": "Director General de Operaciones y Estrategia Corporativa Global",
        "department": "Alta Dirección y Gestión Estratégica de Proyectos Internacionales",
        "hire_date": "2020-01-01",
        "status": "active"
    }


@pytest.fixture
def employee_data_with_none_optionals(valid_employee_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos de empleado con campos opcionales como None.
    
    Args:
        valid_employee_create_data: Fixture con datos válidos de empleado
        
    Returns:
        Dict[str, Any]: Diccionario con campos opcionales como None
    """
    data = valid_employee_create_data.copy()
    data["phone"] = None
    data["position"] = None
    data["department"] = None
    return data


@pytest.fixture(params=["active", "on_leave", "terminated"])
def employee_status_variations(request) -> str:
    """Variaciones de estados de empleado.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        str: Estado de empleado válido
    """
    return request.param


@pytest.fixture
def multiple_valid_employees_data() -> list[Dict[str, Any]]:
    """Lista de varios empleados válidos.
    
    Returns:
        list[Dict[str, Any]]: Lista de diccionarios de empleados
    """
    return [
        {
            "first_name": "Carlos",
            "last_name": "Ruiz",
            "code": "EMP-003",
            "email": "carlos.ruiz@example.com",
            "hire_date": "2023-03-01"
        },
        {
            "first_name": "Laura",
            "last_name": "Gómez",
            "code": "EMP-004",
            "email": "laura.gomez@example.com",
            "hire_date": "2023-04-01"
        }
    ]