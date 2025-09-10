"""Fixtures para los esquemas de Workload."""

from typing import Any, Dict
from datetime import date, datetime
from decimal import Decimal

import pytest


@pytest.fixture
def valid_workload_base_data() -> Dict[str, Any]:
    """Datos base válidos para Workload.
    
    Returns:
        Dict[str, Any]: Diccionario con datos base de carga de trabajo
    """
    test_date = date(2024, 2, 15)  # Jueves de la semana 7
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,  # Semana 7 de 2024
        "month": 2,  # Febrero
        "year": 2024,
        "planned_hours": Decimal("8.0"),
        "actual_hours": Decimal("8.5"),
        "utilization_percentage": Decimal("93.75"),  # 7.5/8 * 100
        "efficiency_score": Decimal("94.12"),  # 8/8.5 * 100
        "productivity_index": Decimal("85.0"),
        "is_billable": True,
        "notes": "Trabajo en desarrollo de funcionalidad X"
    }


@pytest.fixture
def valid_workload_create_data(valid_workload_base_data: Dict[str, Any]) -> Dict[str, Any]:
    """Datos válidos para WorkloadCreate.
    
    Args:
        valid_workload_base_data: Fixture con datos base de carga de trabajo
        
    Returns:
        Dict[str, Any]: Diccionario con datos para crear una carga de trabajo
    """
    return valid_workload_base_data.copy()


@pytest.fixture
def valid_workload_data() -> Dict[str, Any]:
    """Datos válidos para Workload completo (con ID y timestamps).
    
    Returns:
        Dict[str, Any]: Diccionario con datos completos de carga de trabajo
    """
    test_date = date(2024, 2, 15)
    now = datetime(2024, 2, 15, 10, 30, 0)
    
    return {
        "id": 1,
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2024,
        "planned_hours": Decimal("8.0"),
        "actual_hours": Decimal("8.0"),
        "utilization_percentage": Decimal("100.0"),
        "efficiency_score": Decimal("100.0"),
        "productivity_index": Decimal("90.0"),
        "is_billable": True,
        "notes": "Trabajo completado según planificación",
        "created_at": now,
        "updated_at": now
    }


@pytest.fixture
def workload_minimal_data() -> Dict[str, Any]:
    """Datos mínimos requeridos para Workload.
    
    Returns:
        Dict[str, Any]: Diccionario con datos mínimos
    """
    test_date = date(2024, 3, 10)  # Domingo de la semana 10
    return {
        "employee_id": 1,
        "date": test_date,
        "week_number": 10,
        "month": 3,
        "year": 2024
    }


@pytest.fixture
def workload_without_project() -> Dict[str, Any]:
    """Datos de Workload sin proyecto específico.
    
    Returns:
        Dict[str, Any]: Diccionario sin project_id
    """
    test_date = date(2024, 4, 5)  # Viernes de la semana 14
    return {
        "employee_id": 1,
        "project_id": None,
        "date": test_date,
        "week_number": 14,
        "month": 4,
        "year": 2024,
        "planned_hours": Decimal("4.0"),
        "actual_hours": Decimal("3.5"),
        "is_billable": False,
        "notes": "Tiempo administrativo"
    }


@pytest.fixture
def workload_with_high_efficiency() -> Dict[str, Any]:
    """Datos de Workload con alta eficiencia.
    
    Returns:
        Dict[str, Any]: Diccionario con métricas de alta eficiencia
    """
    test_date = date(2024, 5, 20)  # Lunes de la semana 21
    return {
        "employee_id": 2,
        "project_id": 2,
        "date": test_date,
        "week_number": 21,
        "month": 5,
        "year": 2024,
        "planned_hours": Decimal("6.0"),
        "actual_hours": Decimal("6.0"),
        "utilization_percentage": Decimal("100.0"),
        "efficiency_score": Decimal("100.0"),  # 6/6 * 100
        "productivity_index": Decimal("95.0"),
        "is_billable": True
    }


@pytest.fixture
def workload_boundary_values() -> Dict[str, Any]:
    """Datos de Workload con valores en los límites.
    
    Returns:
        Dict[str, Any]: Diccionario con valores límite
    """
    test_date = date(2024, 12, 30)  # Lunes de la semana 53
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 53,  # Máximo
        "month": 12,  # Máximo
        "year": 2024,
        "planned_hours": Decimal("24.0"),  # Máximo
        "actual_hours": Decimal("24.0"),  # Máximo
        "utilization_percentage": Decimal("100.0"),  # Máximo
        "efficiency_score": Decimal("100.0"),  # Máximo
        "productivity_index": Decimal("100.0"),  # Máximo
        "is_billable": True
    }


