"""Fixtures para los esquemas de Schedule."""

from typing import Any, Dict
from datetime import date, time, datetime

import pytest


@pytest.fixture
def valid_schedule_base_data() -> Dict[str, Any]:
    """Datos base válidos para Schedule.
    
    Returns:
        Dict[str, Any]: Diccionario con datos base de horario
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "team_id": None,
        "status_code_id": 1,
        "date": date(2024, 2, 15),
        "start_time": time(9, 0),
        "end_time": time(17, 0),
        "description": "Descripción de prueba",
        "location": "Oficina",
        "is_confirmed": False,
        "notes": "Trabajo en la tarea X."
    }


@pytest.fixture
def valid_schedule_create_data(valid_schedule_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para ScheduleCreate.
    
    Args:
        valid_schedule_base_data: Fixture con datos base de horario
        
    Returns:
        Dict[str, Any]: Diccionario con datos para crear un horario
    """
    data = valid_schedule_base_data.copy()
    data["date"] = "2024-02-16"
    data["start_time"] = "08:30"
    data["end_time"] = "16:30"
    return data


@pytest.fixture
def valid_schedule_update_data() -> Dict[str, Any]:
    """Datos válidos para ScheduleUpdate.
    
    Returns:
        Dict[str, Any]: Diccionario con datos para actualizar un horario
    """
    return {
        "employee_id": 2,
        "project_id": 2,
        "status_code_id": 2,
        "start_time": "10:00",
        "end_time": "18:00",
        "description": "Actualización de la descripción",
        "is_confirmed": True,
        "notes": "Reunión con el cliente."
    }


@pytest.fixture
def valid_schedule_data(valid_schedule_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para Schedule.
    
    Args:
        valid_schedule_base_data: Fixture con datos base de horario
        
    Returns:
        Dict[str, Any]: Diccionario con datos de horario
    """
    data = valid_schedule_base_data.copy()
    data["id"] = 1
    data["created_at"] = datetime(2024, 2, 1, 10, 0, 0)
    data["updated_at"] = datetime(2024, 2, 1, 10, 0, 0)
    return data


@pytest.fixture
def valid_schedule_search_filter_data() -> Dict[str, Any]:
    """Datos válidos para ScheduleSearchFilter.
    
    Returns:
        Dict[str, Any]: Diccionario con filtros de búsqueda de horario
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date_from": "2024-02-01",
        "date_to": "2024-02-29",
        "is_confirmed": True
    }


@pytest.fixture
def schedule_minimal_data() -> Dict[str, Any]:
    """Datos mínimos para crear un horario.
    
    Returns:
        Dict[str, Any]: Diccionario con datos mínimos de horario
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": date(2024, 2, 15),
    }


@pytest.fixture
def schedule_with_team_only() -> Dict[str, Any]:
    """Horario asignado solo a un equipo.
    
    Returns:
        Dict[str, Any]: Diccionario de horario con solo equipo
    """
    return {
        "employee_id": 1,
        "team_id": 1,
        "date": date(2024, 2, 15),
        "start_time": time(9, 0, 0),
        "end_time": time(17, 0, 0)
    }


@pytest.fixture
def schedule_without_times() -> Dict[str, Any]:
    """Horario sin horas de inicio/fin.
    
    Returns:
        Dict[str, Any]: Diccionario de horario sin tiempos
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": date(2024, 2, 15),
        "description": "Trabajo todo el día",
        "is_confirmed": True
    }


@pytest.fixture
def invalid_schedule_no_project_or_team() -> Dict[str, Any]:
    """Datos inválidos: sin proyecto ni equipo.
    
    Returns:
        Dict[str, Any]: Diccionario sin proyecto ni equipo
    """
    return {
        "employee_id": 1,
        "date": "2024-07-22",
        "hours": 8.0
    }


@pytest.fixture
def invalid_schedule_end_before_start() -> Dict[str, Any]:
    """Datos inválidos: hora de fin antes de hora de inicio.
    
    Returns:
        Dict[str, Any]: Diccionario con tiempos inválidos
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": "2024-07-22",
        "start_time": "17:00",
        "end_time": "09:00",
        "hours": 8.0
    }


@pytest.fixture
def invalid_schedule_only_start_time() -> Dict[str, Any]:
    """Datos inválidos: solo hora de inicio.
    
    Returns:
        Dict[str, Any]: Diccionario con solo hora de inicio
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": "2024-07-22",
        "start_time": "09:00",
        "hours": 8.0
    }


@pytest.fixture
def invalid_schedule_only_end_time() -> Dict[str, Any]:
    """Datos inválidos: solo hora de fin.
    
    Returns:
        Dict[str, Any]: Diccionario con solo hora de fin
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": "2024-07-22",
        "end_time": "17:00",
        "hours": 8.0
    }


@pytest.fixture
def invalid_schedule_long_location() -> Dict[str, Any]:
    """Datos inválidos: ubicación demasiado larga.
    
    Returns:
        Dict[str, Any]: Diccionario con ubicación muy larga
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": "2024-02-15",
        "location": "a" * 201  # Excede el límite de 200 caracteres
    }


@pytest.fixture(params=[
    {"start_time": "17:00", "end_time": "09:00"}, # end_time antes que start_time
    {"start_time": "09:00", "end_time": "09:00"}, # end_time igual a start_time
    {"start_time": "09:00"}, # Solo start_time sin end_time
    {"end_time": "17:00"}, # Solo end_time sin start_time
    {} # Sin project_id ni team_id
])
def schedule_edge_cases(request) -> Dict[str, Any]:
    """Casos límite para horarios que deberían fallar validación.
    
    Args:
        request: Fixture de pytest para parametrización
        
    Returns:
        Dict[str, Any]: Diccionario con caso límite de horario
    """
    base_data = {
        "employee_id": 1,
        "date": "2024-02-15"
    }
    # Solo agregar project_id si no es el caso que prueba la falta de project_id/team_id
    if request.param != {}:
        base_data["project_id"] = 1
    base_data.update(request.param)
    return base_data