# src/planificador/database/repositories/workload/__init__.py

"""
Repositorio Workload - Sistema de Gestión de Cargas de Trabajo.

Este paquete implementa un sistema completo de gestión de cargas de trabajo
utilizando el patrón Repository con arquitectura modular y especializada.

Arquitectura del Sistema:
    - Facade Pattern: Interfaz unificada a través de WorkloadRepositoryFacade
    - Interface Segregation: Interfaces especializadas por responsabilidad
    - Modular Design: Módulos independientes para cada tipo de operación
    - Dependency Injection: Componentes desacoplados y testeable
    - Error Handling: Manejo consistente de errores y logging

Componentes Principales:
    - WorkloadRepositoryFacade: Punto de entrada principal del repositorio
    - Interfaces: Contratos especializados (CRUD, Query, Validation, Statistics, Relationship)
    - Módulos: Implementaciones concretas de las interfaces
    - Excepciones: Sistema de errores específico del dominio

Funcionalidades Implementadas:
    ✅ 69 funciones documentadas en workload_available_functions.md
    ✅ Operaciones CRUD completas
    ✅ Consultas especializadas y búsquedas avanzadas
    ✅ Validaciones de datos y reglas de negocio
    ✅ Análisis estadísticos y métricas de productividad
    ✅ Gestión de relaciones y dependencias
    ✅ Operaciones compuestas y en lote
    ✅ Dashboard y reportes integrados

Principios de Diseño:
    - Single Responsibility: Cada componente tiene una responsabilidad específica
    - Open/Closed: Extensible sin modificar código existente
    - Liskov Substitution: Interfaces intercambiables
    - Interface Segregation: Interfaces pequeñas y específicas
    - Dependency Inversion: Dependencias hacia abstracciones

Uso Básico:
    ```python
    from planificador.database.repositories.workload import WorkloadRepositoryFacade
    
    async with get_async_session() as session:
        workload_repo = WorkloadRepositoryFacade(session)
        
        # Crear carga de trabajo con validación
        result = await workload_repo.create_workload_with_validation({
            "employee_id": 1,
            "project_id": 2,
            "hours": 8.0,
            "work_date": "2024-01-15",
            "description": "Desarrollo de funcionalidad X",
            "status": "completed"
        })
        
        # Obtener estadísticas del empleado
        stats = await workload_repo.get_employee_workload_statistics(
            employee_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
        
        # Obtener datos del dashboard
        dashboard = await workload_repo.get_workload_dashboard_data(
            employee_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
    ```

Uso Avanzado con Módulos Específicos:
    ```python
    from planificador.database.repositories.workload.modules import (
        WorkloadCrudModule,
        WorkloadQueryModule,
        WorkloadValidationModule,
        WorkloadStatisticsModule,
        WorkloadRelationshipModule
    )
    
    async with get_async_session() as session:
        # Usar módulos individualmente para casos específicos
        crud_module = WorkloadCrudModule(session)
        stats_module = WorkloadStatisticsModule(session)
        
        # Operaciones especializadas
        workload = await crud_module.create_workload(workload_data)
        productivity = await stats_module.calculate_productivity_metrics(
            employee_id=1,
            start_date=date(2024, 1, 1),
            end_date=date(2024, 1, 31)
        )
    ```

Integración con Interfaces:
    ```python
    from planificador.database.repositories.workload.interfaces import (
        IWorkloadCrudOperations,
        IWorkloadQueryOperations,
        IWorkloadValidationOperations,
        IWorkloadStatisticsOperations,
        IWorkloadRelationshipOperations
    )
    
    # Usar interfaces para testing o implementaciones alternativas
    def process_workloads(crud_ops: IWorkloadCrudOperations):
        # Lógica que funciona con cualquier implementación
        pass
    ```

Manejo de Errores:
    ```python
    from planificador.exceptions.repository import WorkloadRepositoryError
    
    try:
        workload = await workload_repo.create_workload(invalid_data)
    except WorkloadRepositoryError as e:
        logger.error(f"Error en repositorio: {e.message}")
        logger.error(f"Operación: {e.operation}")
        logger.error(f"Entidad: {e.entity_type}")
    ```

Notas de Implementación:
    - Todas las operaciones son asíncronas usando SQLAlchemy async
    - Logging estructurado con Loguru para trazabilidad completa
    - Validaciones robustas con Pydantic cuando es apropiado
    - Manejo de fechas con Pendulum para precisión temporal
    - Transacciones automáticas con rollback en caso de error
    - Optimización de consultas con eager/lazy loading apropiado
"""

# Importar la fachada principal (punto de entrada recomendado)
from .workload_repository_facade import WorkloadRepositoryFacade

# Importar interfaces para casos de uso avanzados
from .interfaces import (
    IWorkloadCrudOperations,
    IWorkloadQueryOperations,
    IWorkloadValidationOperations,
    IWorkloadStatisticsOperations,
    IWorkloadRelationshipOperations
)

# Importar módulos para uso especializado
from .modules import (
    WorkloadCrudModule,
    WorkloadQueryModule,
    WorkloadValidationModule,
    WorkloadStatisticsModule,
    WorkloadRelationshipModule
)

# Exportar componentes principales
__all__ = [
    # Fachada principal (recomendado para uso general)
    'WorkloadRepositoryFacade',
    
    # Interfaces (para testing y casos avanzados)
    'IWorkloadCrudOperations',
    'IWorkloadQueryOperations',
    'IWorkloadValidationOperations',
    'IWorkloadStatisticsOperations',
    'IWorkloadRelationshipOperations',
    
    # Módulos especializados (para casos específicos)
    'WorkloadCrudModule',
    'WorkloadQueryModule',
    'WorkloadValidationModule',
    'WorkloadStatisticsModule',
    'WorkloadRelationshipModule'
]

# Información del paquete
__version__ = "1.0.0"
__author__ = "Planificador Development Team"
__description__ = "Sistema completo de gestión de cargas de trabajo con arquitectura modular"

# Configuración de logging para el paquete
import logging
logger = logging.getLogger(__name__)
logger.info("Repositorio Workload inicializado - 69 funciones disponibles")