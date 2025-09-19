# src/planificador/repositories/alert/alert_repository_facade.py

from typing import List, Optional, Dict, Any, Union
from datetime import datetime
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger
import pendulum

from .interfaces.alert_repository_interface import IAlertRepository
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.state_manager import StateManager
from .modules.validation_operations import ValidationOperations
from ...models.alert import Alert, AlertType, AlertStatus
from ...schemas.alert.alert import AlertCreate, AlertUpdate, AlertSearchFilter
from ...exceptions.repository_exceptions import RepositoryError


class AlertRepositoryFacade(IAlertRepository):
    """
    Facade principal para el repositorio de alertas.
    
    Integra todos los módulos especializados y proporciona una interfaz
    unificada para todas las operaciones relacionadas con alertas.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade del repositorio de alertas.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self._session = session
        self._logger = logger.bind(component="AlertRepositoryFacade")
        
        # Inicializar módulos especializados
        self._crud_operations = CrudOperations(session)
        self._query_operations = QueryOperations(session)
        self._statistics_operations = StatisticsOperations(session)
        self._state_manager = StateManager(session)
        self._validation_operations = ValidationOperations(session)
        
        self._logger.debug("AlertRepositoryFacade inicializado")

    # ==========================================
    # OPERACIONES CRUD
    # ==========================================

    async def create_alert(self, alert_data: AlertCreate) -> Alert:
        """Crea una nueva alerta."""
        return await self._crud_operations.create_alert(alert_data)

    async def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta por su ID."""
        return await self._crud_operations.get_by_id(alert_id)

    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Alert]:
        """Obtiene una alerta por un campo único."""
        return await self._crud_operations.get_by_unique_field(field_name, field_value)

    async def update_alert(self, alert_id: int, alert_data: AlertUpdate) -> Alert:
        """Actualiza una alerta existente."""
        return await self._crud_operations.update_alert(alert_id, alert_data)

    async def delete_alert(self, alert_id: int) -> bool:
        """Elimina una alerta."""
        return await self._crud_operations.delete_alert(alert_id)

    async def bulk_create_alerts(self, alerts_data: List[AlertCreate]) -> List[Alert]:
        """Crea múltiples alertas en lote."""
        return await self._crud_operations.bulk_create_alerts(alerts_data)

    # ==========================================
    # OPERACIONES DE CONSULTA
    # ==========================================

    async def find_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Busca alertas por tipo."""
        return await self._query_operations.find_by_type(alert_type)

    async def find_by_status(self, status: AlertStatus) -> List[Alert]:
        """Busca alertas por estado."""
        return await self._query_operations.find_by_status(status)

    async def get_active_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas activas."""
        return await self._query_operations.get_active_alerts()

    async def get_critical_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas críticas."""
        return await self._query_operations.get_critical_alerts()

    async def get_unread_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas no leídas."""
        return await self._query_operations.get_unread_alerts()

    async def get_alerts_with_relations(self) -> List[Alert]:
        """Obtiene alertas con sus relaciones cargadas."""
        return await self._query_operations.get_alerts_with_relations()

    async def get_with_relations(self, alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta con sus relaciones cargadas."""
        return await self._query_operations.get_with_relations(alert_id)

    async def find_by_employee(self, employee_id: int) -> List[Alert]:
        """Busca alertas por empleado."""
        return await self._query_operations.find_by_employee(employee_id)

    async def find_by_project(self, project_id: int) -> List[Alert]:
        """Busca alertas por proyecto."""
        return await self._query_operations.find_by_project(project_id)

    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Alert]:
        """Busca alertas en un rango de fechas."""
        return await self._query_operations.find_by_date_range(start_date, end_date)

    async def get_old_resolved_alerts(self, days_old: int = 30) -> List[Alert]:
        """Obtiene alertas resueltas antiguas."""
        return await self._query_operations.get_old_resolved_alerts(days_old)

    async def get_current_week_alerts(self) -> List[Alert]:
        """Obtiene alertas de la semana actual."""
        return await self._query_operations.get_current_week_alerts()

    async def get_current_month_alerts(self) -> List[Alert]:
        """Obtiene alertas del mes actual."""
        return await self._query_operations.get_current_month_alerts()

    async def get_all_with_filters(self, filters: AlertSearchFilter) -> List[Alert]:
        """Obtiene alertas aplicando filtros."""
        return await self._query_operations.get_all_with_filters(filters)

    async def count_alerts_by_date_range(self, start_date: datetime, end_date: datetime) -> int:
        """Cuenta alertas en un rango de fechas."""
        return await self._query_operations.count_alerts_by_date_range(start_date, end_date)

    # ==========================================
    # OPERACIONES ESTADÍSTICAS
    # ==========================================

    async def count_total_alerts(self) -> int:
        """Cuenta el total de alertas."""
        return await self._statistics_operations.count_total_alerts()

    async def count_by_status(self, status: AlertStatus) -> int:
        """Cuenta alertas por estado."""
        return await self._statistics_operations.count_by_status(status)

    async def count_by_type(self, alert_type: AlertType) -> int:
        """Cuenta alertas por tipo."""
        return await self._statistics_operations.count_by_type(alert_type)

    async def count_unread_alerts(self) -> int:
        """Cuenta alertas no leídas."""
        return await self._statistics_operations.count_unread_alerts()

    async def count_critical_alerts(self) -> int:
        """Cuenta alertas críticas."""
        return await self._statistics_operations.count_critical_alerts()

    async def count_by_employee(self, employee_id: int) -> int:
        """Cuenta alertas por empleado."""
        return await self._statistics_operations.count_by_employee(employee_id)

    async def get_employee_alert_summary(self, employee_id: int) -> Dict[str, Any]:
        """Obtiene resumen de alertas por empleado."""
        return await self._statistics_operations.get_employee_alert_summary(employee_id)

    async def get_daily_alert_counts(self, days: int = 30) -> Dict[str, int]:
        """Obtiene conteos diarios de alertas."""
        return await self._statistics_operations.get_daily_alert_counts(days)

    async def get_weekly_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas semanales."""
        return await self._statistics_operations.get_weekly_statistics()

    async def get_monthly_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas mensuales."""
        return await self._statistics_operations.get_monthly_statistics()

    async def get_alert_trends(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene tendencias de alertas."""
        return await self._statistics_operations.get_alert_trends(days)

    async def get_comprehensive_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas comprehensivas."""
        return await self._statistics_operations.get_comprehensive_statistics()

    # ==========================================
    # GESTIÓN DE ESTADOS
    # ==========================================

    async def mark_as_read(self, alert_id: int) -> Alert:
        """Marca una alerta como leída."""
        return await self._state_manager.mark_as_read(alert_id)

    async def mark_as_resolved(self, alert_id: int) -> Alert:
        """Marca una alerta como resuelta."""
        return await self._state_manager.mark_as_resolved(alert_id)

    async def mark_as_ignored(self, alert_id: int) -> Alert:
        """Marca una alerta como ignorada."""
        return await self._state_manager.mark_as_ignored(alert_id)

    async def reactivate_alert(self, alert_id: int) -> Alert:
        """Reactiva una alerta."""
        return await self._state_manager.reactivate_alert(alert_id)

    async def mark_multiple_as_read(self, alert_ids: List[int]) -> List[Alert]:
        """Marca múltiples alertas como leídas."""
        return await self._state_manager.mark_multiple_as_read(alert_ids)

    async def mark_all_as_read_for_employee(self, employee_id: int) -> int:
        """Marca todas las alertas de un empleado como leídas."""
        return await self._state_manager.mark_all_as_read_for_employee(employee_id)

    async def resolve_multiple_alerts(self, alert_ids: List[int]) -> List[Alert]:
        """Resuelve múltiples alertas."""
        return await self._state_manager.resolve_multiple_alerts(alert_ids)

    async def cleanup_old_resolved_alerts(self, days_old: int = 30) -> int:
        """Limpia alertas resueltas antiguas."""
        return await self._state_manager.cleanup_old_resolved_alerts(days_old)

    async def get_state_transition_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de transiciones de estado."""
        return await self._state_manager.get_state_transition_summary()

    # ==========================================
    # OPERACIONES DE VALIDACIÓN
    # ==========================================

    async def validate_alert_exists(self, alert_id: int) -> bool:
        """Valida que una alerta existe."""
        return await self._validation_operations.validate_alert_exists(alert_id)

    async def validate_employee_exists(self, employee_id: int) -> bool:
        """Valida que un empleado existe."""
        return await self._validation_operations.validate_employee_exists(employee_id)

    async def validate_project_exists(self, project_id: int) -> bool:
        """Valida que un proyecto existe."""
        return await self._validation_operations.validate_project_exists(project_id)

    async def validate_alert_data(self, alert_data: Union[AlertCreate, AlertUpdate]) -> List[str]:
        """Valida los datos de una alerta."""
        return await self._validation_operations.validate_alert_data(alert_data)

    async def validate_alert_consistency(self, alert_id: int) -> List[str]:
        """Valida la consistencia de una alerta."""
        return await self._validation_operations.validate_alert_consistency(alert_id)

    async def validate_duplicate_alert(self, title: str, user_id: int, type_alert: AlertType) -> bool:
        """Valida si existe una alerta duplicada."""
        return await self._validation_operations.validate_duplicate_alert(title, user_id, type_alert)

    async def validate_alert_limit_per_user(self, user_id: int, limit: int = 50) -> bool:
        """Valida el límite de alertas por usuario."""
        return await self._validation_operations.validate_alert_limit_per_user(user_id, limit)

    async def validate_critical_alert_escalation(self, alert_id: int, hours_threshold: int = 24) -> bool:
        """Valida si una alerta crítica necesita escalación."""
        return await self._validation_operations.validate_critical_alert_escalation(alert_id, hours_threshold)

    async def validate_multiple_alerts(self, alert_ids: List[int]) -> Dict[int, List[str]]:
        """Valida múltiples alertas."""
        return await self._validation_operations.validate_multiple_alerts(alert_ids)

    async def get_data_integrity_report(self) -> Dict[str, Any]:
        """Obtiene reporte de integridad de datos."""
        return await self._validation_operations.get_data_integrity_report()

    # ==========================================
    # MÉTODOS AUXILIARES Y UTILIDADES
    # ==========================================

    async def get_repository_health(self) -> Dict[str, Any]:
        """
        Obtiene el estado de salud del repositorio.
        
        Returns:
            Dict[str, Any]: Información de salud del repositorio
        """
        try:
            self._logger.debug("Obteniendo estado de salud del repositorio")
            
            # Obtener estadísticas básicas
            total_alerts = await self.count_total_alerts()
            unread_count = await self.count_unread_alerts()
            critical_count = await self.count_critical_alerts()
            
            # Obtener reporte de integridad
            integrity_report = await self.get_data_integrity_report()
            
            # Obtener resumen de transiciones
            transition_summary = await self.get_state_transition_summary()
            
            health_info = {
                'repository_status': 'healthy',
                'total_alerts': total_alerts,
                'unread_alerts': unread_count,
                'critical_alerts': critical_count,
                'data_integrity': integrity_report,
                'state_transitions': transition_summary,
                'modules_status': {
                    'crud_operations': 'active',
                    'query_operations': 'active',
                    'statistics_operations': 'active',
                    'state_manager': 'active',
                    'validation_operations': 'active'
                },
                'last_check': pendulum.now().isoformat()
            }
            
            # Determinar estado general
            if integrity_report.get('health_score', 100) < 95:
                health_info['repository_status'] = 'warning'
            if integrity_report.get('health_score', 100) < 80:
                health_info['repository_status'] = 'critical'
            
            self._logger.info(f"Estado de salud del repositorio: {health_info['repository_status']}")
            return health_info
            
        except Exception as e:
            self._logger.error(f"Error obteniendo estado de salud del repositorio: {e}")
            raise RepositoryError(
                message=f"Error obteniendo estado de salud del repositorio: {e}",
                operation="get_repository_health",
                entity_type="AlertRepository",
                original_error=e
            )

    async def perform_maintenance(self, cleanup_days: int = 30) -> Dict[str, Any]:
        """
        Realiza tareas de mantenimiento del repositorio.
        
        Args:
            cleanup_days: Días de antigüedad para limpieza
            
        Returns:
            Dict[str, Any]: Resultado de las tareas de mantenimiento
        """
        try:
            self._logger.info("Iniciando tareas de mantenimiento del repositorio")
            
            maintenance_results = {
                'started_at': pendulum.now().isoformat(),
                'tasks_performed': [],
                'alerts_cleaned': 0,
                'errors': []
            }
            
            try:
                # Limpiar alertas resueltas antiguas
                cleaned_count = await self.cleanup_old_resolved_alerts(cleanup_days)
                maintenance_results['alerts_cleaned'] = cleaned_count
                maintenance_results['tasks_performed'].append('cleanup_old_resolved_alerts')
                
            except Exception as e:
                maintenance_results['errors'].append(f"Error en limpieza: {str(e)}")
            
            try:
                # Generar reporte de integridad
                integrity_report = await self.get_data_integrity_report()
                maintenance_results['integrity_check'] = integrity_report
                maintenance_results['tasks_performed'].append('data_integrity_check')
                
            except Exception as e:
                maintenance_results['errors'].append(f"Error en verificación de integridad: {str(e)}")
            
            maintenance_results['completed_at'] = pendulum.now().isoformat()
            maintenance_results['success'] = len(maintenance_results['errors']) == 0
            
            self._logger.info(f"Mantenimiento completado. Éxito: {maintenance_results['success']}")
            return maintenance_results
            
        except Exception as e:
            self._logger.error(f"Error durante mantenimiento del repositorio: {e}")
            raise RepositoryError(
                message=f"Error durante mantenimiento del repositorio: {e}",
                operation="perform_maintenance",
                entity_type="AlertRepository",
                original_error=e
            )

    def __str__(self) -> str:
        """Representación en string del facade."""
        return f"AlertRepositoryFacade(session={self._session})"

    def __repr__(self) -> str:
        """Representación detallada del facade."""
        return (
            f"AlertRepositoryFacade("
            f"session={self._session}, "
            f"modules=['crud', 'query', 'statistics', 'state_manager', 'validation']"
            f")"
        )