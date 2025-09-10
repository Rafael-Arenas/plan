# src/planificador/exceptions/repository/team_repository_exceptions.py

from typing import Optional, Any
from .base_repository_exceptions import RepositoryError


class TeamRepositoryError(RepositoryError):
    """
    Excepción base para errores específicos del repositorio de equipos.
    
    Hereda de RepositoryError y proporciona contexto específico
    para operaciones relacionadas con equipos.
    """
    pass


class TeamQueryError(TeamRepositoryError):
    """
    Excepción para errores en consultas de equipos.
    
    Se lanza cuando ocurren errores durante la ejecución
    de consultas específicas de equipos.
    """
    pass


class TeamStatisticsError(TeamRepositoryError):
    """
    Excepción para errores en cálculos estadísticos de equipos.
    
    Se lanza cuando ocurren errores durante el cálculo
    de estadísticas relacionadas con equipos.
    """
    pass


class TeamValidationRepositoryError(TeamRepositoryError):
    """
    Excepción para errores de validación en el repositorio de equipos.
    
    Se lanza cuando los datos del equipo no cumplen con
    las reglas de validación del repositorio.
    """
    pass


class TeamRelationshipError(TeamRepositoryError):
    """
    Excepción para errores en relaciones de equipos.
    
    Se lanza cuando ocurren errores al gestionar relaciones
    entre equipos y otras entidades (empleados, proyectos, etc.).
    """
    pass


class TeamBulkOperationError(TeamRepositoryError):
    """
    Excepción para errores en operaciones masivas de equipos.
    
    Se lanza cuando ocurren errores durante operaciones
    que afectan múltiples equipos simultáneamente.
    """
    pass


class TeamMembershipError(TeamRepositoryError):
    """
    Excepción para errores en membresías de equipos.
    
    Se lanza cuando ocurren errores al gestionar
    la pertenencia de empleados a equipos.
    """
    pass


class TeamCapacityError(TeamRepositoryError):
    """
    Excepción para errores relacionados con la capacidad del equipo.
    
    Se lanza cuando ocurren errores al calcular o validar
    la capacidad de trabajo de un equipo.
    """
    pass


# Factory functions para crear excepciones con contexto enriquecido

def create_team_query_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    project_id: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamQueryError:
    """
    Crea una excepción TeamQueryError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        employee_id: ID del empleado relacionado (opcional)
        project_id: ID del proyecto relacionado (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamQueryError configurada
    """
    return TeamQueryError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "employee_id": employee_id,
            "project_id": project_id,
            **kwargs
        }
    )


def create_team_statistics_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    calculation_type: Optional[str] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamStatisticsError:
    """
    Crea una excepción TeamStatisticsError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        calculation_type: Tipo de cálculo estadístico (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamStatisticsError configurada
    """
    return TeamStatisticsError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "calculation_type": calculation_type,
            **kwargs
        }
    )


def create_team_validation_repository_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    validation_field: Optional[str] = None,
    validation_value: Optional[Any] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamValidationRepositoryError:
    """
    Crea una excepción TeamValidationRepositoryError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        validation_field: Campo que falló la validación (opcional)
        validation_value: Valor que falló la validación (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamValidationRepositoryError configurada
    """
    return TeamValidationRepositoryError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "validation_field": validation_field,
            "validation_value": validation_value,
            **kwargs
        }
    )


def create_team_relationship_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    related_entity_type: Optional[str] = None,
    related_entity_id: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamRelationshipError:
    """
    Crea una excepción TeamRelationshipError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        related_entity_type: Tipo de entidad relacionada (opcional)
        related_entity_id: ID de la entidad relacionada (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamRelationshipError configurada
    """
    return TeamRelationshipError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "related_entity_type": related_entity_type,
            "related_entity_id": related_entity_id,
            **kwargs
        }
    )


def create_team_bulk_operation_error(
    message: str,
    operation: str,
    affected_teams: Optional[list] = None,
    successful_count: Optional[int] = None,
    failed_count: Optional[int] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamBulkOperationError:
    """
    Crea una excepción TeamBulkOperationError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        affected_teams: Lista de IDs de equipos afectados (opcional)
        successful_count: Número de operaciones exitosas (opcional)
        failed_count: Número de operaciones fallidas (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamBulkOperationError configurada
    """
    return TeamBulkOperationError(
        message=message,
        operation=operation,
        entity_type="Team",
        original_error=original_error,
        context={
            "affected_teams": affected_teams,
            "successful_count": successful_count,
            "failed_count": failed_count,
            **kwargs
        }
    )


def create_team_membership_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    employee_id: Optional[int] = None,
    membership_status: Optional[str] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamMembershipError:
    """
    Crea una excepción TeamMembershipError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        employee_id: ID del empleado relacionado (opcional)
        membership_status: Estado de la membresía (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamMembershipError configurada
    """
    return TeamMembershipError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "employee_id": employee_id,
            "membership_status": membership_status,
            **kwargs
        }
    )


def create_team_capacity_error(
    message: str,
    operation: str,
    team_id: Optional[int] = None,
    capacity_type: Optional[str] = None,
    capacity_value: Optional[float] = None,
    original_error: Optional[Exception] = None,
    **kwargs: Any
) -> TeamCapacityError:
    """
    Crea una excepción TeamCapacityError con contexto enriquecido.
    
    Args:
        message: Mensaje descriptivo del error
        operation: Nombre de la operación que falló
        team_id: ID del equipo relacionado (opcional)
        capacity_type: Tipo de capacidad (opcional)
        capacity_value: Valor de capacidad (opcional)
        original_error: Excepción original que causó el error (opcional)
        **kwargs: Contexto adicional
        
    Returns:
        Instancia de TeamCapacityError configurada
    """
    return TeamCapacityError(
        message=message,
        operation=operation,
        entity_type="Team",
        entity_id=team_id,
        original_error=original_error,
        context={
            "team_id": team_id,
            "capacity_type": capacity_type,
            "capacity_value": capacity_value,
            **kwargs
        }
    )