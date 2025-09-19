"""Fixtures para tests de AlertRepositoryFacade."""

import pytest
from unittest.mock import AsyncMock, MagicMock
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
import pendulum

from planificador.repositories.alert.alert_repository_facade import (
    AlertRepositoryFacade,
)
from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.schemas.alert.alert import AlertCreate, AlertUpdate, AlertSearchFilter


@pytest.fixture
def mock_session():
    """Mock de AsyncSession para tests."""
    session = AsyncMock(spec=AsyncSession)
    session.rollback = AsyncMock()
    session.commit = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def alert_repository(mock_session):
    """Fixture que proporciona una instancia de AlertRepositoryFacade con mocks."""
    # Crear mocks para todas las operaciones
    mock_crud = AsyncMock()
    mock_query = AsyncMock()
    mock_statistics = AsyncMock()
    mock_state_manager = AsyncMock()
    mock_validation = AsyncMock()
    
    # Crear facade con dependencias inyectadas
    facade = AlertRepositoryFacade(session=mock_session)
    
    # Inyectar mocks en el facade
    facade._crud_operations = mock_crud
    facade._query_operations = mock_query
    facade._statistics_operations = mock_statistics
    facade._state_manager = mock_state_manager
    facade._validation_operations = mock_validation
    
    return facade


@pytest.fixture
def sample_alert():
    """Fixture que proporciona datos de ejemplo para una alerta."""
    return Alert(
        id=1,
        user_id=1,
        alert_type=AlertType.SYSTEM_ERROR,
        status=AlertStatus.READ,
        title="Test Alert",
        message="This is a test alert message",
        related_entity_type="schedule",
        related_entity_id=123,
        is_read=True,
        read_at=None,
        created_at=pendulum.now().subtract(hours=2),
        updated_at=pendulum.now().subtract(hours=1)
    )


@pytest.fixture
def sample_alert_create():
    """Fixture que proporciona datos de ejemplo para crear una alerta."""
    return AlertCreate(
        user_id=1,
        alert_type=AlertType.SYSTEM_ERROR,
        title="Test Alert Create",
        message="This is a test alert create message",
        related_entity_type="Project",
        related_entity_id=1,
        status=AlertStatus.READ
    )


@pytest.fixture
def sample_alert_update():
    """Fixture que proporciona datos de ejemplo para actualizar una alerta."""
    return AlertUpdate(
        status=AlertStatus.READ,
        is_read=True,
        read_at=pendulum.now()
    )


@pytest.fixture
def sample_alert_search_filter():
    """Fixture que proporciona filtros de ejemplo para búsqueda de alertas."""
    return AlertSearchFilter(
        user_id=1,
        alert_type=AlertType.CONFLICT,
        status=AlertStatus.NEW,
        is_read=False
    )


@pytest.fixture
def sample_alerts_list():
    """Fixture que proporciona una lista de alertas de ejemplo."""
    return [
        Alert(
            id=1,
            user_id=1,
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.READ,
            title="Test Alert 1",
            message="This is test alert message 1",
            is_read=True,
            created_at=pendulum.now().subtract(hours=1),
            updated_at=pendulum.now().subtract(hours=0)
        ),
        Alert(
            id=2,
            user_id=1,
            alert_type=AlertType.DEADLINE_WARNING,
            status=AlertStatus.READ,
            title="Advertencia de fecha límite",
            message="Proyecto próximo a vencer",
            is_read=True,
            read_at=pendulum.now().subtract(hours=1),
            created_at=pendulum.now().subtract(hours=3),
            updated_at=pendulum.now().subtract(hours=1)
        ),
        Alert(
            id=3,
            user_id=2,
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.RESOLVED,
            title="Error del sistema",
            message="Error en el procesamiento de datos",
            is_read=True,
            read_at=pendulum.now().subtract(minutes=30),
            created_at=pendulum.now().subtract(hours=4),
            updated_at=pendulum.now().subtract(minutes=30)
        )
    ]


@pytest.fixture
def sample_alert_statistics():
    """Fixture que proporciona estadísticas de ejemplo para alertas."""
    return {
        'total_alerts': 150,
        'unread_alerts': 25,
        'critical_alerts': 8,
        'alerts_by_type': {
            'CONFLICT': 45,
            'DEADLINE_WARNING': 30,
            'SYSTEM_ERROR': 15,
            'VALIDATION_ERROR': 20,
            'OTHER': 40
        },
        'alerts_by_status': {
            'NEW': 25,
            'READ': 50,
            'RESOLVED': 60,
            'IGNORED': 15
        },
        'weekly_trend': {
            'current_week': 12,
            'previous_week': 18,
            'change_percentage': -33.33
        }
    }


@pytest.fixture
def sample_employee_alert_summary():
    """Fixture que proporciona resumen de alertas por empleado."""
    return {
        'employee_id': 1,
        'total_alerts': 25,
        'unread_alerts': 5,
        'critical_alerts': 2,
        'alerts_by_type': {
            'CONFLICT': 8,
            'DEADLINE_WARNING': 6,
            'SYSTEM_ERROR': 3,
            'OTHER': 8
        },
        'alerts_by_status': {
            'NEW': 5,
            'READ': 10,
            'RESOLVED': 8,
            'IGNORED': 2
        },
        'last_alert_date': pendulum.now().subtract(hours=2).isoformat(),
        'response_time_avg_hours': 4.5
    }


@pytest.fixture
def sample_data_integrity_report():
    """Fixture que proporciona reporte de integridad de datos."""
    return {
        'total_alerts_checked': 150,
        'inconsistencies_found': 2,
        'orphaned_alerts': 0,
        'invalid_references': 1,
        'read_status_mismatches': 1,
        'health_score': 98.67,
        'recommendations': [
            "Revisar alerta ID 45 - referencia inválida a entidad eliminada",
            "Corregir estado de lectura en alerta ID 78"
        ],
        'last_check': pendulum.now().isoformat()
    }


@pytest.fixture
def sample_state_transition_summary():
    """Fixture que proporciona resumen de transiciones de estado."""
    return {
        'total_transitions': 320,
        'transitions_by_type': {
            'NEW_to_READ': 180,
            'READ_to_RESOLVED': 95,
            'NEW_to_RESOLVED': 25,
            'READ_to_IGNORED': 15,
            'RESOLVED_to_NEW': 5
        },
        'average_resolution_time_hours': 12.5,
        'average_read_time_minutes': 45.2,
        'most_active_users': [
            {'user_id': 1, 'transitions': 85},
            {'user_id': 3, 'transitions': 72},
            {'user_id': 2, 'transitions': 58}
        ],
        'period_start': pendulum.now().subtract(days=30).isoformat(),
        'period_end': pendulum.now().isoformat()
    }