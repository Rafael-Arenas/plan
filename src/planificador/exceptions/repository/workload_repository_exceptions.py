# src/planificador/exceptions/repository/workload_repository_exceptions.py
"""
Excepciones específicas para WorkloadRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de cargas de trabajo, incluyendo errores específicos de validación, consultas,
estadísticas y lógica de negocio relacionada con workloads.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date
from decimal import Decimal

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from ..domain import WorkloadError, WorkloadNotFoundError, WorkloadValidationError, WorkloadBusinessLogicError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE WORKLOADS
# ============================================================================

class WorkloadRepositoryError(RepositoryError):
    """
    Excepción base para errores del repositorio de cargas de trabajo.
    
    Hereda de RepositoryError y añade contexto específico para operaciones
    de workloads, incluyendo información sobre la carga de trabajo afectada.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        workload_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            operation=operation,
            entity_type="Workload",
            entity_id=str(workload_id) if workload_id else None,
            **kwargs
        )
        self.operation = operation
        self.workload_id = workload_id


class WorkloadQueryError(WorkloadRepositoryError):
    """
    Error en consultas de cargas de trabajo.
    
    Se lanza cuando hay problemas específicos en la construcción o ejecución
    de consultas relacionadas con cargas de trabajo.
    """
    
    def __init__(
        self, 
        query_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs
    ):
        message = f"Error en consulta de workload '{query_type}': {reason}"
        
        super().__init__(
            message,
            operation=f"query_{query_type}",
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('query_type', query_type)
        self.add_detail('query_parameters', parameters)
        self.add_detail('failure_reason', reason)
        
        self.query_type = query_type
        self.parameters = parameters


class WorkloadStatisticsError(WorkloadRepositoryError):
    """
    Error en cálculos estadísticos de cargas de trabajo.
    
    Se lanza cuando hay problemas en el cálculo de estadísticas,
    métricas o agregaciones relacionadas con cargas de trabajo.
    """
    
    def __init__(
        self, 
        statistic_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs
    ):
        message = f"Error calculando estadística de workload '{statistic_type}': {reason}"
        
        super().__init__(
            message,
            operation=f"calculate_{statistic_type}",
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('statistic_type', statistic_type)
        self.add_detail('calculation_parameters', parameters)
        self.add_detail('failure_reason', reason)
        
        self.statistic_type = statistic_type
        self.parameters = parameters


class WorkloadValidationRepositoryError(WorkloadRepositoryError, RepositoryValidationError):
    """
    Error de validación específico del repositorio de cargas de trabajo.
    
    Se lanza cuando los datos de workload no cumplen con las reglas
    de validación específicas del repositorio.
    """
    
    def __init__(
        self, 
        validation_type: str,
        invalid_data: Any,
        reason: str,
        workload_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error de validación de workload '{validation_type}': {reason}"
        
        super().__init__(
            message,
            operation=f"validate_{validation_type}",
            workload_id=workload_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('validation_type', validation_type)
        self.add_detail('invalid_data', invalid_data)
        self.add_detail('validation_reason', reason)
        
        self.validation_type = validation_type
        self.invalid_data = invalid_data


class WorkloadRelationshipError(WorkloadRepositoryError):
    """
    Error en operaciones de relaciones de cargas de trabajo.
    
    Se lanza cuando hay problemas con las relaciones entre workloads
    y otras entidades como empleados, proyectos o equipos.
    """
    
    def __init__(
        self, 
        relationship_type: str,
        related_entity_id: Union[int, str],
        operation: str,
        reason: str,
        workload_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error en relación de workload '{relationship_type}' durante '{operation}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            workload_id=workload_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('relationship_type', relationship_type)
        self.add_detail('related_entity_id', related_entity_id)
        self.add_detail('failure_reason', reason)
        
        self.relationship_type = relationship_type
        self.related_entity_id = related_entity_id


class WorkloadBulkOperationError(WorkloadRepositoryError):
    """
    Error en operaciones masivas de cargas de trabajo.
    
    Se lanza cuando hay problemas en operaciones que afectan
    múltiples workloads simultáneamente.
    """
    
    def __init__(
        self, 
        operation_type: str,
        affected_count: int,
        total_count: int,
        reason: str,
        failed_items: Optional[List[Any]] = None,
        **kwargs
    ):
        message = f"Error en operación masiva de workload '{operation_type}': {reason} ({affected_count}/{total_count} afectados)"
        
        super().__init__(
            message,
            operation=f"bulk_{operation_type}",
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('operation_type', operation_type)
        self.add_detail('affected_count', affected_count)
        self.add_detail('total_count', total_count)
        self.add_detail('failure_reason', reason)
        if failed_items:
            self.add_detail('failed_items', failed_items)
        
        self.operation_type = operation_type
        self.affected_count = affected_count
        self.total_count = total_count
        self.failed_items = failed_items or []


class WorkloadDateRangeError(WorkloadRepositoryError):
    """
    Error en operaciones con rangos de fechas de cargas de trabajo.
    
    Se lanza cuando hay problemas con rangos de fechas inválidos
    o inconsistentes en operaciones de workload.
    """
    
    def __init__(
        self, 
        start_date: Optional[date],
        end_date: Optional[date],
        operation: str,
        reason: str,
        **kwargs
    ):
        date_range = f"{start_date} - {end_date}" if start_date and end_date else "rango inválido"
        message = f"Error en rango de fechas de workload durante '{operation}': {reason} (Rango: {date_range})"
        
        super().__init__(
            message,
            operation=operation,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('start_date', start_date.isoformat() if start_date else None)
        self.add_detail('end_date', end_date.isoformat() if end_date else None)
        self.add_detail('failure_reason', reason)
        
        self.start_date = start_date
        self.end_date = end_date


class WorkloadCapacityError(WorkloadRepositoryError):
    """
    Error en operaciones de capacidad de cargas de trabajo.
    
    Se lanza cuando hay problemas con cálculos de capacidad,
    sobrecarga o subutilización de empleados.
    """
    
    def __init__(
        self, 
        capacity_type: str,
        threshold_value: Union[float, Decimal],
        actual_value: Union[float, Decimal],
        employee_id: Optional[Union[int, str]] = None,
        operation: str = "capacity_check",
        **kwargs
    ):
        message = f"Error de capacidad de workload '{capacity_type}': valor {actual_value} vs umbral {threshold_value}"
        
        super().__init__(
            message,
            operation=operation,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('capacity_type', capacity_type)
        self.add_detail('threshold_value', float(threshold_value))
        self.add_detail('actual_value', float(actual_value))
        if employee_id:
            self.add_detail('employee_id', employee_id)
        
        self.capacity_type = capacity_type
        self.threshold_value = threshold_value
        self.actual_value = actual_value
        self.employee_id = employee_id


# ============================================================================
# FUNCIONES FACTORY PARA CREAR EXCEPCIONES
# ============================================================================

def create_workload_query_error(
    query_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> WorkloadQueryError:
    """
    Crea una excepción WorkloadQueryError con parámetros estandarizados.
    
    Args:
        query_type: Tipo de consulta que falló
        parameters: Parámetros de la consulta
        reason: Razón del fallo
        
    Returns:
        Instancia de WorkloadQueryError
    """
    return WorkloadQueryError(
        query_type=query_type,
        parameters=parameters,
        reason=reason
    )


def create_workload_statistics_error(
    statistic_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> WorkloadStatisticsError:
    """
    Crea una excepción WorkloadStatisticsError con parámetros estandarizados.
    
    Args:
        statistic_type: Tipo de estadística que falló
        parameters: Parámetros del cálculo
        reason: Razón del fallo
        
    Returns:
        Instancia de WorkloadStatisticsError
    """
    return WorkloadStatisticsError(
        statistic_type=statistic_type,
        parameters=parameters,
        reason=reason
    )


def create_workload_validation_repository_error(
    validation_type: str,
    invalid_data: Any,
    reason: str,
    workload_id: Optional[Union[int, str]] = None
) -> WorkloadValidationRepositoryError:
    """
    Crea una excepción WorkloadValidationRepositoryError con parámetros estandarizados.
    
    Args:
        validation_type: Tipo de validación que falló
        invalid_data: Datos que no pasaron la validación
        reason: Razón del fallo
        workload_id: ID del workload afectado
        
    Returns:
        Instancia de WorkloadValidationRepositoryError
    """
    return WorkloadValidationRepositoryError(
        validation_type=validation_type,
        invalid_data=invalid_data,
        reason=reason,
        workload_id=workload_id
    )


def create_workload_relationship_error(
    relationship_type: str,
    related_entity_id: Union[int, str],
    operation: str,
    reason: str,
    workload_id: Optional[Union[int, str]] = None
) -> WorkloadRelationshipError:
    """
    Crea una excepción WorkloadRelationshipError con parámetros estandarizados.
    
    Args:
        relationship_type: Tipo de relación afectada
        related_entity_id: ID de la entidad relacionada
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        workload_id: ID del workload afectado
        
    Returns:
        Instancia de WorkloadRelationshipError
    """
    return WorkloadRelationshipError(
        relationship_type=relationship_type,
        related_entity_id=related_entity_id,
        operation=operation,
        reason=reason,
        workload_id=workload_id
    )


def create_workload_bulk_operation_error(
    operation_type: str,
    affected_count: int,
    total_count: int,
    reason: str,
    failed_items: Optional[List[Any]] = None
) -> WorkloadBulkOperationError:
    """
    Crea una excepción WorkloadBulkOperationError con parámetros estandarizados.
    
    Args:
        operation_type: Tipo de operación masiva
        affected_count: Número de elementos afectados
        total_count: Número total de elementos
        reason: Razón del fallo
        failed_items: Lista de elementos que fallaron
        
    Returns:
        Instancia de WorkloadBulkOperationError
    """
    return WorkloadBulkOperationError(
        operation_type=operation_type,
        affected_count=affected_count,
        total_count=total_count,
        reason=reason,
        failed_items=failed_items
    )


def create_workload_date_range_error(
    start_date: Optional[date],
    end_date: Optional[date],
    operation: str,
    reason: str
) -> WorkloadDateRangeError:
    """
    Crea una excepción WorkloadDateRangeError con parámetros estandarizados.
    
    Args:
        start_date: Fecha de inicio del rango
        end_date: Fecha de fin del rango
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        
    Returns:
        Instancia de WorkloadDateRangeError
    """
    return WorkloadDateRangeError(
        start_date=start_date,
        end_date=end_date,
        operation=operation,
        reason=reason
    )


def create_workload_capacity_error(
    capacity_type: str,
    threshold_value: Union[float, Decimal],
    actual_value: Union[float, Decimal],
    employee_id: Optional[Union[int, str]] = None,
    operation: str = "capacity_check"
) -> WorkloadCapacityError:
    """
    Crea una excepción WorkloadCapacityError con parámetros estandarizados.
    
    Args:
        capacity_type: Tipo de capacidad (overload, underutilized, etc.)
        threshold_value: Valor umbral
        actual_value: Valor actual
        employee_id: ID del empleado afectado
        operation: Operación que se estaba realizando
        
    Returns:
        Instancia de WorkloadCapacityError
    """
    return WorkloadCapacityError(
        capacity_type=capacity_type,
        threshold_value=threshold_value,
        actual_value=actual_value,
        employee_id=employee_id,
        operation=operation
    )