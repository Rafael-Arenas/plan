# src/planificador/exceptions/repository/team_membership_repository_exceptions.py

from typing import Optional, Any
from .base_repository_exceptions import RepositoryError


class TeamMembershipRepositoryError(RepositoryError):
    """
    Excepción base para errores específicos del repositorio de membresías de equipo.
    """
    pass


class TeamMembershipQueryError(TeamMembershipRepositoryError):
    """
    Excepción para errores en consultas de membresías de equipo.
    """
    pass


class TeamMembershipStatisticsError(TeamMembershipRepositoryError):
    """
    Excepción para errores en cálculos estadísticos de membresías de equipo.
    """
    pass


class TeamMembershipValidationRepositoryError(TeamMembershipRepositoryError):
    """
    Excepción para errores de validación en el repositorio de membresías de equipo.
    """
    pass


class TeamMembershipRelationshipError(TeamMembershipRepositoryError):
    """
    Excepción para errores en relaciones de membresías de equipo.
    """
    pass