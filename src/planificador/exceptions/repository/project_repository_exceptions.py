# src/planificador/exceptions/repository/project_repository_exceptions.py
"""
Excepciones específicas para ProjectRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de proyectos, incluyendo errores específicos de validación, consultas, estadísticas
y lógica de negocio relacionada con proyectos.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE PROYECTOS
# ============================================================================

class ProjectRepositoryError(RepositoryError):
    """
    Excepción base para errores del repositorio de proyectos.
    
    Hereda de RepositoryError y añade contexto específico para operaciones
    de proyectos, incluyendo información sobre el proyecto afectado.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        project_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        super().__init__(
            message,
            operation=operation,
            entity_type="Project",
            entity_id=str(project_id) if project_id else None,
            **kwargs
        )
        # Nota: self.operation se accede a través de la propiedad heredada
        self.project_id = project_id


class ProjectQueryError(ProjectRepositoryError):
    """
    Error en consultas específicas de proyectos.
    
    Se lanza cuando una consulta especializada de proyectos falla
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


class ProjectStatisticsError(ProjectRepositoryError):
    """
    Error en generación de estadísticas de proyectos.
    
    Se lanza cuando falla la generación de métricas, reportes
    o estadísticas relacionadas con proyectos.
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


class ProjectValidationRepositoryError(ProjectRepositoryError):
    """
    Error de validación específico del repositorio de proyectos.
    
    Se lanza cuando la validación de datos de proyecto falla
    en el contexto específico del repositorio.
    """
    
    def __init__(
        self, 
        field: str,
        value: Any,
        reason: str,
        operation: Optional[str] = None,
        project_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error de validación en campo '{field}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            project_id=project_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('invalid_field', field)
        self.add_detail('invalid_value', value)
        self.add_detail('validation_reason', reason)
        
        self.field = field
        self.value = value


class ProjectRelationshipError(ProjectRepositoryError):
    """
    Error en gestión de relaciones de proyectos.
    
    Se lanza cuando falla la gestión de relaciones entre proyectos
    y otras entidades como clientes, empleados o equipos.
    """
    
    def __init__(
        self, 
        relationship_type: str,
        project_id: Union[int, str],
        related_entity_type: str,
        related_entity_id: Optional[Union[int, str]] = None,
        reason: str = "Error en gestión de relación",
        **kwargs
    ):
        message = f"Error en relación '{relationship_type}' del proyecto {project_id}"
        if related_entity_id:
            message += f" con {related_entity_type} {related_entity_id}"
        message += f": {reason}"
        
        super().__init__(
            message,
            operation=f"relationship_{relationship_type}",
            project_id=project_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('relationship_type', relationship_type)
        self.add_detail('related_entity_type', related_entity_type)
        self.add_detail('related_entity_id', related_entity_id)
        self.add_detail('failure_reason', reason)
        
        self.relationship_type = relationship_type
        self.related_entity_type = related_entity_type
        self.related_entity_id = related_entity_id


class ProjectBulkOperationError(ProjectRepositoryError):
    """
    Error en operaciones masivas de proyectos.
    
    Se lanza cuando falla una operación que afecta múltiples proyectos
    simultáneamente, proporcionando detalles sobre qué elementos fallaron.
    """
    
    def __init__(
        self, 
        operation_type: str,
        total_items: int,
        failed_items: List[Dict[str, Any]],
        reason: str,
        **kwargs
    ):
        failed_count = len(failed_items)
        success_count = total_items - failed_count
        
        message = f"Operación masiva '{operation_type}' falló parcialmente: {failed_count}/{total_items} elementos fallaron. {reason}"
        
        super().__init__(
            message,
            operation=f"bulk_{operation_type}",
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('total_items', total_items)
        self.add_detail('failed_items', failed_items)
        self.add_detail('success_count', success_count)
        self.add_detail('failure_reason', reason)
        
        self.operation_type = operation_type
        self.total_items = total_items
        self.failed_items = failed_items
        self.success_count = success_count


class ProjectDateRangeError(ProjectRepositoryError):
    """
    Error en operaciones con rangos de fechas de proyectos.
    
    Se lanza cuando se proporcionan rangos de fechas inválidos
    para consultas o operaciones relacionadas con proyectos.
    """
    
    def __init__(
        self, 
        start_date: Union[date, datetime],
        end_date: Union[date, datetime],
        operation: str,
        reason: str = "Rango de fechas inválido",
        **kwargs
    ):
        message = f"Error en rango de fechas para operación '{operation}': {reason}"
        
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


class ProjectReferenceError(ProjectRepositoryError):
    """
    Error específico de referencias de proyectos.
    
    Se lanza cuando hay problemas con la referencia única del proyecto,
    como duplicados o formatos inválidos.
    """
    
    def __init__(
        self, 
        reference: str,
        operation: str,
        reason: str,
        project_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error con referencia '{reference}' en operación '{operation}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            project_id=project_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('reference', reference)
        self.add_detail('failure_reason', reason)
        
        self.reference = reference


class ProjectTrigramError(ProjectRepositoryError):
    """
    Error específico de trigramas de proyectos.
    
    Se lanza cuando hay problemas con el trigrama único del proyecto,
    como duplicados o formatos inválidos.
    """
    
    def __init__(
        self, 
        trigram: str,
        operation: str,
        reason: str,
        project_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error con trigrama '{trigram}' en operación '{operation}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            project_id=project_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('trigram', trigram)
        self.add_detail('failure_reason', reason)
        
        self.trigram = trigram


class ProjectWorkloadError(ProjectRepositoryError):
    """
    Error en operaciones de carga de trabajo de proyectos.
    
    Se lanza cuando hay problemas con la gestión de cargas de trabajo
    asociadas a proyectos, como cálculos de estadísticas o asignaciones.
    """
    
    def __init__(
        self, 
        workload_data: Any,
        operation: str,
        reason: str,
        project_id: Optional[Union[int, str]] = None,
        **kwargs
    ):
        message = f"Error en carga de trabajo para operación '{operation}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            project_id=project_id,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('workload_data', workload_data)
        self.add_detail('failure_reason', reason)
        
        self.workload_data = workload_data


# ============================================================================
# FUNCIONES FACTORY PARA CREAR EXCEPCIONES
# ============================================================================

def create_project_query_error(
    query_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> ProjectQueryError:
    """
    Crea una excepción ProjectQueryError con parámetros estandarizados.
    
    Args:
        query_type: Tipo de consulta que falló
        parameters: Parámetros de la consulta
        reason: Razón del fallo
        
    Returns:
        Instancia de ProjectQueryError
    """
    return ProjectQueryError(
        query_type=query_type,
        parameters=parameters,
        reason=reason
    )


def create_project_statistics_error(
    statistic_type: str,
    parameters: Dict[str, Any],
    reason: str
) -> ProjectStatisticsError:
    """
    Crea una excepción ProjectStatisticsError con parámetros estandarizados.
    
    Args:
        statistic_type: Tipo de estadística que falló
        parameters: Parámetros de la estadística
        reason: Razón del fallo
        
    Returns:
        Instancia de ProjectStatisticsError
    """
    return ProjectStatisticsError(
        statistic_type=statistic_type,
        parameters=parameters,
        reason=reason
    )


def create_project_validation_repository_error(
    field: str,
    value: Any,
    reason: str,
    operation: Optional[str] = None,
    project_id: Optional[Union[int, str]] = None
) -> ProjectValidationRepositoryError:
    """
    Crea una excepción ProjectValidationRepositoryError con parámetros estandarizados.
    
    Args:
        field: Campo que falló la validación
        value: Valor inválido
        reason: Razón del fallo
        operation: Operación que se estaba realizando
        project_id: ID del proyecto afectado
        
    Returns:
        Instancia de ProjectValidationRepositoryError
    """
    return ProjectValidationRepositoryError(
        field=field,
        value=value,
        reason=reason,
        operation=operation,
        project_id=project_id
    )


def create_project_relationship_error(
    relationship_type: str,
    project_id: Union[int, str],
    related_entity_type: str,
    related_entity_id: Optional[Union[int, str]] = None,
    reason: str = "Error en gestión de relación"
) -> ProjectRelationshipError:
    """
    Crea una excepción ProjectRelationshipError con parámetros estandarizados.
    
    Args:
        relationship_type: Tipo de relación
        project_id: ID del proyecto
        related_entity_type: Tipo de entidad relacionada
        related_entity_id: ID de la entidad relacionada
        reason: Razón del fallo
        
    Returns:
        Instancia de ProjectRelationshipError
    """
    return ProjectRelationshipError(
        relationship_type=relationship_type,
        project_id=project_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        reason=reason
    )


def create_project_bulk_operation_error(
    operation_type: str,
    total_items: int,
    failed_items: List[Dict[str, Any]],
    reason: str
) -> ProjectBulkOperationError:
    """
    Crea una excepción ProjectBulkOperationError con parámetros estandarizados.
    
    Args:
        operation_type: Tipo de operación masiva
        total_items: Total de elementos procesados
        failed_items: Lista de elementos que fallaron
        reason: Razón del fallo
        
    Returns:
        Instancia de ProjectBulkOperationError
    """
    return ProjectBulkOperationError(
        operation_type=operation_type,
        total_items=total_items,
        failed_items=failed_items,
        reason=reason
    )


def create_project_date_range_error(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
    operation: str,
    reason: str = "Rango de fechas inválido"
) -> ProjectDateRangeError:
    """
    Crea una excepción ProjectDateRangeError con parámetros estandarizados.
    
    Args:
        start_date: Fecha de inicio
        end_date: Fecha de fin
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        
    Returns:
        Instancia de ProjectDateRangeError
    """
    return ProjectDateRangeError(
        start_date=start_date,
        end_date=end_date,
        operation=operation,
        reason=reason
    )


def create_project_reference_error(
    reference: str,
    operation: str,
    reason: str,
    project_id: Optional[Union[int, str]] = None
) -> ProjectReferenceError:
    """
    Crea una excepción ProjectReferenceError con parámetros estandarizados.
    
    Args:
        reference: Referencia del proyecto
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        project_id: ID del proyecto afectado
        
    Returns:
        Instancia de ProjectReferenceError
    """
    return ProjectReferenceError(
        reference=reference,
        operation=operation,
        reason=reason,
        project_id=project_id
    )


def create_project_trigram_error(
    trigram: str,
    operation: str,
    reason: str,
    project_id: Optional[Union[int, str]] = None
) -> ProjectTrigramError:
    """
    Crea una excepción ProjectTrigramError con parámetros estandarizados.
    
    Args:
        trigram: Trigrama del proyecto
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        project_id: ID del proyecto afectado
        
    Returns:
        Instancia de ProjectTrigramError
    """
    return ProjectTrigramError(
        trigram=trigram,
        operation=operation,
        reason=reason,
        project_id=project_id
    )


def create_project_workload_error(
    workload_data: Any,
    operation: str,
    reason: str,
    project_id: Optional[Union[int, str]] = None
) -> ProjectWorkloadError:
    """
    Crea una excepción ProjectWorkloadError con parámetros estandarizados.
    
    Args:
        workload_data: Datos de carga de trabajo
        operation: Operación que se estaba realizando
        reason: Razón del fallo
        project_id: ID del proyecto afectado
        
    Returns:
        Instancia de ProjectWorkloadError
    """
    return ProjectWorkloadError(
        workload_data=workload_data,
        operation=operation,
        reason=reason,
        project_id=project_id
    )