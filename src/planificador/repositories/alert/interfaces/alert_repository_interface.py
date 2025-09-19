# src/planificador/repositories/alert/alert_repository_interface.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from planificador.models.alert import Alert, AlertType, AlertStatus


class IAlertRepository(ABC):
    """Interfaz para el repositorio de alertas."""

    # ==========================================
    # OPERACIONES CRUD BÁSICAS
    # ==========================================

    @abstractmethod
    async def create_alert(self, alert_data: Dict[str, Any]) -> Alert:
        """Crea una nueva alerta con validaciones completas."""
        pass

    @abstractmethod
    async def get_by_id(self, alert_id: int) -> Optional[Alert]:
        """Obtiene una alerta por su ID."""
        pass

    @abstractmethod
    async def update_alert(self, alert_id: int, update_data: Dict[str, Any]) -> Alert:
        """Actualiza una alerta existente con validaciones."""
        pass

    @abstractmethod
    async def delete_alert(self, alert_id: int) -> bool:
        """Elimina una alerta del sistema."""
        pass

    @abstractmethod
    async def bulk_create_alerts(self, alerts_data: List[Dict[str, Any]]) -> List[Alert]:
        """Crea múltiples alertas en lote con validaciones."""
        pass

    # ==========================================
    # CONSULTAS POR TIPO Y ESTADO
    # ==========================================

    @abstractmethod
    async def find_by_type(self, alert_type: AlertType) -> List[Alert]:
        """Obtiene alertas por tipo específico."""
        pass

    @abstractmethod
    async def find_by_status(self, status: AlertStatus) -> List[Alert]:
        """Obtiene alertas por estado específico."""
        pass

    @abstractmethod
    async def get_active_alerts(self) -> List[Alert]:
        """Obtiene todas las alertas activas (NEW y READ)."""
        pass

    @abstractmethod
    async def get_critical_alerts(self) -> List[Alert]:
        """Obtiene alertas críticas activas."""
        pass

    @abstractmethod
    async def get_unread_alerts(self) -> List[Alert]:
        """Obtiene alertas no leídas (estado NEW)."""
        pass

    @abstractmethod
    async def get_alerts_with_relations(self) -> List[Alert]:
        """Obtiene todas las alertas con sus relaciones cargadas."""
        pass

    @abstractmethod
    async def get_with_relations(self, alert_id: int) -> Optional[Alert]:
        """Obtiene alerta específica con todas sus relaciones cargadas."""
        pass

    # ==========================================
    # CONSULTAS POR ENTIDADES RELACIONADAS
    # ==========================================

    @abstractmethod
    async def find_by_employee(self, employee_id: int) -> List[Alert]:
        """Obtiene alertas asociadas a un empleado específico."""
        pass

    @abstractmethod
    async def find_by_project(self, project_id: int) -> List[Alert]:
        """Obtiene alertas asociadas a un proyecto específico."""
        pass

    # ==========================================
    # CONSULTAS TEMPORALES
    # ==========================================

    @abstractmethod
    async def find_by_date_range(self, start_date: datetime, end_date: datetime) -> List[Alert]:
        """Obtiene alertas en un rango de fechas."""
        pass

    @abstractmethod
    async def get_old_resolved_alerts(self, days_old: int = 30) -> List[Alert]:
        """Obtiene alertas resueltas antiguas para limpieza."""
        pass

    @abstractmethod
    async def get_current_week_alerts(self) -> List[Alert]:
        """Obtiene alertas de la semana actual."""
        pass

    @abstractmethod
    async def get_current_month_alerts(self) -> List[Alert]:
        """Obtiene alertas del mes actual."""
        pass

    # ==========================================
    # GESTIÓN DE ESTADOS DE ALERTAS
    # ==========================================

    @abstractmethod
    async def acknowledge_alert(self, alert_id: int, acknowledged_by: str) -> Alert:
        """Marca una alerta como reconocida (READ)."""
        pass

    @abstractmethod
    async def resolve_alert(
        self, 
        alert_id: int, 
        resolved_by: str, 
        resolution_notes: Optional[str] = None
    ) -> Alert:
        """Marca una alerta como resuelta."""
        pass

    @abstractmethod
    async def dismiss_alert(
        self, 
        alert_id: int, 
        dismissed_by: str, 
        dismissal_reason: Optional[str] = None
    ) -> Alert:
        """Descarta una alerta (IGNORED)."""
        pass

    # ==========================================
    # OPERACIONES EN LOTE
    # ==========================================

    @abstractmethod
    async def bulk_acknowledge_alerts(
        self, 
        alert_ids: List[int], 
        acknowledged_by: str
    ) -> List[Alert]:
        """Reconoce múltiples alertas en lote."""
        pass

    @abstractmethod
    async def bulk_resolve_alerts(
        self, 
        alert_ids: List[int], 
        resolved_by: str, 
        resolution_notes: Optional[str] = None
    ) -> List[Alert]:
        """Resuelve múltiples alertas en lote."""
        pass

    # ==========================================
    # LIMPIEZA Y MANTENIMIENTO
    # ==========================================

    @abstractmethod
    async def cleanup_old_alerts(self, days_old: int = 90) -> int:
        """Limpia alertas antiguas resueltas o descartadas."""
        pass

    # ==========================================
    # FUNCIONES DE UTILIDAD
    # ==========================================

    @abstractmethod
    async def get_valid_state_transitions(self, current_status: AlertStatus) -> List[AlertStatus]:
        """Obtiene transiciones de estado válidas."""
        pass

    @abstractmethod
    async def can_transition_to_state(
        self, 
        current_status: AlertStatus, 
        target_status: AlertStatus
    ) -> bool:
        """Verifica si se puede transicionar a un estado."""
        pass

    @abstractmethod
    async def count_alerts_by_date_range(
        self, 
        start_date: datetime, 
        end_date: datetime
    ) -> int:
        """Cuenta alertas en un rango de fechas."""
        pass

    @abstractmethod
    async def format_alert_created_at(
        self, 
        alert: Alert, 
        format_str: str = 'YYYY-MM-DD HH:mm:ss'
    ) -> str:
        """Formatea la fecha de creación de una alerta."""
        pass

    @abstractmethod
    async def get_all_with_filters(self, filters: Dict[str, Any]) -> List[Alert]:
        """Obtiene alertas con filtros dinámicos."""
        pass

    # ==========================================
    # ESTADÍSTICAS Y MÉTRICAS
    # ==========================================

    @abstractmethod
    async def get_alert_statistics(
        self, 
        start_date: Optional[datetime] = None, 
        end_date: Optional[datetime] = None
    ) -> Dict[str, Any]:
        """Obtiene estadísticas generales de alertas."""
        pass

    @abstractmethod
    async def get_alert_counts_by_status(self) -> Dict[str, int]:
        """Obtiene conteo de alertas por estado."""
        pass

    @abstractmethod
    async def get_alert_counts_by_type(self) -> Dict[str, int]:
        """Obtiene conteo de alertas por tipo."""
        pass

    @abstractmethod
    async def get_alert_trends(
        self, 
        days: int = 30, 
        group_by: str = 'day'
    ) -> List[Dict[str, Any]]:
        """Obtiene tendencias de alertas en período específico."""
        pass

    @abstractmethod
    async def get_alert_response_time_stats(self) -> Dict[str, float]:
        """Calcula estadísticas de tiempo de respuesta."""
        pass

    @abstractmethod
    async def get_alerts_by_employee_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene estadísticas de alertas por empleado."""
        pass

    @abstractmethod
    async def get_alerts_by_project_stats(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene estadísticas de alertas por proyecto."""
        pass

    @abstractmethod
    async def get_critical_alerts_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de alertas críticas."""
        pass

    @abstractmethod
    async def get_performance_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de rendimiento del sistema de alertas."""
        pass

    # ==========================================
    # VALIDACIONES
    # ==========================================

    @abstractmethod
    async def validate_alert_data(self, alert_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida y normaliza datos de alerta."""
        pass

    @abstractmethod
    async def validate_bulk_data(self, alerts_data: List[Dict[str, Any]]) -> List[Dict[str, Any]]:
        """Valida datos de múltiples alertas."""
        pass

    @abstractmethod
    async def validate_update_data(self, update_data: Dict[str, Any]) -> Dict[str, Any]:
        """Valida datos para actualización de alerta."""
        pass