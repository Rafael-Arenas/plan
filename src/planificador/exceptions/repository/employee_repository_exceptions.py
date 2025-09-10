# src/planificador/exceptions/repository/employee_repository_exceptions.py
"""
Excepciones específicas para EmployeeRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de empleados, incluyendo errores específicos de validación, consultas, estadísticas
y lógica de negocio relacionada con empleados.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from ..domain import EmployeeError, EmployeeNotFoundError, EmployeeValidationError, EmployeeConflictError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE EMPLEADOS
# ============================================================================

class EmployeeRepositoryError(RepositoryError):
    """
    Excepción base para errores del repositorio de empleados.
    
    Hereda de RepositoryError y añade contexto específico para operaciones
    de empleados, incluyendo información sobre el empleado afectado.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        employee_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            operation=operation,
            entity_type="Employee",
            entity_id=str(employee_id) if employee_id else None,
            **kwargs
        )
        self.operation = operation
        self.employee_id = employee_id


class EmployeeQueryError(EmployeeRepositoryError):
    """
    Error en consultas específicas de empleados.
    
    Se lanza cuando una consulta especializada de empleados falla
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


class EmployeeStatisticsError(EmployeeRepositoryError):
    """
    Error en generación de estadísticas de empleados.
    
    Se lanza cuando falla la generación de métricas, reportes
    o estadísticas relacionadas con empleados.
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
        
        # Agregar detalles específicos
        self.add_detail('statistic_type', statistic_type)
        self.add_detail('parameters', parameters)
        self.add_detail('failure_reason', reason)
        
        self.statistic_type = statistic_type
        self.parameters = parameters


