# src/planificador/exceptions/repository/vacation_repository_exceptions.py

from typing import Optional, Any, List, Union
from datetime import date
from .base_repository_exceptions import RepositoryError


class VacationRepositoryError(RepositoryError):
    """
    Excepción base para errores específicos del repositorio de vacaciones.
    
    Hereda de RepositoryError y proporciona contexto específico
    para operaciones relacionadas con vacaciones.
    """
    pass


class VacationQueryError(VacationRepositoryError):
    """
    Excepción para errores en consultas de vacaciones.
    
    Se lanza cuando ocurren errores durante la ejecución
    de consultas específicas de vacaciones.
    """
    pass


class VacationStatisticsError(VacationRepositoryError):
    """
    Excepción para errores en cálculos estadísticos de vacaciones.
    
    Se lanza cuando ocurren errores durante el cálculo
    de estadísticas relacionadas con vacaciones.
    """
    pass


class VacationValidationRepositoryError(VacationRepositoryError):
    """
    Excepción para errores de validación en el repositorio de vacaciones.
    
    Se lanza cuando los datos de vacación no cumplen con
    las reglas de validación del repositorio.
    """
    pass


class VacationRelationshipError(VacationRepositoryError):
    """
    Excepción para errores en relaciones de vacaciones.
    
    Se lanza cuando ocurren errores al gestionar relaciones
    entre vacaciones y otras entidades (empleados, equipos, etc.).
    """
    pass


class VacationBulkOperationError(VacationRepositoryError):
    """
    Excepción para errores en operaciones masivas de vacaciones.
    
    Se lanza cuando ocurren errores durante operaciones
    que afectan múltiples vacaciones simultáneamente.
    """
    pass


class VacationDateRangeError(VacationRepositoryError):
    """
    Excepción para errores relacionados con rangos de fechas de vacaciones.
    
    Se lanza cuando ocurren errores con fechas inválidas,
    solapamientos o conflictos de fechas.
    """
    pass


class VacationBalanceError(VacationRepositoryError):
    """
    Excepción para errores relacionados con el balance de vacaciones.
    
    Se lanza cuando ocurren errores al calcular o validar
    el balance de días de vacaciones de un empleado.
    """
    pass


class VacationApprovalError(VacationRepositoryError):
    """
    Excepción para errores en procesos de aprobación de vacaciones.
    
    Se lanza cuando ocurren errores durante los procesos
    de aprobación, rechazo o cancelación de vacaciones.
    """
    pass


# Factory functions para crear excepciones con contexto enriquecido

def create_vacation_query_error(
    message: str,
    operation: str,
    vacation_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationQueryError:
    """
    Crea una excepción VacationQueryError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        vacation_id: ID de la vacación relacionada (opcional)
        employee_id: ID del empleado relacionado (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationQueryError configurada
    """
    return VacationQueryError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        entity_id=vacation_id,
        original_error=original_error,
        context={
            "vacation_id": vacation_id,
            "employee_id": employee_id,
            **kwargs
        }
    )


def create_vacation_statistics_error(
    message: str,
    operation: str,
    employee_id: Optional[int] = None,
    team_id: Optional[int] = None,
    calculation_type: Optional[str] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationStatisticsError:
    """
    Crea una excepción VacationStatisticsError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        employee_id: ID del empleado relacionado (opcional)
        team_id: ID del equipo relacionado (opcional)
        calculation_type: Tipo de cálculo estadístico (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationStatisticsError configurada
    """
    return VacationStatisticsError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        original_error=original_error,
        context={
            "employee_id": employee_id,
            "team_id": team_id,
            "calculation_type": calculation_type,
            **kwargs
        }
    )


def create_vacation_validation_repository_error(
    message: str,
    operation: str,
    vacation_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    validation_field: Optional[str] = None,
    validation_value: Optional[Any] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationValidationRepositoryError:
    """
    Crea una excepción VacationValidationRepositoryError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        vacation_id: ID de la vacación relacionada (opcional)
        employee_id: ID del empleado relacionado (opcional)
        validation_field: Campo que falló la validación (opcional)
        validation_value: Valor que falló la validación (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationValidationRepositoryError configurada
    """
    return VacationValidationRepositoryError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        entity_id=vacation_id,
        original_error=original_error,
        context={
            "vacation_id": vacation_id,
            "employee_id": employee_id,
            "validation_field": validation_field,
            "validation_value": validation_value,
            **kwargs
        }
    )


