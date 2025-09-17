# src/planificador/repositories/vacation/interfaces/__init__.py

"""
Interfaces del Repositorio Vacation.

Este módulo expone todas las interfaces abstractas para las operaciones
del repositorio de vacaciones, siguiendo el principio de segregación
de interfaces (Interface Segregation Principle).

Interfaces Disponibles:
    - IVacationCrudOperations: Operaciones CRUD básicas
    - IVacationQueryOperations: Consultas y filtros avanzados
    - IVacationValidationOperations: Validaciones de datos y reglas de negocio
    - IVacationRelationshipOperations: Gestión de relaciones y conflictos
    - IVacationStatisticsOperations: Estadísticas y análisis de métricas

Principios de Diseño:
    - Interface Segregation: Cada interfaz tiene una responsabilidad específica
    - Dependency Inversion: Abstracciones para implementaciones concretas
    - Single Responsibility: Cada interfaz maneja un aspecto específico

Uso:
    ```python
    from planificador.repositories.vacation.interfaces import (
        IVacationCrudOperations,
        IVacationQueryOperations,
        IVacationValidationOperations,
        IVacationRelationshipOperations,
        IVacationStatisticsOperations
    )
    
    class VacationRepositoryFacade(
        IVacationCrudOperations,
        IVacationQueryOperations,
        IVacationValidationOperations,
        IVacationRelationshipOperations,
        IVacationStatisticsOperations
    ):
        # Implementación del facade
        pass
    ```
"""

from .crud_interface import IVacationCrudOperations
from .query_interface import IVacationQueryOperations
from .validation_interface import IVacationValidationOperations
from .relationship_interface import IVacationRelationshipOperations
from .statistics_interface import IVacationStatisticsOperations

__all__ = [
    "IVacationCrudOperations",
    "IVacationQueryOperations", 
    "IVacationValidationOperations",
    "IVacationRelationshipOperations",
    "IVacationStatisticsOperations",
]