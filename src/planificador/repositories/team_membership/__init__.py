# src/planificador/repositories/team_membership/__init__.py

"""
Repositorio TeamMembership - Gestión de membresías de equipos.

Este paquete implementa el patrón Repository para la gestión completa
de membresías de equipos, incluyendo operaciones CRUD, consultas,
relaciones, estadísticas y validaciones.

Módulos:
    - interfaces: Definiciones de interfaces para operaciones
    - modules: Implementaciones concretas de las interfaces
        - crud_module: Operaciones CRUD básicas
        - query_module: Operaciones de consulta y búsqueda
        - relationship_module: Gestión de relaciones entre entidades
        - statistics_module: Análisis estadístico de membresías
        - validation_module: Validación de datos y reglas de negocio
    - team_membership_repository_facade: Facade principal del repositorio

Uso:
    ```python
    from planificador.repositories.team_membership import TeamMembershipRepositoryFacade
    
    # Crear instancia del repositorio
    repository = TeamMembershipRepositoryFacade(session)
    
    # Usar operaciones
    membership = await repository.create_membership(data)
    memberships = await repository.get_by_employee_id(employee_id)
    ```
"""

from .team_membership_repository_facade import TeamMembershipRepositoryFacade

__all__ = [
    'TeamMembershipRepositoryFacade'
]