# src/planificador/services/domain/team/interfaces/__init__.py

"""
Interfaces del servicio de dominio de Team.

Este módulo contiene todas las interfaces que definen los contratos
para las operaciones del servicio de dominio de equipos.
"""

from .team_domain_interface import ITeamDomainService
from .crud_operations import ITeamDomainCrudOperations
from .membership_operations import ITeamDomainMembershipOperations
from .search_operations import ITeamDomainSearchOperations
from .statistics_operations import ITeamDomainStatisticsOperations
from .productivity_operations import ITeamDomainProductivityOperations
from .validation_operations import ITeamDomainValidationOperations
from .relationship_operations import ITeamDomainRelationshipOperations
from .diagnostic_operations import ITeamDomainDiagnosticOperations

__all__ = [
    "ITeamDomainService",
    "ITeamDomainCrudOperations",
    "ITeamDomainMembershipOperations",
    "ITeamDomainSearchOperations",
    "ITeamDomainStatisticsOperations",
    "ITeamDomainProductivityOperations",
    "ITeamDomainValidationOperations",
    "ITeamDomainRelationshipOperations",
    "ITeamDomainDiagnosticOperations",
]