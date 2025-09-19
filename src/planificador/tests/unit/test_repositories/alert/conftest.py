"""Configuración de fixtures para tests del repositorio de alertas."""

import pytest
from unittest.mock import AsyncMock, MagicMock
import pendulum

from planificador.repositories.alert.alert_repository_facade import (
    AlertRepositoryFacade,
)
from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.schemas.alert.alert import AlertCreate, AlertUpdate, AlertSearchFilter


@pytest.fixture
def mock_maintenance_operations():
    """Mock de operaciones de mantenimiento."""
    maintenance_ops = AsyncMock()
    maintenance_ops.cleanup_old_alerts = AsyncMock()
    maintenance_ops.export_alerts = AsyncMock()
    maintenance_ops.backup_alerts = AsyncMock()
    maintenance_ops.restore_alerts = AsyncMock()
    maintenance_ops.archive_alerts = AsyncMock()
    maintenance_ops.optimize_database = AsyncMock()
    return maintenance_ops


@pytest.fixture
def mock_session():
    """Mock de sesión de base de datos."""
    session = AsyncMock()
    session.commit = AsyncMock()
    session.rollback = AsyncMock()
    session.close = AsyncMock()
    return session


@pytest.fixture
def mock_crud_operations():
    """Mock de operaciones CRUD."""
    crud_ops = AsyncMock()
    crud_ops.create = AsyncMock()
    crud_ops.get_by_id = AsyncMock()
    crud_ops.update = AsyncMock()
    crud_ops.delete = AsyncMock()
    crud_ops.get_all = AsyncMock()
    return crud_ops


@pytest.fixture
def mock_query_operations():
    """Mock de operaciones de consulta."""
    query_ops = AsyncMock()
    query_ops.find_by_user_id = AsyncMock()
    query_ops.find_by_id = AsyncMock()
    query_ops.find_by_type = AsyncMock()
    query_ops.find_by_status = AsyncMock()
    query_ops.find_unread = AsyncMock()
    query_ops.find_active_alerts = AsyncMock()
    query_ops.search = AsyncMock()
    query_ops.search_paginated = AsyncMock()
    query_ops.find_by_employee = AsyncMock()
    query_ops.find_by_project = AsyncMock()
    query_ops.find_by_related_entity = AsyncMock()
    query_ops.find_requiring_attention = AsyncMock()
    query_ops.find_overdue = AsyncMock()
    query_ops.find_recent = AsyncMock()
    query_ops.find_by_date_range = AsyncMock()
    query_ops.find_current_week_alerts = AsyncMock()
    query_ops.find_current_month_alerts = AsyncMock()
    query_ops.find_filtered_alerts = AsyncMock()
    query_ops.count_by_criteria = AsyncMock()
    query_ops.get_by_criteria = AsyncMock()
    return query_ops


@pytest.fixture
def mock_statistics_operations():
    """Mock de operaciones de estadísticas."""
    stats_ops = AsyncMock()
    stats_ops.get_alert_statistics = AsyncMock()
    stats_ops.get_alerts_by_priority = AsyncMock()
    stats_ops.get_alerts_by_date_range = AsyncMock()
    stats_ops.get_alerts_count_by_type = AsyncMock()
    stats_ops.get_alerts_count_by_status = AsyncMock()
    stats_ops.get_recent_alerts_summary = AsyncMock()
    stats_ops.get_overdue_alerts_count = AsyncMock()
    stats_ops.get_critical_alerts_count = AsyncMock()
    stats_ops.get_unread_alerts_count = AsyncMock()
    stats_ops.get_alerts_trend = AsyncMock()
    stats_ops.get_performance_metrics = AsyncMock()
    stats_ops.get_user_activity_summary = AsyncMock()
    stats_ops.get_system_health_indicators = AsyncMock()
    stats_ops.get_alert_resolution_time = AsyncMock()
    stats_ops.get_alert_frequency_analysis = AsyncMock()
    stats_ops.get_alert_impact_assessment = AsyncMock()
    stats_ops.get_alert_correlation_data = AsyncMock()
    stats_ops.get_predictive_analytics = AsyncMock()
    stats_ops.get_custom_report_data = AsyncMock()
    stats_ops.get_alert_statistics.return_value = {"total": 100, "active": 50}
    stats_ops.get_performance_metrics.return_value = {"avg_time": 2.5}
    stats_ops.get_comprehensive_statistics.return_value = {"total": 100}
    stats_ops.get_weekly_statistics.return_value = {"week_total": 50}
    return stats_ops


@pytest.fixture
def mock_state_manager():
    """Mock del gestor de estados."""
    state_mgr = AsyncMock()
    state_mgr.mark_as_read = AsyncMock()
    state_mgr.mark_as_resolved = AsyncMock()
    state_mgr.mark_as_ignored = AsyncMock()
    state_mgr.bulk_mark_as_read = AsyncMock()
    state_mgr.bulk_update_status = AsyncMock()
    return state_mgr


@pytest.fixture
def mock_validation_operations():
    """Mock de operaciones de validación."""
    validation_ops = AsyncMock()
    validation_ops.validate_alert_data = AsyncMock()
    validation_ops.validate_alert_consistency = AsyncMock()
    validation_ops.validate_state_transition = AsyncMock()
    validation_ops.validate_business_rules = AsyncMock()
    validation_ops.check_alert_permissions = AsyncMock()
    return validation_ops


