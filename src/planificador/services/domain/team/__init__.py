"""Dominio de Equipos (Team) - Servicios de Dominio.

Este paquete contiene todos los servicios de dominio relacionados con la gestión
de equipos, incluyendo operaciones CRUD, membresías, búsquedas, estadísticas,
productividad, validaciones, relaciones y diagnósticos.
"""

from .interfaces import (
    ITeamDomainService,
    ITeamDomainCrudOperations,
    ITeamDomainMembershipOperations,
    ITeamDomainSearchOperations,
    ITeamDomainStatisticsOperations,
    ITeamDomainProductivityOperations,
    ITeamDomainValidationOperations,
    ITeamDomainRelationshipOperations,
    ITeamDomainDiagnosticOperations
)

from .modules import (
    TeamDomainCrudOperations,
    TeamDomainMembershipOperations,
    TeamDomainSearchOperations,
    TeamDomainStatisticsOperations,
    TeamDomainProductivityOperations,
    TeamDomainValidationOperations,
    TeamDomainRelationshipOperations,
    TeamDomainDiagnosticOperations
)

from .team_domain_service import TeamDomainService

__all__ = [
    # Main Service
    "TeamDomainService",
    
    # Interfaces
    "ITeamDomainService",
    "ITeamDomainCrudOperations",
    "ITeamDomainMembershipOperations",
    "ITeamDomainSearchOperations",
    "ITeamDomainStatisticsOperations",
    "ITeamDomainProductivityOperations",
    "ITeamDomainValidationOperations",
    "ITeamDomainRelationshipOperations",
    "ITeamDomainDiagnosticOperations",
    
    # Implementations
    "TeamDomainCrudOperations",
    "TeamDomainMembershipOperations",
    "TeamDomainSearchOperations",
    "TeamDomainStatisticsOperations",
    "TeamDomainProductivityOperations",
    "TeamDomainValidationOperations",
    "TeamDomainRelationshipOperations",
    "TeamDomainDiagnosticOperations"
]