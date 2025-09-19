# src/planificador/repositories/workload/interfaces/__init__.py

"""
Interfaces especializadas del repositorio Workload.

Este módulo proporciona las interfaces abstractas que definen los contratos
para las operaciones especializadas del repositorio de cargas de trabajo.

Componentes Especializados:
    - IWorkloadCrudOperations: Operaciones CRUD básicas
    - IWorkloadQueryOperations: Consultas y búsquedas avanzadas
    - IWorkloadValidationOperations: Validaciones de datos y reglas de negocio
    - IWorkloadStatisticsOperations: Análisis y métricas estadísticas
    - IWorkloadRelationshipOperations: Gestión de relaciones entre entidades

Principios de Diseño:
    - Interface Segregation: Cada interfaz tiene una responsabilidad específica
    - Dependency Inversion: Dependencias basadas en abstracciones
    - Single Responsibility: Cada interfaz maneja un aspecto específico

Uso:
    ```python
    from planificador.repositories.workload.interfaces import (
        IWorkloadCrudOperations,
        IWorkloadQueryOperations,
        IWorkloadValidationOperations,
        IWorkloadStatisticsOperations,
        IWorkloadRelationshipOperations
    )
    
    class WorkloadRepository(
        IWorkloadCrudOperations,
        IWorkloadQueryOperations,
        IWorkloadValidationOperations,
        IWorkloadStatisticsOperations,
        IWorkloadRelationshipOperations
    ):
        # Implementación completa del repositorio
        pass
    ```
"""

from planificador.repositories.workload.interfaces.crud_interface import IWorkloadCrudOperations
from planificador.repositories.workload.interfaces.query_interface import IWorkloadQueryOperations
from planificador.repositories.workload.interfaces.validation_interface import IWorkloadValidationOperations
from planificador.repositories.workload.interfaces.statistics_interface import IWorkloadStatisticsOperations
from planificador.repositories.workload.interfaces.relationship_interface import IWorkloadRelationshipOperations

__all__ = [
    "IWorkloadCrudOperations",
    "IWorkloadQueryOperations", 
    "IWorkloadValidationOperations",
    "IWorkloadStatisticsOperations",
    "IWorkloadRelationshipOperations",
]