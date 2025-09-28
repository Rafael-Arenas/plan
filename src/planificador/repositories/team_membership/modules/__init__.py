# src/planificador/repositories/team_membership/modules/__init__.py

"""
Módulos de implementación del repositorio TeamMembership.

Este paquete contiene las implementaciones concretas de las interfaces
definidas para el repositorio TeamMembership, organizadas por responsabilidad:

- CrudModule: Operaciones CRUD básicas (crear, actualizar, eliminar, activar, desactivar)
- QueryModule: Operaciones de consulta y búsqueda de membresías
- RelationshipModule: Gestión de relaciones entre empleados, equipos y membresías
- StatisticsModule: Estadísticas, métricas y análisis de membresías
- ValidationModule: Validaciones y reglas de negocio para membresías

Cada módulo hereda de BaseRepository e implementa las interfaces correspondientes,
proporcionando funcionalidad específica mientras mantiene consistencia
en el manejo de errores, logging y transacciones.

Uso:
    ```python
    from planificador.repositories.team_membership.modules import (
        TeamMembershipCrudModule,
        TeamMembershipQueryModule,
        TeamMembershipRelationshipModule,
        TeamMembershipStatisticsModule,
        TeamMembershipValidationModule
    )
    
    # Inicializar módulos con sesión de base de datos
    crud_module = TeamMembershipCrudModule(session)
    query_module = TeamMembershipQueryModule(session)
    relationship_module = TeamMembershipRelationshipModule(session)
    statistics_module = TeamMembershipStatisticsModule(session)
    validation_module = TeamMembershipValidationModule(session)
    ```

Arquitectura:
    - Cada módulo es independiente y reutilizable
    - Implementan interfaces específicas para garantizar contratos
    - Usan BaseRepository para funcionalidad común
    - Manejo consistente de excepciones y logging
    - Soporte completo para operaciones asíncronas
    - Validaciones de negocio para integridad de membresías
    - Análisis estadístico avanzado de equipos y empleados
"""

from .crud_module import TeamMembershipCrudModule
from .query_module import TeamMembershipQueryModule
from .relationship_module import TeamMembershipRelationshipModule
from .statistics_module import TeamMembershipStatisticsModule
from .validation_module import TeamMembershipValidationModule

__all__ = [
    "TeamMembershipCrudModule",
    "TeamMembershipQueryModule", 
    "TeamMembershipRelationshipModule",
    "TeamMembershipStatisticsModule",
    "TeamMembershipValidationModule",
]