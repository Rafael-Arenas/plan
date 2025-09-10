# src/planificador/tests/unit/test_schemas/fixtures/alert.py

import pytest
from datetime import datetime
from typing import Dict, Any
import pendulum

from planificador.models.alert import AlertType, AlertStatus


# Fixtures para datos válidos
@pytest.fixture
def valid_alert_data() -> Dict[str, Any]:
    """Datos válidos para crear una alerta."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "status": AlertStatus.NEW,
        "title": "Conflicto de horario",
        "message": "Se ha detectado un conflicto en la programación del empleado",
        "related_entity_type": "schedule",
        "related_entity_id": 123,
        "is_read": False,
        "read_at": None
    }


@pytest.fixture
def minimal_alert_data() -> Dict[str, Any]:
    """Datos mínimos requeridos para crear una alerta."""
    return {
        "user_id": 1,
        "alert_type": AlertType.SYSTEM_ERROR,
        "title": "Error del sistema",
        "message": "Ha ocurrido un error en el sistema"
    }


@pytest.fixture
def complete_alert_data() -> Dict[str, Any]:
    """Datos completos para una alerta (incluyendo campos de respuesta)."""
    now = pendulum.now()
    return {
        "id": 1,
        "user_id": 1,
        "alert_type": AlertType.DEADLINE_WARNING,
        "status": AlertStatus.READ,
        "title": "Advertencia de fecha límite",
        "message": "El proyecto está próximo a su fecha límite",
        "related_entity_type": "project",
        "related_entity_id": 456,
        "is_read": True,
        "read_at": now.subtract(hours=1),
        "created_at": now.subtract(days=1),
        "updated_at": now.subtract(hours=1)
    }


@pytest.fixture
def read_alert_data() -> Dict[str, Any]:
    """Datos para una alerta leída."""
    read_time = pendulum.now().subtract(hours=2)
    return {
        "user_id": 2,
        "alert_type": AlertType.APPROVAL_PENDING,
        "status": AlertStatus.READ,
        "title": "Aprobación pendiente",
        "message": "Hay una solicitud pendiente de aprobación",
        "is_read": True,
        "read_at": read_time
    }


@pytest.fixture
def unread_alert_data() -> Dict[str, Any]:
    """Datos para una alerta no leída."""
    return {
        "user_id": 3,
        "alert_type": AlertType.VACATION_CONFLICT,
        "status": AlertStatus.NEW,
        "title": "Conflicto de vacaciones",
        "message": "Se ha detectado un conflicto en las fechas de vacaciones",
        "is_read": False,
        "read_at": None
    }


# Fixtures para datos inválidos
@pytest.fixture
def invalid_alert_data() -> Dict[str, Any]:
    """Datos inválidos para crear una alerta."""
    return {
        "user_id": "invalid",  # Debe ser int
        "alert_type": "invalid_type",  # Debe ser AlertType
        "title": "",  # No puede estar vacío
        "message": "",  # No puede estar vacío
    }


@pytest.fixture
def invalid_title_data() -> Dict[str, Any]:
    """Datos con título inválido."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "title": "x" * 201,  # Excede el límite de 200 caracteres
        "message": "Mensaje válido"
    }


@pytest.fixture
def invalid_read_consistency_data() -> Dict[str, Any]:
    """Datos con inconsistencia en estado de lectura."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "title": "Título válido",
        "message": "Mensaje válido",
        "is_read": True,
        "read_at": None  # Inconsistente: marcada como leída pero sin fecha
    }


@pytest.fixture
def invalid_future_read_at_data() -> Dict[str, Any]:
    """Datos con read_at en el futuro."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "title": "Título válido",
        "message": "Mensaje válido",
        "is_read": True,
        "read_at": pendulum.now().add(days=1)  # Fecha futura
    }