@pytest.fixture
def alert_repository(
    mock_session,
    mock_crud_operations,
    mock_query_operations,
    mock_statistics_operations,
    mock_state_manager,
    mock_validation_operations,
    mock_maintenance_operations,
):
    """Fixture del repositorio de alertas con mocks."""
    repository = AlertRepositoryFacade(mock_session)
    
    # Inyectar mocks
    repository._crud_operations = mock_crud_operations
    repository._query_operations = mock_query_operations
    repository._statistics_operations = mock_statistics_operations
    repository._state_manager = mock_state_manager
    repository._validation_operations = mock_validation_operations
    repository._maintenance_operations = mock_maintenance_operations
    
    return repository


@pytest.fixture
def sample_alert():
    """Fixture de alerta de ejemplo."""
    return Alert(
            id=1,
            user_id=1,
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.READ,
            title="Test Alert",
            message="This is a test alert message",
            related_entity_type="Project",
            related_entity_id=1,
            is_read=True,
            read_at=pendulum.now().subtract(hours=1),
            created_at=pendulum.now().subtract(hours=2),
            updated_at=pendulum.now().subtract(hours=1)
        )


@pytest.fixture
def sample_alert_create():
    """Fixture de datos para crear alerta."""
    return AlertCreate(
        user_id=1,
        alert_type=AlertType.SYSTEM_ERROR,
        title="Nueva alerta de conflicto",
        message="Se detectó un nuevo conflicto",
        related_entity_type="schedule",
        related_entity_id=123,
        metadata={"severity": "medium"}
    )


@pytest.fixture
def sample_alert_update():
    """Fixture de datos para actualizar alerta."""
    import pendulum
    return AlertUpdate(
        title="Título actualizado",
        message="Mensaje actualizado",
        status=AlertStatus.READ,
        is_read=True,
        read_at=pendulum.now().subtract(hours=1),
        metadata={"severity": "low", "updated": True}
    )


@pytest.fixture
def sample_alerts_list():
    """Fixture de lista de alertas de ejemplo."""
    now = pendulum.now()
    return [
        Alert(
            id=1,
            user_id=1,
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.NEW,
            title="Conflicto de horario",
            message="Conflicto detectado",
            is_read=False,
            created_at=now.subtract(hours=2),
            updated_at=now.subtract(hours=2),
            related_entity_type="schedule",
            related_entity_id=123
        ),
        Alert(
            id=2,
            user_id=1,
            alert_type=AlertType.DEADLINE_WARNING,
            status=AlertStatus.READ,
            title="Advertencia de fecha límite",
            message="Se acerca la fecha límite",
            is_read=True,
            read_at=now.subtract(hours=1),
            created_at=now.subtract(hours=4),
            updated_at=now.subtract(hours=1),
            related_entity_type="task",
            related_entity_id=456
        ),
        Alert(
            id=3,
            user_id=2,
            alert_type=AlertType.SYSTEM_ERROR,
            status=AlertStatus.RESOLVED,
            title="Error del sistema",
            message="Error resuelto automáticamente",
            is_read=True,
            read_at=now.subtract(hours=3),
            created_at=now.subtract(hours=6),
            updated_at=now.subtract(hours=3),
            related_entity_type="system",
            related_entity_id=789
        )
    ]


@pytest.fixture
def sample_alert_search_filter():
    """Fixture de filtro de búsqueda de alertas."""
    return AlertSearchFilter(
        user_id=1,
        alert_type=AlertType.SYSTEM_ERROR,
        status=AlertStatus.NEW,
        is_read=False,
        start_date=pendulum.now().subtract(days=7),
        end_date=pendulum.now(),
        related_entity_type="schedule"
    )


@pytest.fixture
def sample_alert_statistics():
    """Fixture de estadísticas de alertas."""
    return {
        'total_alerts': 150,
        'unread_alerts': 25,
        'critical_alerts': 8,
        'alerts_by_type': {
            'SYSTEM_ERROR': 45,
            'DEADLINE_WARNING': 38,
            'VALIDATION_ERROR': 32,
            'NOTIFICATION': 20
        },
        'alerts_by_status': {
            'NEW': 25,
            'READ': 45,
            'RESOLVED': 65,
            'IGNORED': 15
        },
        'weekly_trend': {
            'current_week': 28,
            'previous_week': 32,
            'change_percentage': -12.5
        },
        'average_resolution_time_hours': 8.5,
        'most_active_hour': 14,
        'most_active_day': 'Wednesday'
    }


@pytest.fixture
def sample_employee_alert_summary():
    """Fixture de resumen de alertas por empleado."""
    return {
        'employee_id': 1,
        'total_alerts': 25,
        'unread_alerts': 5,
        'critical_alerts': 2,
        'alerts_by_type': {
            'SYSTEM_ERROR': 12,
            'DEADLINE_WARNING': 8,
            'VALIDATION_ERROR': 3,
            'NOTIFICATION': 2
        },
        'alerts_by_status': {
            'NEW': 5,
            'READ': 8,
            'RESOLVED': 10,
            'IGNORED': 2
        },
        'average_response_time_hours': 4.2,
        'last_alert_date': pendulum.now().subtract(hours=6).isoformat(),
        'most_common_alert_time': 9  # 9 AM
    }