def create_vacation_relationship_error(
    message: str,
    operation: str,
    vacation_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationRelationshipError:
    """
    Crea una excepción VacationRelationshipError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        vacation_id: ID de la vacación relacionada (opcional)
        related_entity_type: Tipo de entidad relacionada (opcional)
        related_entity_id: ID de la entidad relacionada (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationRelationshipError configurada
    """
    return VacationRelationshipError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        entity_id=vacation_id,
        original_error=original_error,
        context={
            "vacation_id": vacation_id,
            "related_entity_type": related_entity_type,
            "related_entity_id": related_entity_id,
            **kwargs
        }
    )


def create_vacation_bulk_operation_error(
    message: str,
    operation: str,
    affected_vacations: Optional[List[int]] = None,
    successful_count: Optional[int] = None,
    failed_count: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationBulkOperationError:
    """
    Crea una excepción VacationBulkOperationError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        affected_vacations: Lista de IDs de vacaciones afectadas (opcional)
        successful_count: Número de operaciones exitosas (opcional)
        failed_count: Número de operaciones fallidas (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationBulkOperationError configurada
    """
    return VacationBulkOperationError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        original_error=original_error,
        context={
            "affected_vacations": affected_vacations,
            "successful_count": successful_count,
            "failed_count": failed_count,
            **kwargs
        }
    )


def create_vacation_date_range_error(
    message: str,
    operation: str,
    start_date: Optional[date] = None,
    end_date: Optional[date] = None,
    vacation_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationDateRangeError:
    """
    Crea una excepción VacationDateRangeError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        start_date: Fecha de inicio (opcional)
        end_date: Fecha de fin (opcional)
        vacation_id: ID de la vacación relacionada (opcional)
        employee_id: ID del empleado relacionado (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationDateRangeError configurada
    """
    return VacationDateRangeError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        entity_id=vacation_id,
        original_error=original_error,
        context={
            "start_date": start_date.isoformat() if start_date else None,
            "end_date": end_date.isoformat() if end_date else None,
            "vacation_id": vacation_id,
            "employee_id": employee_id,
            **kwargs
        }
    )


def create_vacation_balance_error(
    message: str,
    operation: str,
    employee_id: Optional[int] = None,
    balance_type: Optional[str] = None,
    requested_days: Optional[float] = None,
    available_days: Optional[float] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationBalanceError:
    """
    Crea una excepción VacationBalanceError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        employee_id: ID del empleado relacionado (opcional)
        balance_type: Tipo de balance (opcional)
        requested_days: Días solicitados (opcional)
        available_days: Días disponibles (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationBalanceError configurada
    """
    return VacationBalanceError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        original_error=original_error,
        context={
            "employee_id": employee_id,
            "balance_type": balance_type,
            "requested_days": requested_days,
            "available_days": available_days,
            **kwargs
        }
    )


def create_vacation_approval_error(
    message: str,
    operation: str,
    vacation_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    approver_id: Optional[int] = None,
    current_status: Optional[str] = None,
    target_status: Optional[str] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> VacationApprovalError:
    """
    Crea una excepción VacationApprovalError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        vacation_id: ID de la vacación relacionada (opcional)
        employee_id: ID del empleado relacionado (opcional)
        approver_id: ID del aprobador (opcional)
        current_status: Estado actual de la vacación (opcional)
        target_status: Estado objetivo de la vacación (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de VacationApprovalError configurada
    """
    return VacationApprovalError(
        message=message,
        operation=operation,
        entity_type="Vacation",
        entity_id=vacation_id,
        original_error=original_error,
        context={
            "vacation_id": vacation_id,
            "employee_id": employee_id,
            "approver_id": approver_id,
            "current_status": current_status,
            "target_status": target_status,
            **kwargs
        }
    )