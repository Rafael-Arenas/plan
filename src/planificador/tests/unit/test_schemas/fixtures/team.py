"""Fixtures para los esquemas de Team."""

from typing import Any, Dict, List
from datetime import date, datetime

import pytest


from planificador.schemas.team import TeamMembership


@pytest.fixture
def valid_team_base_data() -> dict[str, Any]:
    """Datos válidos para TeamBase schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para TeamBase
    """
    return {
        "name": "Equipo de Desarrollo",
        "code": "DEV-01",
        "description": "Equipo de desarrollo principal",
        "description": "Equipo de desarrollo principal",
        "color_hex": "#4A90E2",
        "max_members": 10,
        "is_active": True,
        "notes": "Notas para el equipo",
        "notes": "Este es un equipo de prueba"
    }


@pytest.fixture
def valid_team_data() -> Dict[str, Any]:
    """Datos válidos para Team schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para Team
    """
    return {
        "name": "Equipo de Desarrollo",
        "code": "DEV-01",
        "description": "Equipo de desarrollo principal",
        "color_hex": "#4A90E2",
        "max_members": 10,
        "is_active": True,
        "notes": "Notas para el equipo de desarrollo"
    }


@pytest.fixture
def valid_team_create_data(valid_team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para TeamCreate schema.
    
    Args:
        valid_team_data: Fixture con datos base de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para TeamCreate
    """
    return valid_team_data.copy()


@pytest.fixture
def valid_team_update_data() -> Dict[str, Any]:
    """Datos válidos para TeamUpdate schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para TeamUpdate
    """
    return {
        "name": "Equipo de Desarrollo Avanzado",
        "description": "Nueva descripción",
        "color_hex": "#D0021B",
        "max_members": 15,
        "is_active": True,
        "notes": "Notas de actualización"
    }


@pytest.fixture
def valid_team_membership_base_data() -> Dict[str, Any]:
    """Datos base válidos para TeamMembership.
    
    Returns:
        Dict[str, Any]: Diccionario con datos base de membresía
    """
    return {
        "team_id": 1,
        "employee_id": 1,
        "role": "member",
        "start_date": date(2024, 1, 1),
        "is_active": True,
        "end_date": None,
    }


@pytest.fixture
def valid_team_membership_create_data(valid_team_membership_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para TeamMembershipCreate.
    
    Args:
        valid_team_membership_base_data: Fixture con datos base de membresía
        
    Returns:
        Dict[str, Any]: Diccionario con datos para crear una membresía
    """
    data = valid_team_membership_base_data.copy()
    data["is_active"] = True
    data["start_date"] = date(2024, 1, 1)
    return data


@pytest.fixture
def valid_team_membership_data(valid_team_membership_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para TeamMembership.
    
    Args:
        valid_team_membership_base_data: Fixture con datos base de membresía
        
    Returns:
        Dict[str, Any]: Diccionario con datos de membresía
    """
    data = valid_team_membership_base_data.copy()
    data["id"] = 1
    data["created_at"] = datetime(2024, 1, 1, 10, 0, 0)
    data["updated_at"] = datetime(2024, 1, 1, 10, 0, 0)
    return data


@pytest.fixture
def valid_team_with_members_data(valid_team_data: Dict[str, Any], valid_team_membership_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos de un equipo con miembros.
    
    Args:
        valid_team_data: Fixture con datos de equipo
        valid_team_membership_data: Fixture con datos de membresía
        
    Returns:
        Dict[str, Any]: Diccionario de equipo con lista de miembros
    """
    team_data = valid_team_data.copy()
    team_data["id"] = 1
    team_data["created_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["updated_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["memberships"] = [TeamMembership(**valid_team_membership_data)]
    return team_data


@pytest.fixture
def valid_team_complete_data(valid_team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para Team schema completo con campos requeridos.
    
    Args:
        valid_team_data: Fixture con datos base de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con datos completos para Team
    """
    team_data = valid_team_data.copy()
    team_data["id"] = 1
    team_data["created_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["updated_at"] = datetime(2024, 1, 1, 10, 0, 0)
    return team_data


@pytest.fixture
def valid_team_with_schedules_data(valid_team_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos de un equipo con planificaciones.
    
    Args:
        valid_team_data: Fixture con datos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario de equipo con lista de planificaciones
    """
    team_data = valid_team_data.copy()
    team_data["id"] = 1
    team_data["created_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["updated_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["schedules"] = []
    return team_data


@pytest.fixture
def valid_team_with_details_data(valid_team_with_members_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos de un equipo con detalles completos.
    
    Args:
        valid_team_with_members_data: Fixture con datos de equipo y miembros
        
    Returns:
        Dict[str, Any]: Diccionario de equipo con detalles completos
    """
    team_data = valid_team_with_members_data.copy()
    team_data["schedules"] = []
    team_data["created_at"] = datetime(2024, 1, 1, 10, 0, 0)
    team_data["updated_at"] = datetime(2024, 1, 1, 10, 0, 0)
    return team_data


@pytest.fixture
def invalid_team_empty_name(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: nombre de equipo vacío.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con nombre de equipo vacío
    """
    data = valid_team_create_data.copy()
    data["name"] = ""
    return data


@pytest.fixture
def invalid_team_long_name(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: nombre de equipo muy largo.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con nombre de equipo muy largo
    """
    data = valid_team_create_data.copy()
    data["name"] = "a" * 101
    return data


@pytest.fixture
def invalid_team_long_code(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: código de equipo muy largo.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con código de equipo muy largo
    """
    data = valid_team_create_data.copy()
    data["code"] = "a" * 21
    return data


@pytest.fixture
def invalid_team_color_hex(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: color hexadecimal incorrecto.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con color hexadecimal inválido
    """
    data = valid_team_create_data.copy()
    data["color_hex"] = "#12345G"
    return data


@pytest.fixture
def invalid_team_max_members_low(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: número máximo de miembros demasiado bajo.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con max_members inválido
    """
    data = valid_team_create_data.copy()
    data["max_members"] = 0
    return data


@pytest.fixture
def invalid_team_max_members_high(valid_team_create_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos inválidos: número máximo de miembros demasiado alto.
    
    Args:
        valid_team_create_data: Fixture con datos válidos de equipo
        
    Returns:
        Dict[str, Any]: Diccionario con max_members inválido
    """
    data = valid_team_create_data.copy()
    data["max_members"] = 101
    return data


@pytest.fixture
def invalid_team_membership_dates() -> Dict[str, Any]:
    """Datos inválidos: fecha de fin anterior a la de inicio.
    
    Returns:
        Dict[str, Any]: Diccionario con fechas de membresía inválidas
    """
    return {
        "team_id": 1,
        "employee_id": 1,
        "role": "member",
        "start_date": "2030-01-01",
        "end_date": "2030-12-31"
    }


@pytest.fixture
def invalid_team_membership_old_start_date() -> Dict[str, Any]:
    """Datos inválidos: fecha de inicio muy antigua.
    
    Returns:
        Dict[str, Any]: Diccionario con fecha de inicio inválida
    """
    return {
        "team_id": 1,
        "employee_id": 1,
        "role": "member",
        "start_date": "2010-01-01"
    }


@pytest.fixture
def invalid_team_membership_future_start_date() -> Dict[str, Any]:
    """Datos inválidos: fecha de inicio muy futura.
    
    Returns:
        Dict[str, Any]: Diccionario con fecha de inicio inválida
    """
    return {
        "team_id": 1,
        "employee_id": 1,
        "role": "member",
        "start_date": "2100-01-01"
    }


@pytest.fixture
def invalid_team_membership_future_end_date() -> Dict[str, Any]:
    """Datos inválidos: fecha de fin muy futura.
    
    Returns:
        Dict[str, Any]: Diccionario con fecha de fin inválida
    """
    return {
        "team_id": 1,
        "employee_id": 1,
        "role": "lead",
        "start_date": "2024-01-01",
        "end_date": "2040-01-01"  # Más de 10 años en el futuro
    }


@pytest.fixture
def minimal_team_data() -> Dict[str, Any]:
    """Datos mínimos para crear un equipo.
    
    Returns:
        Dict[str, Any]: Diccionario con datos mínimos de equipo
    """
    return {
        "name": "Equipo Mínimo"
    }


@pytest.fixture
def maximal_team_data() -> Dict[str, Any]:
    """Datos máximos para crear un equipo.
    
    Returns:
        Dict[str, Any]: Diccionario con todos los campos de equipo
    """
    return {
        "name": "Equipo Completo con Todos los Detalles Posibles y un Nombre Muy Largo",
        "code": "MAX-TEAM-CODE-001",
        "description": "Descripción máxima",
        "color_hex": "#BD10E0",
        "max_members": 100,
        "is_active": False,
        "notes": "Notas para el equipo maximal"
    }


@pytest.fixture(params=["#FFFFFF", "#000000", "#FF5733"])
def valid_color_hex_values(request) -> str:
    """Valores válidos de colores hexadecimales.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        str: Valor de color hexadecimal válido
    """
    return request.param


@pytest.fixture(params=["#12345G", "#FFF", "123456"])
def invalid_color_hex_values(request) -> str:
    """Valores inválidos de colores hexadecimales.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        str: Valor de color hexadecimal inválido
    """
    return request.param


@pytest.fixture(params=["developer", "leader", "coordinator"])
def membership_role_values(request) -> str:
    """Valores válidos para roles de membresía.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        str: Rol de membresía válido
    """
    return request.param