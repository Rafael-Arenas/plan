# src/planificador/repositories/status_code/modules/__init__.py

"""
Módulos especializados para el repositorio StatusCode.

Este paquete contiene los módulos especializados que implementan las diferentes
operaciones del repositorio StatusCode siguiendo el principio de Single Responsibility.

Arquitectura Modular:
    - Cada módulo se enfoca en un conjunto específico de operaciones
    - Implementación de interfaces abstractas para garantizar contratos
    - Separación clara de responsabilidades
    - Reutilización y mantenibilidad mejoradas

Módulos Disponibles:
    - CrudModule: Operaciones CRUD básicas (Create, Read, Update, Delete)
    - QueryModule: Operaciones de consulta, búsqueda y filtrado avanzado
    - ValidationModule: Validación de datos y reglas de negocio
    - StatisticsModule: Análisis estadístico y métricas de rendimiento

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Interface Segregation: Interfaces pequeñas y específicas
    - Dependency Injection: Inyección de dependencias para flexibilidad
    - Error Handling: Manejo consistente de errores con logging estructurado

Uso:
    ```python
    from planificador.repositories.status_code.modules import (
        StatusCodeCrudModule,
        StatusCodeQueryModule,
        StatusCodeValidationModule,
        StatusCodeStatisticsModule
    )
    
    # Inicializar módulos
    crud_module = StatusCodeCrudModule(session)
    query_module = StatusCodeQueryModule(session)
    validation_module = StatusCodeValidationModule(session)
    statistics_module = StatusCodeStatisticsModule(session)
    ```
"""

from .crud_module import StatusCodeCrudModule
from .query_module import StatusCodeQueryModule
from .validation_module import StatusCodeValidationModule
from .statistics_module import StatusCodeStatisticsModule

__all__ = [
    # Módulos especializados
    'StatusCodeCrudModule',
    'StatusCodeQueryModule', 
    'StatusCodeValidationModule',
    'StatusCodeStatisticsModule'
]