# src/planificador/services/domain/team/interfaces/team_domain_interface.py

"""
Interfaz principal del servicio de dominio de Team.

Esta interfaz actúa como un facade que hereda de todas las interfaces especializadas
para proporcionar una API unificada para la gestión completa de equipos.
"""

from abc import ABC

from .crud_operations_interface import ITeamDomainCrudOperations
from .membership_operations_interface import ITeamDomainMembershipOperations
from .search_operations_interface import ITeamDomainSearchOperations
from .statistics_operations_interface import ITeamDomainStatisticsOperations
from .productivity_operations_interface import ITeamDomainProductivityOperations
from .validation_operations_interface import ITeamDomainValidationOperations
from .relationship_operations_interface import ITeamDomainRelationshipOperations
from .diagnostic_operations_interface import ITeamDomainDiagnosticOperations


class ITeamDomainService(
    ITeamDomainCrudOperations,
    ITeamDomainMembershipOperations,
    ITeamDomainSearchOperations,
    ITeamDomainStatisticsOperations,
    ITeamDomainProductivityOperations,
    ITeamDomainValidationOperations,
    ITeamDomainRelationshipOperations,
    ITeamDomainDiagnosticOperations,
    ABC
):
    """
    Interfaz principal del servicio de dominio de Team.
    
    Esta interfaz actúa como un facade que combina todas las operaciones
    especializadas de gestión de equipos en una sola interfaz unificada.
    
    Hereda de:
        - ITeamDomainCrudOperations: Operaciones CRUD básicas
        - ITeamDomainMembershipOperations: Gestión de membresías
        - ITeamDomainSearchOperations: Operaciones de búsqueda
        - ITeamDomainStatisticsOperations: Estadísticas y métricas
        - ITeamDomainProductivityOperations: Análisis de productividad
        - ITeamDomainValidationOperations: Validaciones de negocio
        - ITeamDomainRelationshipOperations: Operaciones relacionales
        - ITeamDomainDiagnosticOperations: Diagnóstico y salud del servicio
    """
    pass