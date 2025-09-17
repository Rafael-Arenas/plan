# src/planificador/repositories/team/modules/__init__.py

"""
Módulos de implementación del repositorio Team.

Este paquete contiene las implementaciones concretas de las interfaces
definidas para el repositorio Team, organizadas por responsabilidad:

- CrudModule: Operaciones CRUD básicas (crear, actualizar, eliminar)
- QueryModule: Operaciones de consulta y búsqueda
- RelationshipModule: Gestión de membresías y relaciones
- StatisticsModule: Estadísticas y reportes
- ValidationModule: Validaciones y reglas de negocio

Cada módulo hereda de BaseRepository e implementa las interfaces correspondientes,
proporcionando funcionalidad específica mientras mantiene consistencia
en el manejo de errores, logging y transacciones.

Uso:
    ```python
    from planificador.repositories.team.modules import (
        TeamCrudModule,
        TeamQueryModule,
        TeamRelationshipModule,
        TeamStatisticsModule,
        TeamValidationModule
    )
    
    # Inicializar módulos con sesión de base de datos
    crud_module = TeamCrudModule(session)
    query_module = TeamQueryModule(session)
    relationship_module = TeamRelationshipModule(session)
    statistics_module = TeamStatisticsModule(session)
    validation_module = TeamValidationModule(session)
    ```

Arquitectura:
    - Cada módulo es independiente y reutilizable
    - Implementan interfaces específicas para garantizar contratos
    - Usan BaseRepository para funcionalidad común
    - Manejo consistente de excepciones y logging
    - Soporte completo para operaciones asíncronas
"""

from .crud_module import TeamCrudModule
from .query_module import TeamQueryModule
from .relationship_module import TeamRelationshipModule
from .statistics_module import TeamStatisticsModule
from .validation_module import TeamValidationModule

__all__ = [
    "TeamCrudModule",
    "TeamQueryModule", 
    "TeamRelationshipModule",
    "TeamStatisticsModule",
    "TeamValidationModule"
]