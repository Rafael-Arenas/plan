# src/planificador/exceptions/repository/alert_repository_exceptions.py
"""
Excepciones específicas para AlertRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de alertas, incluyendo errores específicos de validación, estado y lógica de negocio.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from ..domain import AlertError, AlertNotFoundError, AlertConflictError, AlertBusinessLogicError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE ALERTAS
# ============================================================================

class AlertRepositoryError(RepositoryError):
    """
    Excepción base para errores específicos del repositorio de alertas.
    
    Hereda de RepositoryError y proporciona contexto específico
    para operaciones de alertas.
    """
    
    def __init__(self, message: str, operation: Optional[str] = None, **kwargs):
        super().__init__(message, operation=operation, entity_type="Alert", **kwargs)


class AlertStateTransitionError(AlertRepositoryError):
    """
    Error en transiciones de estado de alertas.
    
    Se lanza cuando se intenta realizar una transición de estado inválida
    o cuando el estado actual no permite la operación solicitada.
    """
    
    def __init__(
        self, 
        current_state: str, 
        target_state: str, 
        alert_id: Optional[int] = None,
        **kwargs
    ):
        message = f"Transición de estado inválida: {current_state} -> {target_state}"
        if alert_id:
            message += f" para alerta ID {alert_id}"
        
        super().__init__(
            message, 
            operation="state_transition",
            **kwargs
        )
        
        # Atributos específicos
        self.current_state = current_state
        self.target_state = target_state
        self.alert_id = alert_id
        
        # Agregar detalles específicos
        self.add_detail('current_state', current_state)
        self.add_detail('target_state', target_state)
        if alert_id:
            self.add_detail('alert_id', alert_id)


class AlertBulkOperationError(AlertRepositoryError):
    """
    Error en operaciones en lote de alertas.
    
    Se lanza cuando falla una operación que afecta múltiples alertas,
    proporcionando información sobre qué alertas fallaron.
    """
    
    def __init__(
        self, 
        operation: str,
        failed_alert_ids: List[int],
        total_alerts: int,
        error_details: Optional[Dict[int, str]] = None,
        **kwargs
    ):
        message = f"Operación en lote '{operation}' falló para {len(failed_alert_ids)}/{total_alerts} alertas"
        
        super().__init__(
            message,
            operation=f"bulk_{operation}",
            **kwargs
        )
        
        # Atributos específicos
        self.operation_type = operation
        self.failed_alert_ids = failed_alert_ids
        self.total_alerts = total_alerts
        self.error_details = error_details or {}
        
        # Agregar detalles específicos
        self.add_detail('operation_type', operation)
        self.add_detail('failed_alert_ids', failed_alert_ids)
        self.add_detail('total_alerts', total_alerts)
        self.add_detail('failed_count', len(failed_alert_ids))
        if error_details:
            self.add_detail('error_details', error_details)


class AlertQueryError(AlertRepositoryError):
    """
    Error en consultas específicas de alertas.
    
    Se lanza cuando una consulta especializada de alertas falla
    debido a parámetros inválidos o condiciones no soportadas.
    """
    
    def __init__(
        self, 
        query_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs
    ):
        message = f"Error en consulta '{query_type}': {reason}"
        
        super().__init__(
            message,
            operation=f"query_{query_type}",
            **kwargs
        )
        
        # Atributos específicos
        self.query_type = query_type
        self.parameters = parameters
        self.reason = reason
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('query_type', query_type)
        self.add_detail('query_parameters', parameters)
        self.add_detail('failure_reason', reason)


class AlertStatisticsError(AlertRepositoryError):
    """
    Error en cálculo de estadísticas de alertas.
    
    Se lanza cuando falla el cálculo de métricas, tendencias
    o estadísticas relacionadas con alertas.
    """
    
    def __init__(
        self, 
        statistic_type: str,
        parameters: Optional[Dict[str, Any]] = None,
        reason: Optional[str] = None,
        original_error: Optional[Exception] = None,
        **kwargs
    ):
        message = f"Error calculando estadística '{statistic_type}'"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            operation=f"statistics_{statistic_type}",
            original_error=original_error,
            **kwargs
        )
        
        # Atributos específicos
        self.statistic_type = statistic_type
        self.parameters = parameters or {}
        self.reason = reason
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('statistic_type', statistic_type)
        self.add_detail('statistic_parameters', parameters or {})
        if reason:
            self.add_detail('failure_reason', reason)


class AlertValidationRepositoryError(AlertRepositoryError):
    """
    Error de validación específico del repositorio de alertas.
    
    Proporciona información detallada sobre qué validación falló
    en el contexto del repositorio de alertas.
    """
    
    def __init__(
        self, 
        field: str,
        value: Any,
        validation_rule: str,
        alert_data: Optional[Dict[str, Any]] = None,
        **kwargs
    ):
        message = f"Validación fallida en repositorio para campo '{field}': {validation_rule}"
        
        # Inicializar AlertRepositoryError
        super().__init__(
            message,
            operation="validation",
            **kwargs
        )
        
        # Atributos específicos
        self.field = field
        self.value = value
        self.validation_rule = validation_rule
        self.alert_data = alert_data or {}
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('field', field)
        self.add_detail('value', value)
        self.add_detail('validation_rule', validation_rule)
        self.add_detail('alert_data', alert_data or {})


class AlertRelationshipError(AlertRepositoryError):
    """
    Error en relaciones de alertas con otras entidades.
    
    Se lanza cuando hay problemas con las relaciones entre alertas
    y otras entidades como empleados, proyectos, etc.
    """
    
    def __init__(
        self, 
        relationship_type: str,
        entity_id: Union[int, str],
        alert_id: Optional[int] = None,
        reason: Optional[str] = None,
        **kwargs
    ):
        message = f"Error en relación '{relationship_type}' con entidad ID {entity_id}"
        if alert_id:
            message += f" para alerta ID {alert_id}"
        if reason:
            message += f": {reason}"
        
        super().__init__(
            message,
            operation="relationship_validation",
            **kwargs
        )
        
        # Atributos específicos
        self.relationship_type = relationship_type
        self.entity_id = str(entity_id)
        self.alert_id = alert_id
        self.reason = reason
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('relationship_type', relationship_type)
        self.add_detail('entity_id', str(entity_id))
        if alert_id:
            self.add_detail('alert_id', alert_id)
        if reason:
            self.add_detail('failure_reason', reason)


class AlertDateRangeError(AlertRepositoryError):
    """
    Error en validación de rangos de fechas para alertas.
    
    Se lanza cuando los rangos de fechas proporcionados para
    consultas o filtros de alertas son inválidos.
    """
    
    def __init__(
        self, 
        start_date: Optional[datetime],
        end_date: Optional[datetime],
        reason: str,
        **kwargs
    ):
        message = f"Rango de fechas inválido: {reason}"
        if start_date and end_date:
            message += f" (desde {start_date} hasta {end_date})"
        
        super().__init__(
            message,
            operation="date_range_validation",
            **kwargs
        )
        
        # Atributos específicos
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('start_date', start_date.isoformat() if start_date else None)
        self.add_detail('end_date', end_date.isoformat() if end_date else None)
        self.add_detail('failure_reason', reason)


# ============================================================================
# FUNCIONES HELPER PARA CREACIÓN DE EXCEPCIONES
# ============================================================================

def create_alert_state_transition_error(
    current_state: str, 
    target_state: str, 
    alert_id: Optional[int] = None
) -> AlertStateTransitionError:
    """
    Crea una excepción de transición de estado de alerta.
    
    Args:
        current_state: Estado actual de la alerta
        target_state: Estado objetivo de la transición
        alert_id: ID de la alerta (opcional)
        
    Returns:
        Instancia de AlertStateTransitionError
    """
    return AlertStateTransitionError(current_state, target_state, alert_id)


def create_alert_bulk_operation_error(
    operation: str,
    failed_alert_ids: List[int],
    total_alerts: int,
    error_details: Optional[Dict[int, str]] = None
) -> AlertBulkOperationError:
    """
    Crea una excepción de operación en lote de alertas.
    
    Args:
        operation: Nombre de la operación que falló
        failed_alert_ids: Lista de IDs de alertas que fallaron
        total_alerts: Número total de alertas en la operación
        error_details: Detalles específicos de errores por alerta
        
    Returns:
        Instancia de AlertBulkOperationError
    """
    return AlertBulkOperationError(operation, failed_alert_ids, total_alerts, error_details)


def create_alert_query_error(
    query_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> AlertQueryError:
    """
    Crea una excepción de consulta de alertas.
    
    Args:
        query_type: Tipo de consulta que falló
        parameters: Parámetros de la consulta
        reason: Razón del fallo
        
    Returns:
        Instancia de AlertQueryError
    """
    return AlertQueryError(query_type, parameters, reason)


def create_alert_statistics_error(
    statistic_type: str,
    parameters: Optional[Dict[str, Any]] = None,
    reason: Optional[str] = None,
    original_error: Optional[Exception] = None
) -> AlertStatisticsError:
    """
    Crea una excepción de estadísticas de alertas.
    
    Args:
        statistic_type: Tipo de estadística que falló
        parameters: Parámetros de la estadística
        reason: Razón del fallo
        original_error: Excepción original que causó el error
        
    Returns:
        Instancia de AlertStatisticsError
    """
    return AlertStatisticsError(
        statistic_type=statistic_type, 
        parameters=parameters, 
        reason=reason, 
        original_error=original_error
    )


def create_alert_validation_repository_error(
    field: str,
    value: Any,
    validation_rule: str,
    alert_data: Optional[Dict[str, Any]] = None
) -> AlertValidationRepositoryError:
    """
    Crea una excepción de validación específica del repositorio de alertas.
    
    Args:
        field: Campo que falló la validación
        value: Valor que causó el fallo
        validation_rule: Regla de validación que falló
        alert_data: Datos completos de la alerta
        
    Returns:
        Instancia de AlertValidationRepositoryError
    """
    return AlertValidationRepositoryError(field, value, validation_rule, alert_data)


def create_alert_relationship_error(
    relationship_type: str,
    entity_id: Union[int, str],
    alert_id: Optional[int] = None,
    reason: Optional[str] = None
) -> AlertRelationshipError:
    """
    Crea una excepción de relación de alertas.
    
    Args:
        relationship_type: Tipo de relación que falló
        entity_id: ID de la entidad relacionada
        alert_id: ID de la alerta
        reason: Razón del fallo
        
    Returns:
        Instancia de AlertRelationshipError
    """
    return AlertRelationshipError(relationship_type, entity_id, alert_id, reason)


def create_alert_date_range_error(
    start_date: Optional[datetime],
    end_date: Optional[datetime],
    reason: str
) -> AlertDateRangeError:
    """
    Crea una excepción de rango de fechas de alertas.
    
    Args:
        start_date: Fecha de inicio del rango
        end_date: Fecha de fin del rango
        reason: Razón del fallo
        
    Returns:
        Instancia de AlertDateRangeError
    """
    return AlertDateRangeError(start_date, end_date, reason)