# src/planificador/services/domain/team/modules/__init__.py

"""
Módulos de Implementación del Servicio de Dominio Team.

Este paquete contiene las implementaciones concretas de todas las operaciones
del servicio de dominio de equipos, organizadas por categorías funcionales.

Módulos Disponibles:
    - crud_operations: Operaciones CRUD básicas
    - membership_operations: Gestión de membresías
    - search_operations: Búsquedas y consultas
    - statistics_operations: Estadísticas y métricas
    - productivity_operations: Análisis de productividad
    - validation_operations: Validaciones e integridad
    - relationship_operations: Consultas relacionales
    - diagnostic_operations: Diagnóstico y monitoreo

Arquitectura:
    Cada módulo implementa una interfaz específica y proporciona
    funcionalidades especializadas para el dominio de equipos.

Uso:
    ```python
    from planificador.services.domain.team.modules import (
        TeamDomainCrudOperations,
        TeamDomainMembershipOperations,
        # ... otros módulos
    )
    ```
"""

from .crud_operations import TeamDomainCrudOperations
from .membership_operations import TeamDomainMembershipOperations
from .search_operations import TeamDomainSearchOperations
from .statistics_operations import TeamDomainStatisticsOperations
from .productivity_operations import TeamDomainProductivityOperations
from .validation_operations import TeamDomainValidationOperations
from .relationship_operations import TeamDomainRelationshipOperations
from .diagnostic_operations import TeamDomainDiagnosticOperations

__all__ = [
    # Operaciones CRUD
    "TeamDomainCrudOperations",
    
    # Operaciones de Membresía
    "TeamDomainMembershipOperations",
    
    # Operaciones de Búsqueda
    "TeamDomainSearchOperations",
    
    # Operaciones de Estadísticas
    "TeamDomainStatisticsOperations",
    
    # Operaciones de Productividad
    "TeamDomainProductivityOperations",
    
    # Operaciones de Validación
    "TeamDomainValidationOperations",
    
    # Operaciones de Relaciones
    "TeamDomainRelationshipOperations",
    
    # Operaciones de Diagnóstico
    "TeamDomainDiagnosticOperations",
]