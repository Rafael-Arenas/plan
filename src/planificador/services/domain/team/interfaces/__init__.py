# src/planificador/services/domain/team/interfaces/__init__.py

"""
Interfaces del servicio de dominio de Team.

Este módulo contiene todas las interfaces que definen los contratos
para las operaciones del servicio de dominio de equipos.
"""

from .team_domain_interface import ITeamDomainService
from .crud_operations_interface import ITeamDomainCrudOperations
from .membership_operations_interface import ITeamDomainMembershipOperations
from .search_operations_interface import ITeamDomainSearchOperations
from .statistics_operations_interface import ITeamDomainStatisticsOperations
from .productivity_operations_interface import ITeamDomainProductivityOperations
from .validation_operations_interface import ITeamDomainValidationOperations
from .relationship_operations_interface import ITeamDomainRelationshipOperations
from .diagnostic_operations_interface import ITeamDomainDiagnosticOperations

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