@pytest.fixture
def workload_zero_hours() -> Dict[str, Any]:
    """Datos de Workload con cero horas.
    
    Returns:
        Dict[str, Any]: Diccionario con horas en cero
    """
    test_date = date(2024, 1, 1)  # Lunes de la semana 1
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 1,
        "month": 1,
        "year": 2024,
        "planned_hours": Decimal("0.0"),
        "actual_hours": Decimal("0.0"),
        "utilization_percentage": Decimal("0.0"),
        "efficiency_score": Decimal("0.0"),
        "productivity_index": Decimal("0.0"),
        "is_billable": False,
        "notes": "Día festivo"
    }


# Fixtures para datos inválidos
@pytest.fixture
def invalid_workload_inconsistent_date() -> Dict[str, Any]:
    """Datos de Workload con fecha inconsistente.
    
    Returns:
        Dict[str, Any]: Diccionario con fecha que no coincide con año/mes
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": date(2024, 2, 15),  # Febrero 2024
        "week_number": 7,
        "month": 3,  # Inconsistente: dice marzo pero fecha es febrero
        "year": 2024
    }


@pytest.fixture
def invalid_workload_year_mismatch() -> Dict[str, Any]:
    """Datos de Workload con año inconsistente.
    
    Returns:
        Dict[str, Any]: Diccionario con año que no coincide con la fecha
    """
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": date(2024, 2, 15),
        "week_number": 7,
        "month": 2,
        "year": 2023  # Inconsistente: dice 2023 pero fecha es 2024
    }


@pytest.fixture
def invalid_workload_excessive_hours() -> Dict[str, Any]:
    """Datos de Workload con horas reales excesivas.
    
    Returns:
        Dict[str, Any]: Diccionario con horas reales > 2x planificadas
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2024,
        "planned_hours": Decimal("4.0"),
        "actual_hours": Decimal("9.0"),  # Más del doble de las planificadas
    }


@pytest.fixture
def invalid_workload_inconsistent_efficiency() -> Dict[str, Any]:
    """Datos de Workload con eficiencia inconsistente.
    
    Returns:
        Dict[str, Any]: Diccionario con efficiency_score inconsistente
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2024,
        "planned_hours": Decimal("8.0"),
        "actual_hours": Decimal("10.0"),  # Eficiencia real = 80%
        "efficiency_score": Decimal("95.0"),  # Pero dice 95% (inconsistente)
    }


@pytest.fixture
def invalid_workload_negative_hours() -> Dict[str, Any]:
    """Datos de Workload con horas negativas.
    
    Returns:
        Dict[str, Any]: Diccionario con horas negativas
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2024,
        "planned_hours": Decimal("-2.0"),  # Negativo
        "actual_hours": Decimal("-1.0"),   # Negativo
    }


@pytest.fixture
def invalid_workload_excessive_percentage() -> Dict[str, Any]:
    """Datos de Workload con porcentajes excesivos.
    
    Returns:
        Dict[str, Any]: Diccionario con porcentajes > 100
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2024,
        "utilization_percentage": Decimal("150.0"),  # > 100
        "efficiency_score": Decimal("200.0"),        # > 100
        "productivity_index": Decimal("120.0"),      # > 100
    }


@pytest.fixture
def invalid_workload_out_of_range_week() -> Dict[str, Any]:
    """Datos de Workload con semana fuera de rango.
    
    Returns:
        Dict[str, Any]: Diccionario con week_number inválido
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 54,  # > 53
        "month": 2,
        "year": 2024
    }


@pytest.fixture
def invalid_workload_out_of_range_month() -> Dict[str, Any]:
    """Datos de Workload con mes fuera de rango.
    
    Returns:
        Dict[str, Any]: Diccionario con month inválido
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 13,  # > 12
        "year": 2024
    }


@pytest.fixture
def invalid_workload_out_of_range_year() -> Dict[str, Any]:
    """Datos de Workload con año fuera de rango.
    
    Returns:
        Dict[str, Any]: Diccionario con year inválido
    """
    test_date = date(2024, 2, 15)
    return {
        "employee_id": 1,
        "project_id": 1,
        "date": test_date,
        "week_number": 7,
        "month": 2,
        "year": 2051  # > 2050
    }