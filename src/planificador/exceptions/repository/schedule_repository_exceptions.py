# src/planificador/exceptions/repository/schedule_repository_exceptions.py
"""
Excepciones específicas para ScheduleRepository.

Este módulo define excepciones especializadas para operaciones del repositorio
de horarios, incluyendo errores de validación, consultas, estadísticas y
relaciones propias del agregado Schedule.
"""

from typing import Any, Dict, List, Optional, Union
from datetime import datetime, date

from ..base import (
    PlanificadorBaseException,
    ValidationError,
    NotFoundError,
    ConflictError,
    BusinessLogicError,
)
from ..domain import (
    ScheduleError,
    ScheduleNotFoundError,
    ScheduleValidationError,
    ScheduleTimeConflictError,
    ScheduleBusinessLogicError,
)
from .base_repository_exceptions import RepositoryError, RepositoryValidationError


# ============================================================================
# EXCEPCIONES ESPECÍFICAS DEL REPOSITORIO DE SCHEDULES
# ============================================================================

class ScheduleRepositoryError(RepositoryError):
    """Excepción base para errores del repositorio de horarios.

    Hereda de RepositoryError y añade contexto específico para operaciones
    de horarios, incluyendo información sobre el horario afectado.

    Parameters
    ----------
    message : str
        Mensaje descriptivo del error.
    operation : Optional[str]
        Operación del repositorio que falló (create, update, delete, query_*).
    schedule_id : Optional[Union[int, str]]
        Identificador del horario afectado, si aplica.
    """

    def __init__(
        self,
        message: str,
        operation: Optional[str] = None,
        schedule_id: Optional[Union[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        super().__init__(
            message,
            operation=operation,
            entity_type="Schedule",
            entity_id=str(schedule_id) if schedule_id is not None else None,
            **kwargs,
        )
        self.operation = operation
        self.schedule_id = schedule_id


class ScheduleQueryError(ScheduleRepositoryError):
    """Error en consultas específicas de horarios.

    Se lanza cuando una consulta especializada de horarios falla debido a
    parámetros inválidos o condiciones no soportadas.

    Parameters
    ----------
    query_type : str
        Tipo de consulta (p. ej., by_employee_and_date, overlaps_in_range).
    parameters : Dict[str, Any]
        Parámetros usados en la consulta.
    reason : str
        Razón del fallo de la consulta.
    """

    def __init__(
        self,
        query_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs: Any,
    ) -> None:
        message = f"Error en consulta '{query_type}': {reason}"
        super().__init__(message, operation=f"query_{query_type}", **kwargs)
        self.add_detail("query_parameters", parameters)
        self.add_detail("failure_reason", reason)
        self.query_type = query_type
        self.parameters = parameters


class ScheduleStatisticsError(ScheduleRepositoryError):
    """Error en generación de estadísticas de horarios.

    Se lanza cuando falla la generación de métricas, reportes o estadísticas
    relacionadas con horarios.
    """

    def __init__(
        self,
        statistic_type: str,
        parameters: Dict[str, Any],
        reason: str,
        **kwargs: Any,
    ) -> None:
        message = f"Error generando estadística '{statistic_type}': {reason}"
        super().__init__(message, operation=f"statistics_{statistic_type}", **kwargs)
        self.add_detail("statistic_type", statistic_type)
        self.add_detail("parameters", parameters)
        self.add_detail("failure_reason", reason)
        self.statistic_type = statistic_type
        self.parameters = parameters


class ScheduleValidationRepositoryError(ScheduleRepositoryError):
    """Error de validación específico del repositorio de horarios.

    Se lanza cuando los datos del horario no pasan las validaciones
    específicas del repositorio (diferentes a las validaciones de dominio).
    """

    def __init__(
        self,
        field: str,
        value: Any,
        reason: str,
        operation: Optional[str] = None,
        schedule_id: Optional[Union[int, str]] = None,
        **kwargs: Any,
    ) -> None:
        message = f"Error de validación en campo '{field}': {reason}"
        super().__init__(
            message,
            operation=operation,
            schedule_id=schedule_id,
            **kwargs,
        )
        self.add_detail("field", field)
        self.add_detail("invalid_value", value)
        self.add_detail("validation_reason", reason)
        self.field = field
        self.value = value
        self.reason = reason


class ScheduleRelationshipError(ScheduleRepositoryError):
    """Error en gestión de relaciones de horarios.

    Se lanza cuando falla la gestión de relaciones entre horarios y otras
    entidades (empleados, proyectos, equipos, etc.).
    """

    def __init__(
        self,
        relationship_type: str,
        schedule_id: Union[int, str],
        related_entity_type: str,
        related_entity_id: Optional[Union[int, str]] = None,
        reason: str = "Error en gestión de relación",
        **kwargs: Any,
    ) -> None:
        message = (
            f"Error en relación '{relationship_type}' del horario {schedule_id}"
        )
        if related_entity_id is not None:
            message += f" con {related_entity_type} {related_entity_id}"
        message += f": {reason}"

        super().__init__(
            message,
            operation=f"relationship_{relationship_type}",
            schedule_id=schedule_id,
            **kwargs,
        )
        self.add_detail("relationship_type", relationship_type)
        self.add_detail("related_entity_type", related_entity_type)
        self.add_detail("related_entity_id", related_entity_id)
        self.add_detail("failure_reason", reason)
        self.relationship_type = relationship_type
        self.related_entity_type = related_entity_type
        self.related_entity_id = related_entity_id


class ScheduleBulkOperationError(ScheduleRepositoryError):
    """Error en operaciones masivas de horarios.

    Se lanza cuando falla una operación que afecta múltiples horarios
    simultáneamente, proporcionando detalles de los elementos fallidos.
    """

    def __init__(
        self,
        operation_type: str,
        total_items: int,
        failed_items: List[Dict[str, Any]],
        reason: str,
        **kwargs: Any,
    ) -> None:
        failed_count = len(failed_items)
        success_count = total_items - failed_count
        message = (
            f"Operación masiva '{operation_type}' falló parcialmente: "
            f"{failed_count}/{total_items} elementos fallaron. {reason}"
        )
        super().__init__(message, operation=f"bulk_{operation_type}", **kwargs)
        self.add_detail("operation_type", operation_type)
        self.add_detail("total_items", total_items)
        self.add_detail("failed_items", failed_items)
        self.add_detail("success_count", success_count)
        self.add_detail("failure_reason", reason)
        self.operation_type = operation_type
        self.total_items = total_items
        self.failed_items = failed_items
        self.success_count = success_count


class ScheduleDateRangeError(ScheduleRepositoryError):
    """Error en operaciones con rangos de fechas/horas de horarios.

    Se lanza ante problemas con rangos de fechas/horas en consultas o
    validaciones relacionadas con horarios (disponibilidad, ventanas, etc.).
    """

    def __init__(
        self,
        start_date: Union[date, datetime],
        end_date: Union[date, datetime],
        operation: str,
        reason: str = "Rango de fechas/horas inválido",
        **kwargs: Any,
    ) -> None:
        message = (
            f"Error en rango temporal para {operation}: {reason}. "
            f"Rango: {start_date} - {end_date}"
        )
        super().__init__(message, operation=operation, **kwargs)
        self.add_detail(
            "start_date",
            start_date.isoformat() if hasattr(start_date, "isoformat") else str(start_date),
        )
        self.add_detail(
            "end_date",
            end_date.isoformat() if hasattr(end_date, "isoformat") else str(end_date),
        )
        self.add_detail("date_range_reason", reason)
        self.start_date = start_date
        self.end_date = end_date
        self.reason = reason


class ScheduleOverlapError(ScheduleRepositoryError):
    """Error específico para detección/manejo de solapamientos de horarios.

    Indica que se encontró un solapamiento no permitido entre horarios durante
    una operación del repositorio.
    """

    def __init__(
        self,
        start_datetime: datetime,
        end_datetime: datetime,
        employee_id: Optional[Union[int, str]] = None,
        schedule_id: Optional[Union[int, str]] = None,
        operation: str = "detect_overlap",
        reason: str = "Solapamiento de horarios detectado",
        **kwargs: Any,
    ) -> None:
        base = (
            f"Solapamiento de horario {start_datetime} - {end_datetime}"
        )
        if employee_id is not None:
            base += f" para empleado {employee_id}"
        message = f"{base}: {reason}"
        super().__init__(message, operation=operation, schedule_id=schedule_id, **kwargs)
        self.add_detail("start_datetime", start_datetime.isoformat())
        self.add_detail("end_datetime", end_datetime.isoformat())
        self.add_detail("employee_id", employee_id)
        self.add_detail("failure_reason", reason)
        self.employee_id = employee_id
        self.start_datetime = start_datetime
        self.end_datetime = end_datetime
        self.reason = reason


# ============================================================================
# FACTORÍAS PARA CREAR EXCEPCIONES
# ============================================================================

def create_schedule_query_error(
    query_type: str, parameters: Dict[str, Any], reason: str
) -> ScheduleQueryError:
    """Crea un ScheduleQueryError con detalles estandarizados."""
    return ScheduleQueryError(query_type=query_type, parameters=parameters, reason=reason)


def create_schedule_statistics_error(
    statistic_type: str, parameters: Dict[str, Any], reason: str
) -> ScheduleStatisticsError:
    """Crea un ScheduleStatisticsError con detalles estandarizados."""
    return ScheduleStatisticsError(
        statistic_type=statistic_type, parameters=parameters, reason=reason
    )


def create_schedule_validation_repository_error(
    field: str,
    value: Any,
    reason: str,
    operation: Optional[str] = None,
    schedule_id: Optional[Union[int, str]] = None,
) -> ScheduleValidationRepositoryError:
    """Crea un ScheduleValidationRepositoryError con detalles estandarizados."""
    return ScheduleValidationRepositoryError(
        field=field,
        value=value,
        reason=reason,
        operation=operation,
        schedule_id=schedule_id,
    )


def create_schedule_relationship_error(
    relationship_type: str,
    schedule_id: Union[int, str],
    related_entity_type: str,
    related_entity_id: Optional[Union[int, str]] = None,
    reason: str = "Error en gestión de relación",
) -> ScheduleRelationshipError:
    """Crea un ScheduleRelationshipError con detalles estandarizados."""
    return ScheduleRelationshipError(
        relationship_type=relationship_type,
        schedule_id=schedule_id,
        related_entity_type=related_entity_type,
        related_entity_id=related_entity_id,
        reason=reason,
    )


def create_schedule_bulk_operation_error(
    operation_type: str,
    total_items: int,
    failed_items: List[Dict[str, Any]],
    reason: str,
) -> ScheduleBulkOperationError:
    """Crea un ScheduleBulkOperationError con detalles estandarizados."""
    return ScheduleBulkOperationError(
        operation_type=operation_type,
        total_items=total_items,
        failed_items=failed_items,
        reason=reason,
    )


def create_schedule_date_range_error(
    start_date: Union[date, datetime],
    end_date: Union[date, datetime],
    operation: str,
    reason: str = "Rango de fechas/horas inválido",
) -> ScheduleDateRangeError:
    """Crea un ScheduleDateRangeError con detalles estandarizados."""
    return ScheduleDateRangeError(
        start_date=start_date, end_date=end_date, operation=operation, reason=reason
    )


def create_schedule_overlap_error(
    start_datetime: datetime,
    end_datetime: datetime,
    employee_id: Optional[Union[int, str]] = None,
    schedule_id: Optional[Union[int, str]] = None,
    operation: str = "detect_overlap",
    reason: str = "Solapamiento de horarios detectado",
) -> ScheduleOverlapError:
    """Crea un ScheduleOverlapError con detalles estandarizados."""
    return ScheduleOverlapError(
        start_datetime=start_datetime,
        end_datetime=end_datetime,
        employee_id=employee_id,
        schedule_id=schedule_id,
        operation=operation,
        reason=reason,
    )