class EmployeeValidationRepositoryError(EmployeeRepositoryError):
    """
    Error de validación específico del repositorio de empleados.
    
    Se lanza cuando los datos del empleado no pasan las validaciones
    específicas del repositorio (diferentes a las validaciones de dominio).
    """
    
    def __init__(
        self, 
        field: str,
        value: Any,
        reason: str,
        operation: Optional[str] = None,
        employee_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error de validación en campo '{field}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            employee_id=employee_id,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('field', field)
        self.add_detail('invalid_value', value)
        self.add_detail('validation_reason', reason)
        
        self.field = field
        self.value = value
        self.reason = reason


class EmployeeRelationshipError(EmployeeRepositoryError):
    """
    Error en gestión de relaciones de empleados.
    
    Se lanza cuando falla la gestión de relaciones entre empleados
    y otras entidades (equipos, proyectos, vacaciones, etc.).
    """
    
    def __init__(
        self, 
        relationship_type: str,
        employee_id: Union[int, str],
        related_entity_type: str,
        related_entity_id: Optional[Union[int, str]] = None,
        reason: str = "Error en gestión de relación",
        **kwargs
    ):
        message = f"Error en relación '{relationship_type}' entre empleado {employee_id} y {related_entity_type}"
        if related_entity_id:
            message += f" {related_entity_id}"
        message += f": {reason}"
        
        super().__init__(
            message,
            operation=f"relationship_{relationship_type}",
            employee_id=employee_id,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('relationship_type', relationship_type)
        self.add_detail('related_entity_type', related_entity_type)
        self.add_detail('related_entity_id', related_entity_id)
        
        self.relationship_type = relationship_type
        self.related_entity_type = related_entity_type
        self.related_entity_id = related_entity_id


class EmployeeBulkOperationError(EmployeeRepositoryError):
    """
    Error en operaciones masivas de empleados.
    
    Se lanza cuando falla una operación que afecta múltiples empleados
    (creación masiva, actualización masiva, etc.).
    """
    
    def __init__(
        self, 
        operation_type: str,
        total_items: int,
        failed_items: List[Dict[str, Any]],
        reason: str,
        **kwargs
    ):
        success_count = total_items - len(failed_items)
        message = f"Operación masiva '{operation_type}' falló parcialmente: {success_count}/{total_items} exitosos. {reason}"
        
        super().__init__(
            message,
            operation=f"bulk_{operation_type}",
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('operation_type', operation_type)
        self.add_detail('total_items', total_items)
        self.add_detail('failed_items', failed_items)
        self.add_detail('success_count', success_count)
        
        self.operation_type = operation_type
        self.total_items = total_items
        self.failed_items = failed_items
        self.success_count = success_count


class EmployeeDateRangeError(EmployeeRepositoryError):
    """
    Error en operaciones con rangos de fechas de empleados.
    
    Se lanza cuando hay problemas con rangos de fechas en consultas
    o validaciones relacionadas con empleados (fechas de contratación,
    períodos de vacaciones, etc.).
    """
    
    def __init__(
        self, 
        start_date: Union[date, datetime],
        end_date: Union[date, datetime],
        operation: str,
        reason: str = "Rango de fechas inválido",
        **kwargs
    ):
        message = f"Error en rango de fechas para {operation}: {reason}. Rango: {start_date} - {end_date}"
        
        super().__init__(
            message,
            operation=operation,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('start_date', start_date.isoformat() if hasattr(start_date, 'isoformat') else str(start_date))
        self.add_detail('end_date', end_date.isoformat() if hasattr(end_date, 'isoformat') else str(end_date))
        self.add_detail('date_range_reason', reason)
        
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason


class EmployeeSkillsError(EmployeeRepositoryError):
    """
    Error específico para operaciones con habilidades de empleados.
    
    Se lanza cuando hay problemas con la gestión de habilidades
    de empleados (formato JSON inválido, habilidades duplicadas, etc.).
    """
    
    def __init__(
        self, 
        skills_data: Any,
        operation: str,
        reason: str,
        employee_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error en habilidades para {operation}: {reason}"
        
        super().__init__(
            message,
            operation=operation,
            employee_id=employee_id,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('skills_data', skills_data)
        self.add_detail('skills_error_reason', reason)
        
        self.skills_data = skills_data
        self.reason = reason


class EmployeeAvailabilityError(EmployeeRepositoryError):
    """
    Error en consultas de disponibilidad de empleados.
    
    Se lanza cuando hay problemas al determinar la disponibilidad
    de empleados en fechas específicas.
    """
    
    def __init__(
        self, 
        target_date: Union[date, datetime],
        employee_id: Optional[Union[int, str]] = None,
        reason: str = "Error determinando disponibilidad",
        **kwargs
    ):
        message = f"Error de disponibilidad para fecha {target_date}: {reason}"
        if employee_id:
            message = f"Error de disponibilidad del empleado {employee_id} para fecha {target_date}: {reason}"
        
        super().__init__(
            message,
            operation="check_availability",
            employee_id=employee_id,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('target_date', target_date.isoformat() if hasattr(target_date, 'isoformat') else str(target_date))
        self.add_detail('availability_reason', reason)
        
        self.target_date = target_date
        self.reason = reason


# ============================================================================
# FUNCIONES FACTORY PARA CREAR EXCEPCIONES
# ============================================================================

def create_employee_query_error(
    query_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> EmployeeQueryError:
    """
    Crea una excepción de error de consulta de empleados.
    
    Args:
        query_type: Tipo de consulta que falló
        parameters: Parámetros de la consulta
        reason: Razón del fallo
        
    Returns:
        Instancia de EmployeeQueryError
    """
    return EmployeeQueryError(
        query_type=query_type,
        parameters=parameters,
        reason=reason
    )


def create_employee_statistics_error(
    statistic_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> EmployeeStatisticsError:
    """
    Crea una excepción de error de estadísticas de empleados.
    
    Args:
        statistic_type: Tipo de estadística que falló
        parameters: Parámetros de la estadística
        reason: Razón del fallo
        
    Returns:
        Instancia de EmployeeStatisticsError
    """
    return EmployeeStatisticsError(
        statistic_type=statistic_type,
        parameters=parameters,
        reason=reason
    )


def create_employee_validation_repository_error(
    field: str,
    value: Any,
    reason: str,
    operation: Optional[str] = None,
    employee_id: Optional[Union[int, str]] = None
) -> EmployeeValidationRepositoryError:
    """
    Crea una excepción de error de validación del repositorio de empleados.
    
    Args:
        field: Campo que falló la validación
        value: Valor inválido
        reason: Razón de la falla
        operation: Operación que se estaba realizando
        employee_id: ID del empleado afectado
        
    Returns:
        Instancia de EmployeeValidationRepositoryError
    """
    return EmployeeValidationRepositoryError(
        field=field,
        value=value,
        reason=reason,
        operation=operation,
        employee_id=employee_id
    )


def create_employee_relationship_error(
    relationship_type: str,
    employee_id: Union[int, str],
    related_entity_type: str,
    related_entity_id: Optional[Union[int, str]] = None,
    reason: str = "Error en gestión de relación"
) -> EmployeeRelationshipError:
    """
    Crea una excepción de error de relación de empleados.
    
    Args:
        relationship_type: Tipo de relación
        employee_id: ID del empleado
        related_entity_type: Tipo de entidad relacionada
        related_entity_id: ID de la entidad relacionada
        reason: Razón del error
        
    Returns:
        Instancia de EmployeeRelationshipError
    """
    return EmployeeRelationshipError(
        relationship_type=relationship_type,
        employee_id=employee_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        reason=reason
    )


def create_employee_bulk_operation_error(
    operation_type: str,
    total_items: int,
    failed_items: List[Dict[str, Any]],
    reason: str
) -> EmployeeBulkOperationError:
    """
    Crea una excepción de error de operación masiva de empleados.
    
    Args:
        operation_type: Tipo de operación masiva
        total_items: Total de elementos procesados
        failed_items: Lista de elementos que fallaron
        reason: Razón del fallo
        
    Returns:
        Instancia de EmployeeBulkOperationError
    """
    return EmployeeBulkOperationError(
        operation_type=operation_type,
        total_items=total_items,
        failed_items=failed_items,
        reason=reason
    )


def create_employee_date_range_error(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
    operation: str,
    reason: str = "Rango de fechas inválido"
) -> EmployeeDateRangeError:
    """
    Crea una excepción de error de rango de fechas de empleados.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        operation: Operación que se estaba realizando
        reason: Razón del error
        
    Returns:
        Instancia de EmployeeDateRangeError
    """
    return EmployeeDateRangeError(
        start_date=start_date,
        end_date=end_date,
        operation=operation,
        reason=reason
    )


def create_employee_skills_error(
    skills_data: Any,
    operation: str,
    reason: str,
    employee_id: Optional[Union[int, str]] = None
) -> EmployeeSkillsError:
    """
    Crea una excepción de error de habilidades de empleados.
    
    Args:
        skills_data: Datos de habilidades problemáticos
        operation: Operación que se estaba realizando
        reason: Razón del error
        employee_id: ID del empleado afectado
        
    Returns:
        Instancia de EmployeeSkillsError
    """
    return EmployeeSkillsError(
        skills_data=skills_data,
        operation=operation,
        reason=reason,
        employee_id=employee_id
    )


def create_employee_availability_error(
    target_date: Union[date, datetime],
    employee_id: Optional[Union[int, str]] = None,
    reason: str = "Error determinando disponibilidad"
) -> EmployeeAvailabilityError:
    """
    Crea una excepción de error de disponibilidad de empleados.
    
    Args:
        target_date: Fecha objetivo para verificar disponibilidad
        employee_id: ID del empleado
        reason: Razón del error
        
    Returns:
        Instancia de EmployeeAvailabilityError
    """
    return EmployeeAvailabilityError(
        target_date=target_date,
        employee_id=employee_id,
        reason=reason
    )