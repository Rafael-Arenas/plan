# src/planificador/exceptions/domain/team_domain_exceptions.py

"""
Excepciones específicas del dominio de Team.

Este módulo define todas las excepciones relacionadas con la lógica de negocio
y operaciones del dominio de equipos (Team).
"""

from typing import Optional, Dict, Any
from ..base import BusinessLogicError, ValidationError, NotFoundError, ConflictError


class TeamDomainError(BusinessLogicError):
    """
    Excepción base para errores del dominio de Team.
    
    Esta es la excepción padre para todos los errores específicos
    del dominio de equipos.
    """
    
    def __init__(
        self,
        message: str,
        error_code: str = "TEAM_DOMAIN_ERROR",
        context: Optional[Dict[str, Any]] = None
    ):
        super().__init__(message, error_code, context)


class TeamValidationError(TeamDomainError):
    """
    Excepción para errores de validación en el dominio de Team.
    
    Se lanza cuando los datos del equipo no cumplen con las reglas
    de validación del dominio.
    """
    
    def __init__(
        self,
        message: str,
        field: Optional[str] = None,
        value: Optional[Any] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_VALIDATION_ERROR"
        validation_context = context or {}
        
        if field:
            validation_context["field"] = field
        if value is not None:
            validation_context["value"] = value
            
        super().__init__(message, error_code, validation_context)


class TeamBusinessRuleViolationError(TeamDomainError):
    """
    Excepción para violaciones de reglas de negocio en el dominio de Team.
    
    Se lanza cuando una operación viola las reglas de negocio específicas
    del dominio de equipos.
    """
    
    def __init__(
        self,
        message: str,
        rule: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_BUSINESS_RULE_VIOLATION"
        rule_context = context or {}
        
        if rule:
            rule_context["violated_rule"] = rule
            
        super().__init__(message, error_code, rule_context)


class TeamMembershipError(TeamDomainError):
    """
    Excepción para errores relacionados con membresías de equipo.
    
    Se lanza cuando hay problemas con la gestión de miembros del equipo.
    """
    
    def __init__(
        self,
        message: str,
        team_id: Optional[int] = None,
        member_id: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_MEMBERSHIP_ERROR"
        membership_context = context or {}
        
        if team_id:
            membership_context["team_id"] = team_id
        if member_id:
            membership_context["member_id"] = member_id
            
        super().__init__(message, error_code, membership_context)


class TeamCapacityExceededError(TeamDomainError):
    """
    Excepción para cuando se excede la capacidad del equipo.
    
    Se lanza cuando se intenta agregar más miembros de los permitidos
    o cuando se excede la capacidad de trabajo del equipo.
    """
    
    def __init__(
        self,
        message: str,
        current_capacity: Optional[int] = None,
        max_capacity: Optional[int] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_CAPACITY_EXCEEDED"
        capacity_context = context or {}
        
        if current_capacity is not None:
            capacity_context["current_capacity"] = current_capacity
        if max_capacity is not None:
            capacity_context["max_capacity"] = max_capacity
            
        super().__init__(message, error_code, capacity_context)


class TeamStatusTransitionError(TeamDomainError):
    """
    Excepción para transiciones de estado inválidas del equipo.
    
    Se lanza cuando se intenta cambiar el estado del equipo de manera
    que viola las reglas de transición de estados.
    """
    
    def __init__(
        self,
        message: str,
        current_status: Optional[str] = None,
        target_status: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_STATUS_TRANSITION_ERROR"
        transition_context = context or {}
        
        if current_status:
            transition_context["current_status"] = current_status
        if target_status:
            transition_context["target_status"] = target_status
            
        super().__init__(message, error_code, transition_context)


class TeamStatisticsError(TeamDomainError):
    """
    Excepción para errores en el cálculo de estadísticas del equipo.
    
    Se lanza cuando hay problemas al calcular métricas o estadísticas
    del equipo.
    """
    
    def __init__(
        self,
        message: str,
        metric_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_STATISTICS_ERROR"
        stats_context = context or {}
        
        if metric_type:
            stats_context["metric_type"] = metric_type
            
        super().__init__(message, error_code, stats_context)


class TeamProductivityError(TeamDomainError):
    """
    Excepción para errores relacionados con la productividad del equipo.
    
    Se lanza cuando hay problemas al calcular o analizar la productividad
    del equipo.
    """
    
    def __init__(
        self,
        message: str,
        analysis_type: Optional[str] = None,
        context: Optional[Dict[str, Any]] = None
    ):
        error_code = "TEAM_PRODUCTIVITY_ERROR"
        productivity_context = context or {}
        
        if analysis_type:
            productivity_context["analysis_type"] = analysis_type
            
        super().__init__(message, error_code, productivity_context)


# Funciones de utilidad para crear excepciones comunes
def create_team_not_found_error(team_id: int) -> TeamDomainError:
    """
    Crea una excepción estándar para equipo no encontrado.
    
    Args:
        team_id: ID del equipo que no fue encontrado
        
    Returns:
        TeamDomainError: Excepción configurada para equipo no encontrado
    """
    return TeamDomainError(
        message=f"Equipo con ID {team_id} no encontrado",
        error_code="TEAM_NOT_FOUND",
        context={"team_id": team_id}
    )


def create_team_validation_error(field: str, value: Any, reason: str) -> TeamValidationError:
    """
    Crea una excepción estándar para errores de validación de equipo.
    
    Args:
        field: Campo que falló la validación
        value: Valor que causó el error
        reason: Razón del error de validación
        
    Returns:
        TeamValidationError: Excepción configurada para error de validación
    """
    return TeamValidationError(
        message=f"Error de validación en campo '{field}': {reason}",
        field=field,
        value=value,
        context={"reason": reason}
    )


def create_team_business_rule_error(rule: str, description: str) -> TeamBusinessRuleViolationError:
    """
    Crea una excepción estándar para violaciones de reglas de negocio.
    
    Args:
        rule: Nombre de la regla violada
        description: Descripción del error
        
    Returns:
        TeamBusinessRuleViolationError: Excepción configurada para violación de regla
    """
    return TeamBusinessRuleViolationError(
        message=f"Violación de regla de negocio '{rule}': {description}",
        rule=rule,
        context={"description": description}
    )