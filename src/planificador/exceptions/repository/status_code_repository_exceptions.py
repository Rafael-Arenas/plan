# src/planificador/exceptions/repository/status_code_repository_exceptions.py
"""
Excepciones específicas para StatusCodeRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de códigos de estado, incluyendo errores específicos de validación, consultas
y lógica de negocio relacionada con códigos de estado.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime

from ..base import PlanificadorBaseException, ValidationError, NotFoundError, ConflictError, BusinessLogicError
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE CÓDIGOS DE ESTADO
# ============================================================================

class StatusCodeRepositoryError(RepositoryError):
    """
    Excepción base para errores del repositorio de códigos de estado.
    
    Hereda de RepositoryError y añade contexto específico para operaciones
    de códigos de estado, incluyendo información sobre el código afectado.
    """
    
    def __init__(
        self, 
        message: str,
        operation: Optional[str] = None,
        status_code_id: Optional[Union[int, str]] = None,
        status_code: Optional[str] = None,
        **kwargs
    ):
        super().__init__(
            message,
            operation=operation,
            entity_type="StatusCode",
            entity_id=str(status_code_id) if status_code_id else None,
            **kwargs
        )
        # Nota: self.operation se accede a través de la propiedad heredada
        self.status_code_id = status_code_id
        self.status_code = status_code


class StatusCodeDuplicateError(StatusCodeRepositoryError):
    """
    Error cuando se intenta crear un código de estado con un código ya existente.
    
    Se lanza cuando se viola la restricción de unicidad del campo 'code'
    en la tabla status_codes.
    """
    
    def __init__(
        self, 
        code: str,
        existing_id: Optional[int] = None,
        operation: str = "create",
        **kwargs
    ):
        message = f"El código de estado '{code}' ya existe en el sistema"
        if existing_id:
            message += f" (ID: {existing_id})"
        
        super().__init__(
            message,
            operation=operation,
            status_code=code,
            **kwargs
        )
        
        # Agregar detalles específicos usando add_detail()
        self.add_detail('duplicate_code', code)
        if existing_id:
            self.add_detail('existing_id', existing_id)
        
        self.code = code
        self.existing_id = existing_id


class StatusCodeNotFoundError(StatusCodeRepositoryError):
    """
    Error cuando no se encuentra un código de estado específico.
    
    Se lanza cuando una búsqueda por código, ID o criterios específicos
    no retorna ningún resultado.
    """
    
    def __init__(
        self, 
        identifier: Union[int, str],
        search_type: str = "id",
        operation: str = "get",
        **kwargs
    ):
        if search_type == "code":
            message = f"Código de estado con código '{identifier}' no encontrado"
        elif search_type == "id":
            message = f"Código de estado con ID {identifier} no encontrado"
        else:
            message = f"Código de estado no encontrado ({search_type}: {identifier})"
        
        super().__init__(
            message,
            operation=operation,
            status_code_id=identifier if search_type == "id" else None,
            status_code=identifier if search_type == "code" else None,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('search_identifier', str(identifier))
        self.add_detail('search_type', search_type)
        
        self.identifier = identifier
        self.search_type = search_type


class StatusCodeValidationError(StatusCodeRepositoryError):
    """
    Error de validación específico para códigos de estado.
    
    Se lanza cuando los datos del código de estado no cumplen
    con las reglas de validación del dominio.
    """
    
    def __init__(
        self, 
        field: str,
        value: Any,
        reason: str,
        operation: Optional[str] = None,
        status_code: Optional[str] = None,
        **kwargs
    ):
        message = f"Validación fallida para campo '{field}': {reason}"
        
        super().__init__(
            message,
            operation=operation,
            status_code=status_code,
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('validation_field', field)
        self.add_detail('invalid_value', value)
        self.add_detail('validation_reason', reason)
        
        self.field = field
        self.value = value
        self.reason = reason


class StatusCodeOrderingError(StatusCodeRepositoryError):
    """
    Error en operaciones de ordenamiento de códigos de estado.
    
    Se lanza cuando falla la reordenación de códigos de estado
    o cuando hay conflictos en los valores de sort_order.
    """
    
    def __init__(
        self, 
        operation_type: str,
        affected_codes: List[str],
        reason: str,
        **kwargs
    ):
        message = f"Error en ordenamiento ({operation_type}): {reason}"
        
        super().__init__(
            message,
            operation=f"ordering_{operation_type}",
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('ordering_operation', operation_type)
        self.add_detail('affected_codes', affected_codes)
        self.add_detail('failure_reason', reason)
        
        self.operation_type = operation_type
        self.affected_codes = affected_codes


class StatusCodeFilterError(StatusCodeRepositoryError):
    """
    Error en operaciones de filtrado de códigos de estado.
    
    Se lanza cuando los criterios de filtrado son inválidos
    o cuando la consulta de filtrado falla.
    """
    
    def __init__(
        self, 
        filter_criteria: Dict[str, Any],
        reason: str,
        **kwargs
    ):
        message = f"Error en filtrado de códigos de estado: {reason}"
        
        super().__init__(
            message,
            operation="filter_by_criteria",
            **kwargs
        )
        
        # Agregar detalles específicos
        self.add_detail('filter_criteria', filter_criteria)
        self.add_detail('failure_reason', reason)
        
        self.filter_criteria = filter_criteria


class StatusCodeStatisticsError(StatusCodeRepositoryError):
    """
    Error en generación de estadísticas de códigos de estado.
    
    Se lanza cuando falla la generación de métricas, reportes
    o estadísticas relacionadas con códigos de estado.
    """
    
    def __init__(
        self, 
        statistic_type: str,
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
        self.add_detail('failure_reason', reason)
        
        self.statistic_type = statistic_type


# ============================================================================
# FUNCIONES HELPER PARA CREACIÓN DE EXCEPCIONES
# ============================================================================

def create_status_code_duplicate_error(
    code: str,
    existing_id: Optional[int] = None,
    operation: str = "create"
) -> StatusCodeDuplicateError:
    """
    Crea una excepción de código duplicado.
    
    Args:
        code: Código que está duplicado
        existing_id: ID del código existente
        operation: Operación que causó el error
        
    Returns:
        StatusCodeDuplicateError configurada
    """
    return StatusCodeDuplicateError(
        code=code,
        existing_id=existing_id,
        operation=operation
    )


def create_status_code_not_found_error(
    identifier: Union[int, str],
    search_type: str = "id",
    operation: str = "get"
) -> StatusCodeNotFoundError:
    """
    Crea una excepción de código de estado no encontrado.
    
    Args:
        identifier: Identificador buscado
        search_type: Tipo de búsqueda ("id", "code")
        operation: Operación que causó el error
        
    Returns:
        StatusCodeNotFoundError configurada
    """
    return StatusCodeNotFoundError(
        identifier=identifier,
        search_type=search_type,
        operation=operation
    )


def create_status_code_validation_error(
    field: str,
    value: Any,
    reason: str,
    operation: Optional[str] = None,
    status_code: Optional[str] = None
) -> StatusCodeValidationError:
    """
    Crea una excepción de validación de código de estado.
    
    Args:
        field: Campo que falló la validación
        value: Valor inválido
        reason: Razón de la falla
        operation: Operación que causó el error
        status_code: Código de estado afectado
        
    Returns:
        StatusCodeValidationError configurada
    """
    return StatusCodeValidationError(
        field=field,
        value=value,
        reason=reason,
        operation=operation,
        status_code=status_code
    )


def create_status_code_ordering_error(
    operation_type: str,
    affected_codes: List[str],
    reason: str
) -> StatusCodeOrderingError:
    """
    Crea una excepción de ordenamiento de códigos de estado.
    
    Args:
        operation_type: Tipo de operación de ordenamiento
        affected_codes: Códigos afectados
        reason: Razón del error
        
    Returns:
        StatusCodeOrderingError configurada
    """
    return StatusCodeOrderingError(
        operation_type=operation_type,
        affected_codes=affected_codes,
        reason=reason
    )


def create_status_code_filter_error(
    filter_criteria: Dict[str, Any],
    reason: str
) -> StatusCodeFilterError:
    """
    Crea una excepción de filtrado de códigos de estado.
    
    Args:
        filter_criteria: Criterios de filtrado que fallaron
        reason: Razón del error
        
    Returns:
        StatusCodeFilterError configurada
    """
    return StatusCodeFilterError(
        filter_criteria=filter_criteria,
        reason=reason
    )


def create_status_code_statistics_error(
    statistic_type: str,
    reason: str
) -> StatusCodeStatisticsError:
    """
    Crea una excepción de estadísticas de códigos de estado.
    
    Args:
        statistic_type: Tipo de estadística que falló
        reason: Razón del error
        
    Returns:
        StatusCodeStatisticsError configurada
    """
    return StatusCodeStatisticsError(
        statistic_type=statistic_type,
        reason=reason
    )