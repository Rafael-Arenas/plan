# src/planificador/repositories/team/interfaces/__init__.py

"""
Módulo de interfaces para el repositorio Team.

Este módulo expone todas las interfaces abstractas que definen
los contratos para las operaciones del repositorio de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaces específicas por responsabilidad
    - Dependency Inversion: Abstracciones para implementaciones concretas
    - Single Responsibility: Cada interfaz tiene una responsabilidad específica

Interfaces Disponibles:
    - ITeamCrudOperations: Operaciones CRUD básicas
    - ITeamQueryOperations: Operaciones de consulta y búsqueda
    - ITeamRelationshipOperations: Operaciones de relaciones y membresías
    - ITeamStatisticsOperations: Operaciones de estadísticas y análisis
    - ITeamValidationOperations: Operaciones de validación y reglas de negocio

Uso:
    ```python
    from planificador.repositories.team.interfaces import (
        ITeamCrudOperations,
        ITeamQueryOperations,
        ITeamRelationshipOperations,
        ITeamStatisticsOperations,
        ITeamValidationOperations
    )
    
    class TeamRepositoryFacade(
        ITeamCrudOperations,
        ITeamQueryOperations,
        ITeamRelationshipOperations,
        ITeamStatisticsOperations,
        ITeamValidationOperations
    ):
        # Implementación del facade
        pass
    ```
"""

from .crud_interface import ITeamCrudOperations
from .query_interface import ITeamQueryOperations
from .relationship_interface import ITeamRelationshipOperations
from .statistics_interface import ITeamStatisticsOperations
from .validation_interface import ITeamValidationOperations

__all__ = [
    "ITeamCrudOperations",
    "ITeamQueryOperations", 
    "ITeamRelationshipOperations",
    "ITeamStatisticsOperations",
    "ITeamValidationOperations"
]