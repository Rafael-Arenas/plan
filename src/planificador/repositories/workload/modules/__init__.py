# src/planificador/repositories/workload/modules/__init__.py

"""
Módulos especializados del repositorio Workload.

Este paquete contiene los módulos especializados que implementan
las diferentes operaciones del repositorio de cargas de trabajo,
organizados por responsabilidad específica.

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Modular Architecture: Componentes independientes y reutilizables
    - Interface Segregation: Interfaces específicas para cada tipo de operación
    - Dependency Injection: Módulos reciben dependencias como parámetros
    - Error Handling: Manejo consistente de errores en todos los módulos

Módulos Implementados:
    - WorkloadCrudModule: Operaciones CRUD básicas (Create, Read, Update, Delete)
    - WorkloadQueryModule: Consultas especializadas y búsquedas avanzadas
    - WorkloadValidationModule: Validaciones de datos y reglas de negocio
    - WorkloadStatisticsModule: Análisis estadísticos y métricas
    - WorkloadRelationshipModule: Gestión de relaciones y asociaciones

Uso:
    ```python
    from planificador.repositories.workload.modules import (
        WorkloadCrudModule,
        WorkloadQueryModule,
        WorkloadValidationModule,
        WorkloadStatisticsModule,
        WorkloadRelationshipModule
    )
    
    # Usar módulos individualmente
    crud_module = WorkloadCrudModule(session)
    query_module = WorkloadQueryModule(session)
    validation_module = WorkloadValidationModule(session)
    stats_module = WorkloadStatisticsModule(session)
    rel_module = WorkloadRelationshipModule(session)
    
    # Ejemplo de uso coordinado
    workload_data = {...}
    
    # Validar antes de crear
    await validation_module.validate_workload_data(workload_data)
    
    # Crear la carga de trabajo
    workload = await crud_module.create_workload(workload_data)
    
    # Obtener estadísticas actualizadas
    stats = await stats_module.get_employee_workload_statistics(workload.employee_id)
    ```
"""

from .crud_module import WorkloadCrudModule
from .query_module import WorkloadQueryModule
from .validation_module import WorkloadValidationModule
from .statistics_module import WorkloadStatisticsModule
from .relationship_module import WorkloadRelationshipModule

__all__ = [
    'WorkloadCrudModule',
    'WorkloadQueryModule', 
    'WorkloadValidationModule',
    'WorkloadStatisticsModule',
    'WorkloadRelationshipModule'
]