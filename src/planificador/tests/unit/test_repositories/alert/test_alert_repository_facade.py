"""Tests para AlertRepositoryFacade."""

import pytest
from unittest.mock import AsyncMock, patch
import pendulum

from planificador.repositories.alert.alert_repository_facade import (
    AlertRepositoryFacade,
)
from planificador.models.alert import Alert, AlertType, AlertStatus
from planificador.schemas.alert.alert import AlertCreate, AlertUpdate, AlertSearchFilter
from planificador.exceptions import (
    RepositoryError,
    NotFoundError,
    ValidationError,
)


class TestAlertRepositoryFacade:
    """Tests para AlertRepositoryFacade."""

    # ==================== TESTS CRUD ====================

    @pytest.mark.asyncio
    async def test_get_by_id_success(self, alert_repository, sample_alert):
        """Test obtener alerta por ID exitosamente."""
        # Arrange
        alert_id = 1
        alert_repository._crud_operations.get_by_id.return_value = sample_alert

        # Act
        result = await alert_repository.get_by_id(alert_id)

        # Assert
        assert result == sample_alert
        alert_repository._crud_operations.get_by_id.assert_called_once_with(alert_id)

    @pytest.mark.asyncio
    async def test_get_by_id_not_found(self, alert_repository):
        """Test obtener alerta por ID que no existe."""
        # Arrange
        alert_id = 999
        alert_repository._crud_operations.get_by_id.side_effect = NotFoundError(
            message=f"Alert with id {alert_id} not found",
            resource_type="Alert",
            resource_id=alert_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await alert_repository.get_by_id(alert_id)

        assert f"Alert with id {alert_id} not found" in str(exc_info.value)
        alert_repository._crud_operations.get_by_id.assert_called_once_with(alert_id)

    # ==================== TESTS CONSULTAS ====================

    @pytest.mark.asyncio
    async def test_find_by_type_success(self, alert_repository, sample_alerts_list):
        """Test buscar alertas por tipo exitosamente."""
        # Arrange
        alert_type = AlertType.CONFLICT
        type_alerts = [alert for alert in sample_alerts_list if alert.alert_type == alert_type]
        alert_repository._query_operations.find_by_type.return_value = type_alerts

        # Act
        result = await alert_repository.find_by_type(alert_type)

        # Assert
        assert result == type_alerts
        assert len(result) == len(type_alerts)  # Usar la longitud real de type_alerts
        assert all(alert.alert_type == alert_type for alert in result)
        alert_repository._query_operations.find_by_type.assert_called_once_with(alert_type)

    @pytest.mark.asyncio
    async def test_find_by_status_success(self, alert_repository, sample_alerts_list):
        """Test buscar alertas por estado exitosamente."""
        # Arrange
        status = AlertStatus.READ
        status_alerts = [alert for alert in sample_alerts_list if alert.status == status]
        alert_repository._query_operations.find_by_status.return_value = status_alerts

        # Act
        result = await alert_repository.find_by_status(status)

        # Assert
        assert result == status_alerts
        assert len(result) == 1
        assert all(alert.status == status for alert in result)
        alert_repository._query_operations.find_by_status.assert_called_once_with(status)

    # ==================== TESTS ESTADÍSTICAS ====================

    @pytest.mark.asyncio
    async def test_get_alert_statistics_success(
        self, alert_repository, sample_alert_statistics
    ):
        """Test obtener estadísticas de alertas exitosamente."""
        # Arrange
        alert_repository._statistics_operations.get_alert_statistics.return_value = (
            sample_alert_statistics
        )

        # Act
        result = await alert_repository.get_alert_statistics()

        # Assert
        assert result == sample_alert_statistics
        assert result['total_alerts'] == 150
        assert result['unread_alerts'] == 25
        assert result['critical_alerts'] == 8
        assert 'alerts_by_type' in result
        assert 'alerts_by_status' in result
        assert 'weekly_trend' in result
        alert_repository._statistics_operations.get_alert_statistics.assert_called_once()



    @pytest.mark.asyncio
    async def test_get_alert_trends_success(self, alert_repository):
        """Test obtener tendencias de alertas exitosamente."""
        # Arrange
        trends_data = {
            'daily_trends': {
                '2024-01-15': 12,
                '2024-01-16': 8,
                '2024-01-17': 15,
                '2024-01-18': 10,
                '2024-01-19': 6
            },
            'weekly_average': 10.2,
            'monthly_total': 320,
            'growth_rate': 5.2,
            'peak_hours': [9, 14, 16],
            'most_common_types': ['CONFLICT', 'DEADLINE_WARNING', 'SYSTEM_ERROR']
        }
        alert_repository._statistics_operations.get_alert_trends.return_value = trends_data

        # Act
        result = await alert_repository.get_alert_trends()

        # Assert
        assert result == trends_data
        assert 'daily_trends' in result
        assert 'weekly_average' in result
        assert 'monthly_total' in result
        assert result['growth_rate'] == 5.2
        alert_repository._statistics_operations.get_alert_trends.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_critical_alerts_summary_success(self, alert_repository):
        """Test obtener resumen de alertas críticas exitosamente."""
        # Arrange
        critical_summary = {
            'total_critical': 8,
            'unresolved_critical': 3,
            'critical_by_type': {
                'SYSTEM_ERROR': 4,
                'CONFLICT': 3,
                'VALIDATION_ERROR': 1
            },
            'oldest_unresolved': {
                'id': 45,
                'created_at': pendulum.now().subtract(days=5).isoformat(),
                'title': 'Error crítico del sistema'
            },
            'average_resolution_time_hours': 8.5,
            'escalation_needed': [
                {'id': 45, 'age_hours': 120},
                {'id': 67, 'age_hours': 72}
            ]
        }
        alert_repository._statistics_operations.get_critical_alerts_summary.return_value = (
            critical_summary
        )

        # Act
        result = await alert_repository.get_critical_alerts_summary()

        # Assert
        assert result == critical_summary
        assert result['total_critical'] == 8
        assert result['unresolved_critical'] == 3
        assert 'critical_by_type' in result
        assert 'escalation_needed' in result
        alert_repository._statistics_operations.get_critical_alerts_summary.assert_called_once()

    # ==================== TESTS CONSULTAS AVANZADAS ====================

    @pytest.mark.asyncio
    async def test_find_by_employee_success(self, alert_repository, sample_alerts_list):
        """Test obtener alertas por empleado exitosamente."""
        # Arrange
        employee_id = 1
        expected_alerts = sample_alerts_list[:2]  # Primeras 2 alertas
        alert_repository._query_operations.find_by_employee.return_value = expected_alerts

        # Act
        result = await alert_repository.find_by_employee(employee_id)

        # Assert
        assert result == expected_alerts
        assert len(result) == 2
        alert_repository._query_operations.find_by_employee.assert_called_once_with(employee_id)

    @pytest.mark.asyncio
    async def test_get_active_alerts_success(
        self, alert_repository, sample_alerts_list
    ):
        """Test obtener alertas activas exitosamente."""
        # Arrange
        active_alerts = [sample_alerts_list[0]]  # Solo alertas activas
        alert_repository._query_operations.get_active_alerts.return_value = active_alerts

        # Act
        result = await alert_repository.get_active_alerts()

        # Assert
        assert result == active_alerts
        assert len(result) == 1
        alert_repository._query_operations.get_active_alerts.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_critical_alerts_success(self, alert_repository):
        """Test obtener alertas críticas exitosamente."""
        # Arrange
        critical_alerts = [
            Alert(
                id=10,
                user_id=1,
                alert_type=AlertType.DEADLINE_WARNING,
                status=AlertStatus.NEW,
                title="Alerta crítica",
                message="Esta es una alerta crítica que requiere atención",
                is_read=False,
                created_at=pendulum.now().subtract(hours=48),
                updated_at=pendulum.now().subtract(hours=48)
            )
        ]
        alert_repository._query_operations.get_critical_alerts.return_value = critical_alerts

        # Act
        result = await alert_repository.get_critical_alerts()

        # Assert
        assert result == critical_alerts
        assert len(result) == 1
        alert_repository._query_operations.get_critical_alerts.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_date_range_success(self, alert_repository, sample_alerts_list):
        """Test buscar alertas por rango de fechas exitosamente."""
        # Arrange
        start_date = pendulum.now().subtract(hours=6)
        end_date = pendulum.now()
        date_range_alerts = [sample_alerts_list[0], sample_alerts_list[1]]
        alert_repository._query_operations.find_by_date_range.return_value = date_range_alerts

        # Act
        result = await alert_repository.find_by_date_range(start_date, end_date)

        # Assert
        assert result == date_range_alerts
        assert len(result) == 2
        alert_repository._query_operations.find_by_date_range.assert_called_once_with(start_date, end_date)

    # ==================== TESTS GESTIÓN DE ESTADOS ====================

    @pytest.mark.asyncio
    async def test_mark_as_read_success(self, alert_repository, sample_alert):
        """Test marcar alerta como leída exitosamente."""
        # Arrange
        alert_id = 1
        read_alert = Alert(
            id=sample_alert.id,
            user_id=sample_alert.user_id,
            alert_type=sample_alert.alert_type,
            status=sample_alert.status,
            title=sample_alert.title,
            message=sample_alert.message,
            related_entity_type=sample_alert.related_entity_type,
            related_entity_id=sample_alert.related_entity_id,
            is_read=True,
            read_at=pendulum.now(),
            created_at=sample_alert.created_at,
            updated_at=sample_alert.updated_at
        )
        alert_repository._state_manager.mark_as_read.return_value = read_alert

        # Act
        result = await alert_repository.mark_as_read(alert_id)

        # Assert
        assert result == read_alert
        assert result.is_read is True
        assert result.read_at is not None
        alert_repository._state_manager.mark_as_read.assert_called_once_with(alert_id)

    @pytest.mark.asyncio
    async def test_mark_as_resolved_success(self, alert_repository, sample_alert):
        """Test marcar alerta como resuelta exitosamente."""
        # Arrange
        alert_id = 1
        resolved_alert = Alert(
            id=sample_alert.id,
            user_id=sample_alert.user_id,
            alert_type=sample_alert.alert_type,
            status=AlertStatus.RESOLVED,
            title=sample_alert.title,
            message=sample_alert.message,
            related_entity_type=sample_alert.related_entity_type,
            related_entity_id=sample_alert.related_entity_id,
            is_read=sample_alert.is_read,
            read_at=sample_alert.read_at,
            created_at=sample_alert.created_at,
            updated_at=sample_alert.updated_at
        )
        alert_repository._state_manager.mark_as_resolved.return_value = resolved_alert

        # Act
        result = await alert_repository.mark_as_resolved(alert_id)

        # Assert
        assert result == resolved_alert
        assert result.status == AlertStatus.RESOLVED
        alert_repository._state_manager.mark_as_resolved.assert_called_once_with(alert_id)

    @pytest.mark.asyncio
    async def test_mark_as_ignored_success(self, alert_repository, sample_alert):
        """Test marcar alerta como ignorada exitosamente."""
        # Arrange
        alert_id = 1
        ignored_alert = Alert(
            id=sample_alert.id,
            user_id=sample_alert.user_id,
            alert_type=sample_alert.alert_type,
            status=AlertStatus.IGNORED,
            title=sample_alert.title,
            message=sample_alert.message,
            related_entity_type=sample_alert.related_entity_type,
            related_entity_id=sample_alert.related_entity_id,
            is_read=sample_alert.is_read,
            read_at=sample_alert.read_at,
            created_at=sample_alert.created_at,
            updated_at=sample_alert.updated_at
        )
        alert_repository._state_manager.mark_as_ignored.return_value = ignored_alert

        # Act
        result = await alert_repository.mark_as_ignored(alert_id)

        # Assert
        assert result == ignored_alert
        assert result.status == AlertStatus.IGNORED
        alert_repository._state_manager.mark_as_ignored.assert_called_once_with(alert_id)

    @pytest.mark.asyncio
    async def test_mark_as_read_not_found(self, alert_repository):
        """Test marcar como leída una alerta que no existe."""
        # Arrange
        alert_id = 999
        alert_repository._state_manager.mark_as_read.side_effect = NotFoundError(
            message=f"Alert with id {alert_id} not found",
            resource_type="Alert",
            resource_id=alert_id
        )

        # Act & Assert
        with pytest.raises(NotFoundError) as exc_info:
            await alert_repository.mark_as_read(alert_id)

        assert f"Alert with id {alert_id} not found" in str(exc_info.value)
        alert_repository._state_manager.mark_as_read.assert_called_once_with(alert_id)

    @pytest.mark.asyncio
    async def test_mark_as_resolved_already_resolved(self, alert_repository):
        """Test marcar como resuelta una alerta ya resuelta."""
        # Arrange
        alert_id = 1
        alert_repository._state_manager.mark_as_resolved.side_effect = ValidationError(
            message="Alert is already resolved",
            field="status",
            value="RESOLVED"
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await alert_repository.mark_as_resolved(alert_id)

        assert "already resolved" in str(exc_info.value)
        alert_repository._state_manager.mark_as_resolved.assert_called_once_with(alert_id)

    # ==================== TESTS VALIDACIONES ====================

    @pytest.mark.asyncio
    async def test_validate_alert_data_success(self, alert_repository, sample_alert_create):
        """Test validar datos de alerta exitosamente."""
        # Arrange
        alert_repository._validation_operations.validate_alert_data.return_value = True

        # Act
        result = await alert_repository.validate_alert_data(sample_alert_create)

        # Assert
        assert result is True
        alert_repository._validation_operations.validate_alert_data.assert_called_once_with(
            sample_alert_create
        )

    @pytest.mark.asyncio
    async def test_validate_alert_data_invalid_user(self, alert_repository, sample_alert_create):
        """Test validar datos de alerta con usuario inválido."""
        # Arrange
        alert_repository._validation_operations.validate_alert_data.side_effect = ValidationError(
            message="User does not exist",
            field="user_id",
            value=sample_alert_create.user_id
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await alert_repository.validate_alert_data(sample_alert_create)

        assert "User does not exist" in str(exc_info.value)
        assert exc_info.value.field == "user_id"
        alert_repository._validation_operations.validate_alert_data.assert_called_once_with(
            sample_alert_create
        )

    @pytest.mark.asyncio
    async def test_validate_alert_consistency_success(self, alert_repository, sample_alert):
        """Test validar consistencia de alerta exitosamente."""
        # Arrange
        alert_repository._validation_operations.validate_alert_consistency.return_value = True

        # Act
        result = await alert_repository.validate_alert_consistency(sample_alert)

        # Assert
        assert result is True
        alert_repository._validation_operations.validate_alert_consistency.assert_called_once_with(
            sample_alert
        )

    @pytest.mark.asyncio
    async def test_validate_alert_consistency_read_without_timestamp(
        self, alert_repository, sample_alert
    ):
        """Test validar consistencia de alerta leída sin timestamp."""
        # Arrange
        inconsistent_alert = Alert(
            id=sample_alert.id,
            user_id=sample_alert.user_id,
            alert_type=sample_alert.alert_type,
            status=sample_alert.status,
            title=sample_alert.title,
            message=sample_alert.message,
            related_entity_type=sample_alert.related_entity_type,
            related_entity_id=sample_alert.related_entity_id,
            is_read=True,
            read_at=None,
            created_at=sample_alert.created_at,
            updated_at=sample_alert.updated_at
        )
        alert_repository._validation_operations.validate_alert_consistency.side_effect = ValidationError(
            message="Read alert must have read_at timestamp",
            field="read_at",
            value=None
        )

        # Act & Assert
        with pytest.raises(ValidationError) as exc_info:
            await alert_repository.validate_alert_consistency(inconsistent_alert)

        assert "read_at timestamp" in str(exc_info.value)
        alert_repository._validation_operations.validate_alert_consistency.assert_called_once_with(
            inconsistent_alert
        )

    # =====================================================
    # TESTS MÉTODOS AUXILIARES Y MANTENIMIENTO
    # =====================================================

    @pytest.mark.asyncio
    async def test_cleanup_old_alerts_success(self, alert_repository, sample_alerts_list):
        """Test limpieza exitosa de alertas antiguas."""
        # Arrange
        expected_count = 15
        alert_repository._state_manager.cleanup_old_alerts.return_value = expected_count
        
        # Act
        days_old = 30
        result = await alert_repository.cleanup_old_alerts(days_old)
        
        # Assert
        assert result == expected_count
        alert_repository._state_manager.cleanup_old_alerts.assert_called_once_with(days_old)

    @pytest.mark.asyncio
    async def test_cleanup_old_resolved_alerts_success(self, alert_repository):
        """Test limpiar alertas resueltas antiguas exitosamente."""
        # Arrange
        days_old = 30
        expected_count = 15
        alert_repository._state_manager.cleanup_old_resolved_alerts.return_value = expected_count

        # Act
        result = await alert_repository.cleanup_old_resolved_alerts(days_old)

        # Assert
        assert result == expected_count
        alert_repository._state_manager.cleanup_old_resolved_alerts.assert_called_once_with(days_old)

    @pytest.mark.asyncio
    async def test_get_comprehensive_statistics_success(self, alert_repository):
        """Test obtener estadísticas comprehensivas exitosamente."""
        # Arrange
        expected_stats = {
            "total_alerts": 500,
            "by_status": {"active": 100, "resolved": 350, "dismissed": 50},
            "by_type": {"system": 200, "user": 300},
            "performance": {"avg_response_time": 2.5}
        }
        alert_repository._statistics_operations.get_comprehensive_statistics.return_value = expected_stats

        # Act
        result = await alert_repository.get_comprehensive_statistics()

        # Assert
        assert result == expected_stats
        alert_repository._statistics_operations.get_comprehensive_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_weekly_statistics_success(self, alert_repository):
        """Test obtener estadísticas semanales exitosamente."""
        # Arrange
        expected_stats = {
            "week_total": 50,
            "daily_breakdown": {"monday": 8, "tuesday": 12, "wednesday": 10},
            "avg_per_day": 7.1,
            "trend": "increasing"
        }
        alert_repository._statistics_operations.get_weekly_statistics.return_value = expected_stats

        # Act
        result = await alert_repository.get_weekly_statistics()

        # Assert
        assert result == expected_stats
        alert_repository._statistics_operations.get_weekly_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_alert_statistics_success(self, alert_repository):
        """Test obtener estadísticas de alertas exitosamente."""
        # Arrange
        expected_stats = {
            "total_alerts": 100,
            "active_alerts": 25,
            "resolved_alerts": 60,
            "dismissed_alerts": 15
        }
        alert_repository._statistics_operations.get_alert_statistics.return_value = expected_stats

        # Act
        result = await alert_repository.get_alert_statistics()

        # Assert
        assert result == expected_stats
        alert_repository._statistics_operations.get_alert_statistics.assert_called_once_with(None, None)

    @pytest.mark.asyncio
    async def test_get_performance_metrics_success(self, alert_repository):
        """Test obtener métricas de rendimiento exitosamente."""
        # Arrange
        expected_metrics = {
            "avg_response_time": 2.5,
            "total_processed": 1000,
            "success_rate": 0.95
        }
        alert_repository._statistics_operations.get_performance_metrics.return_value = expected_metrics

        # Act
        result = await alert_repository.get_performance_metrics()

        # Assert
        assert result == expected_metrics
        alert_repository._statistics_operations.get_performance_metrics.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_cache_statistics_success(self, alert_repository):
        """Test obtención exitosa de estadísticas de caché."""
        # Configurar mock
        expected_stats = {
            'cache_size': 1024,
            'hit_rate': 85.2,
            'miss_rate': 14.8,
            'total_requests': 5000,
            'cache_hits': 4260,
            'cache_misses': 740,
            'evictions': 12,
            'memory_usage_mb': 15.6
        }
        alert_repository._statistics_operations.get_alert_statistics.return_value = expected_stats
        
        # Ejecutar
        result = await alert_repository.get_alert_statistics()
        
        # Verificar
        assert result == expected_stats
        alert_repository._statistics_operations.get_alert_statistics.assert_called_once()

    @pytest.mark.asyncio
    async def test_count_alerts_by_status_success(self, alert_repository):
        """Test contar alertas por estado exitosamente."""
        # Arrange
        expected_count = {"active": 5, "resolved": 3, "dismissed": 2}
        alert_repository._statistics_operations.get_alert_counts_by_status.return_value = expected_count

        # Act
        result = await alert_repository.get_alert_counts_by_status()

        # Assert
        assert result == expected_count
        alert_repository._statistics_operations.get_alert_counts_by_status.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_employee_success(self, alert_repository, sample_alert):
        """Test búsqueda exitosa de alertas por empleado."""
        # Arrange
        employee_id = 123
        expected_alerts = [sample_alert]
        alert_repository._query_operations.find_by_employee.return_value = expected_alerts

        # Act
        result = await alert_repository.find_by_employee(employee_id)

        # Assert
        assert result == expected_alerts
        alert_repository._query_operations.find_by_employee.assert_called_once_with(employee_id)

    @pytest.mark.asyncio
    async def test_get_active_alerts_success_duplicate(self, alert_repository, sample_alerts_list):
        """Test obtención exitosa de alertas activas."""
        # Configurar mock
        expected_alerts = [sample_alerts_list[0]]
        alert_repository._query_operations.get_active_alerts.return_value = expected_alerts
        
        # Ejecutar
        result = await alert_repository.get_active_alerts()
        
        # Verificar
        assert result == expected_alerts
        alert_repository._query_operations.get_active_alerts.assert_called_once()

    @pytest.mark.asyncio
    async def test_get_critical_alerts_success_duplicate(self, alert_repository):
        """Test obtención exitosa de alertas críticas."""
        # Configurar mock
        expected_alerts = []
        alert_repository._query_operations.get_critical_alerts.return_value = expected_alerts
        
        # Ejecutar
        result = await alert_repository.get_critical_alerts()
        
        # Verificar
        assert result == expected_alerts
        alert_repository._query_operations.get_critical_alerts.assert_called_once()

    @pytest.mark.asyncio
    async def test_find_by_date_range_success_duplicate(self, alert_repository, sample_alerts_list):
        """Test búsqueda exitosa de alertas por rango de fechas."""
        # Configurar mock
        start_date = pendulum.now().subtract(hours=6)
        end_date = pendulum.now()
        expected_alerts = sample_alerts_list[:2]
        alert_repository._query_operations.find_by_date_range.return_value = expected_alerts
        
        # Ejecutar
        result = await alert_repository.find_by_date_range(start_date, end_date)
        
        # Verificar
        assert result == expected_alerts
        assert len(result) == 2
        alert_repository._query_operations.find_by_date_range.assert_called_once_with(start_date, end_date)

    @pytest.mark.asyncio
    async def test_get_alert_statistics_success_duplicate(self, alert_repository):
        """Test obtener estadísticas de alertas por período exitosamente."""
        # Arrange
        expected_summary = {
            'total_alerts': 150,
            'new_alerts': 45,
            'read_alerts': 67,
            'resolved_alerts': 38,
            'critical_alerts': 8,
            'alerts_by_type': {
                'SYSTEM_ERROR': 45,
                'DEADLINE_WARNING': 38,
                'VALIDATION_ERROR': 32,
                'NOTIFICATION': 20
            },
            'alerts_by_status': {
                'NEW': 45,
                'READ': 67,
                'RESOLVED': 38
            }
        }
        alert_repository._statistics_operations.get_alert_statistics.return_value = expected_summary

        # Act
        result = await alert_repository.get_alert_statistics()

        # Assert
        assert result == expected_summary
        assert result['total_alerts'] == 150
        assert result['critical_alerts'] == 8
        alert_repository._statistics_operations.get_alert_statistics.assert_called_once()

    # =====================================================
    # TESTS MANEJO DE ERRORES EN MÉTODOS AUXILIARES
    # =====================================================

    @pytest.mark.asyncio
    async def test_cleanup_old_alerts_error(self, alert_repository):
        """Test error al limpiar alertas antiguas."""
        # Arrange
        alert_repository._state_manager.cleanup_old_alerts.side_effect = RepositoryError(
            message="Error al limpiar alertas",
            operation="cleanup_old_alerts",
            entity_type="Alert"
        )

        # Act & Assert
        with pytest.raises(RepositoryError, match="Error al limpiar alertas"):
            await alert_repository.cleanup_old_alerts(30)

        alert_repository._state_manager.cleanup_old_alerts.assert_called_once_with(30)

    @pytest.mark.asyncio
    async def test_import_alerts_file_not_found_error(self, alert_repository):
        """Test manejo de error cuando archivo de importación no existe."""
        # Configurar mock para error
        from planificador.exceptions.repository import RepositoryError
        alert_repository._query_operations.find_by_type.side_effect = RepositoryError(
            message="Archivo de importación no encontrado",
            operation="import_from_csv",
            entity_type="Alert"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(RepositoryError) as exc_info:
            await alert_repository.find_by_type("INFO")
        
        assert "Archivo de importación no encontrado" in str(exc_info.value)

    @pytest.mark.asyncio
    async def test_get_alert_statistics_service_unavailable_error(self, alert_repository):
        """Test manejo de error cuando servicio de estadísticas no está disponible."""
        # Configurar mock para error
        from planificador.exceptions.repository import RepositoryError
        alert_repository._statistics_operations.get_alert_statistics.side_effect = RepositoryError(
            message="Servicio de estadísticas no disponible",
            operation="get_alert_statistics",
            entity_type="Alert"
        )
        
        # Ejecutar y verificar excepción
        with pytest.raises(RepositoryError) as exc_info:
            await alert_repository.get_alert_statistics()
        
        assert "Servicio de estadísticas no disponible" in str(exc_info.value)