# Fixtures para diferentes tipos de alertas
@pytest.fixture
def conflict_alert_data() -> Dict[str, Any]:
    """Datos para alerta de conflicto."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "status": AlertStatus.NEW,
        "title": "Conflicto de horario detectado",
        "message": "Se ha detectado un conflicto en la programación del empleado",
        "related_entity_type": "schedule",
        "related_entity_id": 123
    }


@pytest.fixture
def deadline_warning_data() -> Dict[str, Any]:
    """Datos para alerta de advertencia de fecha límite."""
    return {
        "user_id": 2,
        "alert_type": AlertType.DEADLINE_WARNING,
        "status": AlertStatus.NEW,
        "title": "Proyecto próximo a vencer",
        "message": "El proyecto 'Sistema de Planificación' vence en 3 días",
        "related_entity_type": "project",
        "related_entity_id": 456
    }


@pytest.fixture
def system_error_data() -> Dict[str, Any]:
    """Datos para alerta de error del sistema."""
    return {
        "user_id": 3,
        "alert_type": AlertType.SYSTEM_ERROR,
        "status": AlertStatus.NEW,
        "title": "Error en el sistema",
        "message": "Se ha producido un error interno del sistema"
    }


@pytest.fixture
def overallocation_alert_data() -> Dict[str, Any]:
    """Datos para alerta de sobreasignación."""
    return {
        "user_id": 4,
        "alert_type": AlertType.OVERALLOCATION,
        "status": AlertStatus.NEW,
        "title": "Empleado sobreasignado",
        "message": "El empleado tiene más de 40 horas asignadas esta semana",
        "related_entity_type": "employee",
        "related_entity_id": 789
    }


# Fixtures para datos de actualización
@pytest.fixture
def alert_update_data() -> Dict[str, Any]:
    """Datos para actualizar una alerta."""
    return {
        "status": AlertStatus.READ,
        "is_read": True,
        "read_at": pendulum.now()
    }


@pytest.fixture
def alert_partial_update_data() -> Dict[str, Any]:
    """Datos para actualización parcial de una alerta."""
    return {
        "title": "Título actualizado",
        "message": "Mensaje actualizado"
    }


@pytest.fixture
def alert_resolve_data() -> Dict[str, Any]:
    """Datos para resolver una alerta."""
    return {
        "status": AlertStatus.RESOLVED,
        "is_read": True,
        "read_at": pendulum.now()
    }


# Fixtures para filtros de búsqueda
@pytest.fixture
def alert_search_filter_data() -> Dict[str, Any]:
    """Datos para filtro de búsqueda de alertas."""
    return {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "status": AlertStatus.NEW,
        "is_read": False
    }


@pytest.fixture
def alert_search_filter_partial_data() -> Dict[str, Any]:
    """Datos parciales para filtro de búsqueda."""
    return {
        "alert_type": AlertType.DEADLINE_WARNING,
        "is_read": True
    }


@pytest.fixture
def alert_search_filter_empty() -> Dict[str, Any]:
    """Filtro de búsqueda vacío."""
    return {}


# Fixtures para casos extremos
@pytest.fixture
def alert_boundary_data() -> Dict[str, Any]:
    """Datos con valores límite."""
    return {
        "user_id": 1,
        "alert_type": AlertType.OTHER,
        "title": "A" * 200,  # Máximo permitido
        "message": "M",  # Mínimo permitido
        "related_entity_type": "E" * 50  # Máximo permitido
    }


@pytest.fixture
def alert_all_types_data() -> list[Dict[str, Any]]:
    """Lista con datos para todos los tipos de alerta."""
    base_data = {
        "user_id": 1,
        "title": "Título de prueba",
        "message": "Mensaje de prueba"
    }
    
    return [
        {**base_data, "alert_type": alert_type}
        for alert_type in AlertType
    ]


@pytest.fixture
def alert_all_statuses_data() -> list[Dict[str, Any]]:
    """Lista con datos para todos los estados de alerta."""
    base_data = {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "title": "Título de prueba",
        "message": "Mensaje de prueba"
    }
    
    return [
        {**base_data, "status": status}
        for status in AlertStatus
    ]


# Fixtures para datos de serialización
@pytest.fixture
def alert_serialization_data() -> Dict[str, Any]:
    """Datos para pruebas de serialización."""
    return {
        "user_id": 1,
        "alert_type": AlertType.VALIDATION_ERROR,
        "status": AlertStatus.NEW,
        "title": "Error de validación",
        "message": "Los datos proporcionados no son válidos",
        "related_entity_type": "form",
        "related_entity_id": 999,
        "is_read": False,
        "read_at": None
    }


# Fixtures para datos de comparación
@pytest.fixture
def alert_comparison_data() -> tuple[Dict[str, Any], Dict[str, Any]]:
    """Datos para pruebas de comparación entre alertas."""
    base_data = {
        "user_id": 1,
        "alert_type": AlertType.CONFLICT,
        "title": "Título",
        "message": "Mensaje"
    }
    
    alert1_data = {**base_data, "status": AlertStatus.NEW}
    alert2_data = {**base_data, "status": AlertStatus.READ}
    
    return alert1_data, alert2_data


# Fixtures para datos de performance
@pytest.fixture
def alert_performance_data() -> list[Dict[str, Any]]:
    """Datos para pruebas de rendimiento."""
    return [
        {
            "user_id": i,
            "alert_type": AlertType.CONFLICT,
            "title": f"Alerta {i}",
            "message": f"Mensaje de alerta número {i}"
        }
        for i in range(1, 101)  # 100 alertas
    ]