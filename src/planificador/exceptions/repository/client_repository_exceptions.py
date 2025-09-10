# src/planificador/exceptions/repository/client_repository_exceptions.py
"""
Excepciones específicas para ClientRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de clientes, incluyendo errores específicos de validación, consultas y lógica de negocio.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from ..domain import ClientError, ClientNotFoundError, ClientValidationError, ClientConflictError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE CLIENTES
# ============================================================================

class ClientRepositoryError(RepositoryError):
    """
    Excepción base para errores del repositorio de clientes.
    
    Hereda de RepositoryError y añade contexto específico para operaciones
    de clientes, incluyendo información sobre el cliente afectado.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        client_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            operation=operation,
            entity_type="Client",
            entity_id=str(client_id) if client_id else None,
            **kwargs
        )
        self.operation = operation
        self.client_id = client_id


class ClientQueryError(ClientRepositoryError):
    """
    Error en consultas específicas de clientes.
    
    Se lanza cuando una consulta especializada de clientes falla
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
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('query_parameters', parameters)
        self.add_detail('failure_reason', reason)
        
        self.query_type = query_type
        self.parameters = parameters


class ClientStatisticsError(ClientRepositoryError):
    """
    Error en generación de estadísticas de clientes.
    
    Se lanza cuando falla la generación de métricas, reportes
    o estadísticas relacionadas con clientes.
    """
    
    def __init__(
        self, 
        statistic_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs
    ):
        message = f"Error generando estadística '{statistic_type}': {reason}"
        
        super().__init__(
            message,
            operation=f"statistics_{statistic_type}",
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('statistic_parameters', parameters)
        self.add_detail('failure_reason', reason)
        
        self.statistic_type = statistic_type
        self.parameters = parameters


class ClientValidationRepositoryError(ClientRepositoryError):
    """
    Error de validación específico del repositorio de clientes.
    
    Extiende ClientRepositoryError con información específica de validación,
    proporcionando contexto tanto de la operación de repositorio
    como de la validación específica de clientes.
    """
    
    def __init__(
        self, 
        field: str,
        value: Any,
        reason: str,
        operation: Optional[str] = None,
        client_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        # Construir mensaje incluyendo la operación si está disponible
        if operation:
            message = f"Validación fallida para cliente en operación '{operation}' para campo '{field}': {reason}"
        else:
            message = f"Validación fallida para cliente en campo '{field}': {reason}"
        
        # Inicializar ClientRepositoryError
        super().__init__(message=message, operation=operation, client_id=client_id, **kwargs)
        
        # Agregar atributos específicos de validación
        self.field = field
        self.value = value
        self.reason = reason


class ClientRelationshipError(ClientRepositoryError):
    """
    Error en gestión de relaciones de clientes.
    
    Se lanza cuando fallan operaciones relacionadas con las relaciones
    entre clientes y otras entidades (proyectos, empleados, etc.).
    """
    
    def __init__(
        self, 
        relationship_type: str,
        client_id: Union[int, str],
        related_entity_type: str,
        related_entity_id: Optional[Union[int, str]] = None,
        reason: str = "Error en gestión de relación",
        **kwargs
    ):
        message = f"Error en relación '{relationship_type}' del cliente {client_id}: {reason}"
        
        super().__init__(message, **kwargs)
        
        # Agregar detalles específicos usando add_detail
        self.add_detail("operation", f"relationship_{relationship_type}")
        self.add_detail("client_id", str(client_id))
        self.add_detail("relationship_type", relationship_type)
        self.add_detail("related_entity_type", related_entity_type)
        self.add_detail("related_entity_id", str(related_entity_id) if related_entity_id else None)
        self.add_detail("failure_reason", reason)
        
        # Mantener atributos para compatibilidad
        self.relationship_type = relationship_type
        self.related_entity_type = related_entity_type
        self.related_entity_id = related_entity_id


class ClientBulkOperationError(ClientRepositoryError):
    """
    Error en operaciones masivas de clientes.
    
    Se lanza cuando fallan operaciones que afectan múltiples clientes
    como creación, actualización o eliminación en lote.
    """
    
    def __init__(
        self, 
        operation_type: str,
        total_items: int,
        failed_items: List[Dict[str, Any]],
        reason: str,
        **kwargs
    ):
        message = f"Error en operación masiva '{operation_type}': {len(failed_items)}/{total_items} elementos fallaron. {reason}"
        
        super().__init__(
            message,
            operation=f"bulk_{operation_type}",
            **kwargs
        )
        # Establecer atributos específicos de la operación masiva
        self.operation_type = operation_type
        self.total_items = total_items
        self.failed_items = failed_items
        self.failed_count = len(failed_items)
        self.failure_reason = reason
        
        # Agregar detalles adicionales
        self.add_detail('total_items', total_items)
        self.add_detail('failed_count', len(failed_items))
        self.add_detail('failed_items', failed_items)
        self.add_detail('failure_reason', reason)


class ClientDateRangeError(ClientRepositoryError):
    """
    Error en operaciones con rangos de fechas de clientes.
    
    Se lanza cuando las consultas o operaciones con rangos de fechas
    tienen parámetros inválidos o producen resultados inconsistentes.
    """
    
    def __init__(
        self, 
        start_date: datetime,
        end_date: datetime,
        operation: str,
        reason: str = "Rango de fechas inválido",
        **kwargs
    ):
        message = f"Error en rango de fechas para operación '{operation}': {reason}"
        
        super().__init__(message, **kwargs)
        
        # Agregar detalles específicos usando add_detail
        self.add_detail("operation", operation)
        self.add_detail("start_date", start_date.isoformat() if start_date else None)
        self.add_detail("end_date", end_date.isoformat() if end_date else None)
        self.add_detail("failure_reason", reason)
        
        self.start_date = start_date
        self.end_date = end_date


# ============================================================================
# FUNCIONES HELPER PARA CREAR EXCEPCIONES
# ============================================================================

def create_client_query_error(
    query_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> ClientQueryError:
    """
    Crea una excepción ClientQueryError con los parámetros especificados.
    
    Args:
        query_type: Tipo de consulta que falló
        parameters: Parámetros de la consulta
        reason: Razón del fallo
        
    Returns:
        Instancia de ClientQueryError
    """
    return ClientQueryError(
        query_type=query_type,
        parameters=parameters,
        reason=reason
    )


def create_client_statistics_error(
    statistic_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> ClientStatisticsError:
    """
    Crea una excepción ClientStatisticsError con los parámetros especificados.
    
    Args:
        statistic_type: Tipo de estadística que falló
        parameters: Parámetros de la estadística
        reason: Razón del fallo
        
    Returns:
        Instancia de ClientStatisticsError
    """
    return ClientStatisticsError(
        statistic_type=statistic_type,
        parameters=parameters,
        reason=reason
    )


def create_client_validation_repository_error(
    field: str,
    value: Any,
    reason: str,
    operation: Optional[str] = None,
    client_id: Optional[Union[int, str]] = None
) -> ClientValidationRepositoryError:
    """
    Crea una excepción ClientValidationRepositoryError con los parámetros especificados.
    
    Args:
        field: Campo que falló la validación
        value: Valor que causó el fallo
        reason: Razón del fallo de validación
        operation: Operación que se estaba realizando
        client_id: ID del cliente afectado
        
    Returns:
        Instancia de ClientValidationRepositoryError
    """
    return ClientValidationRepositoryError(
        field=field,
        value=value,
        reason=reason,
        operation=operation,
        client_id=client_id
    )


def create_client_relationship_error(
    relationship_type: str,
    client_id: Union[int, str],
    related_entity_type: str,
    related_entity_id: Optional[Union[int, str]] = None,
    reason: str = "Error en gestión de relación"
) -> ClientRelationshipError:
    """
    Crea una excepción ClientRelationshipError con los parámetros especificados.
    
    Args:
        relationship_type: Tipo de relación
        client_id: ID del cliente
        related_entity_type: Tipo de entidad relacionada
        related_entity_id: ID de la entidad relacionada
        reason: Razón del fallo
        
    Returns:
        Instancia de ClientRelationshipError
    """
    return ClientRelationshipError(
        relationship_type=relationship_type,
        client_id=client_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        reason=reason
    )


def create_client_bulk_operation_error(
    operation_type: str,
    total_items: int,
    failed_items: List[Dict[str, Any]],
    reason: str
) -> ClientBulkOperationError:
    """
    Crea una excepción ClientBulkOperationError con los parámetros especificados.
    
    Args:
        operation_type: Tipo de operación masiva
        total_items: Total de elementos procesados
        failed_items: Lista de elementos que fallaron
        reason: Razón del fallo
        
    Returns:
        Instancia de ClientBulkOperationError
    """
    return ClientBulkOperationError(
        operation_type=operation_type,
        total_items=total_items,
        failed_items=failed_items,
        reason=reason
    )


def create_client_date_range_error(
    start_date: datetime,
    end_date: datetime,
    operation: str,
    reason: str = "Rango de fechas inválido"
) -> ClientDateRangeError:
    """
    Crea una excepción ClientDateRangeError con los parámetros especificados.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        
    Returns:
        Instancia de ClientDateRangeError
    """
    return ClientDateRangeError(
        start_date=start_date,
        end_date=end_date,
        operation=operation,
        reason=reason
    )