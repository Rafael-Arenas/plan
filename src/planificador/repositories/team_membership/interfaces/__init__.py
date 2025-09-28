# src/planificador/repositories/team_membership/interfaces/__init__.py

"""
Interfaces del repositorio TeamMembership.

Este módulo contiene todas las interfaces abstractas que definen
los contratos para las operaciones del repositorio de membresías de equipos.

Interfaces:
    - ITeamMembershipCrudOperations: Operaciones CRUD básicas
    - ITeamMembershipQueryOperations: Operaciones de consulta
    - ITeamMembershipRelationshipOperations: Operaciones de relaciones
    - ITeamMembershipStatisticsOperations: Operaciones de estadísticas
    - ITeamMembershipValidationOperations: Operaciones de validación
"""

from .crud_interface import ITeamMembershipCrudOperations
from .query_interface import ITeamMembershipQueryOperations
from .relationship_interface import ITeamMembershipRelationshipOperations
from .statistics_interface import ITeamMembershipStatisticsOperations
from .validation_interface import ITeamMembershipValidationOperations

__all__ = [
    "ITeamMembershipCrudOperations",
    "ITeamMembershipQueryOperations",
    "ITeamMembershipRelationshipOperations",
    "ITeamMembershipStatisticsOperations",
    "ITeamMembershipValidationOperations"
]