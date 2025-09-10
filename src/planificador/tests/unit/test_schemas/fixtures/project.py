"""Fixtures para los esquemas de Project."""

from typing import Any, Dict
from datetime import datetime

import pytest


@pytest.fixture
def valid_project_data() -> Dict[str, Any]:
    """Datos válidos para Project schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para Project
    """
    return {
        "name": "Sistema de Gestión",
        "reference": "SGT-2024-001",
        "trigram": "SGT",
        "details": "Desarrollo de sistema de gestión empresarial",
        "status": "planned",
        "priority": "medium",
        "start_date": "2024-02-01",
        "end_date": "2024-12-31",
        "client_id": 1
    }


@pytest.fixture
def valid_project_create_data(valid_project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para ProjectCreate schema.
    
    Args:
        valid_project_data: Fixture con datos base de proyecto
        
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ProjectCreate
    """
    return valid_project_data.copy()


@pytest.fixture
def valid_project_update_data() -> Dict[str, Any]:
    """Datos válidos para ProjectUpdate schema.
    
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ProjectUpdate
    """
    return {
        "name": "Sistema de Gestión Actualizado",
        "details": "Sistema actualizado con nuevas funcionalidades",
        "status": "in_progress",
        "priority": "high"
    }


@pytest.fixture
def valid_project_with_assignments_data(valid_project_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para ProjectWithAssignments schema.
    
    Args:
        valid_project_data: Fixture con datos base de proyecto
        
    Returns:
        Dict[str, Any]: Diccionario con datos válidos para ProjectWithAssignments
    """
    data = valid_project_data.copy()
    data["id"] = 1
    data["created_at"] = datetime(2024, 1, 15, 10, 0, 0)
    data["updated_at"] = datetime(2024, 1, 15, 11, 0, 0)
    data["client"] = {
        "id": 1,
        "name": "Cliente Test",
        "code": "CT-001",
        "contact_person": "Juan Pérez",
        "email": "juan@cliente.com",
        "is_active": True,
        "created_at": datetime(2024, 1, 10, 9, 0, 0),
        "updated_at": datetime(2024, 1, 10, 9, 0, 0)
    }
    data["assignments"] = []
    return data

@pytest.fixture
def invalid_project_empty_name() -> Dict[str, Any]:
    """Datos inválidos: nombre vacío.
    
    Returns:
        Dict[str, Any]: Diccionario con nombre vacío
    """
    return {
        "name": "",
        "trigram": "INV",
        "client_id": 1
    }


@pytest.fixture
def invalid_project_short_trigram() -> Dict[str, Any]:
    """Datos inválidos: trigram muy corto.
    
    Returns:
        Dict[str, Any]: Diccionario con trigram muy corto
    """
    return {
        "name": "Proyecto Inválido",
        "trigram": "I",
        "client_id": 1
    }


@pytest.fixture
def invalid_project_status() -> Dict[str, Any]:
    """Datos inválidos: status no permitido.
    
    Returns:
        Dict[str, Any]: Diccionario con status inválido
    """
    return {
        "name": "Proyecto Inválido",
        "trigram": "INV",
        "status": "invalid_status",
        "client_id": 1
    }


@pytest.fixture
def invalid_project_priority() -> Dict[str, Any]:
    """Datos inválidos: prioridad no permitida.
    
    Returns:
        Dict[str, Any]: Diccionario con prioridad inválida
    """
    return {
        "name": "Proyecto Inválido",
        "trigram": "INV",
        "priority": "invalid_priority",
        "client_id": 1
    }


@pytest.fixture
def invalid_project_date_order() -> Dict[str, Any]:
    """Datos inválidos: fecha de fin antes de fecha de inicio.
    
    Returns:
        Dict[str, Any]: Diccionario con fechas inválidas
    """
    return {
        "name": "Proyecto Inválido",
        "trigram": "INV",
        "start_date": "2024-12-31",
        "end_date": "2024-01-01",
        "client_id": 1
    }


@pytest.fixture
def invalid_project_long_name() -> Dict[str, Any]:
    """Datos inválidos: nombre excede longitud máxima.
    
    Returns:
        Dict[str, Any]: Diccionario con nombre muy largo
    """
    return {
        "name": "A" * 101,
        "trigram": "INV",
        "client_id": 1
    }