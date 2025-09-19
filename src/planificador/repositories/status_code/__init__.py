# src/planificador/repositories/status_code/__init__.py

"""
Repositorio StatusCode - Sistema de Gestión de Códigos de Estado.

Este paquete implementa un sistema completo de gestión de códigos de estado
utilizando el patrón Repository con arquitectura modular y especializada.

Arquitectura del Sistema:
    - Facade Pattern: Interfaz unificada a través de StatusCodeRepositoryFacade
    - Interface Segregation: Interfaces especializadas por responsabilidad
    - Modular Design: Módulos independientes para cada tipo de operación
    - Dependency Injection: Componentes desacoplados y testeable
    - Error Handling: Manejo consistente de errores y logging

Componentes Principales:
    - StatusCodeRepositoryFacade: Punto de entrada principal del repositorio
    - Interfaces: Contratos especializados (CRUD, Query, Validation, Statistics)
    - Módulos: Implementaciones concretas de las interfaces
    - Excepciones: Sistema de errores específico del dominio

Funcionalidades Implementadas:
    ✅ 32 funciones documentadas en status_code_available_functions.md
    ✅ Operaciones CRUD completas
    ✅ Consultas especializadas y búsquedas avanzadas
    ✅ Validaciones de datos y reglas de negocio
    ✅ Análisis estadísticos y métricas de integridad
    ✅ Operaciones de mantenimiento y health checks

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Open/Closed: Extensible sin modificar código existente
    - Liskov Substitution: Los módulos son intercambiables
    - Interface Segregation: Interfaces pequeñas y cohesivas
    - Dependency Inversion: Dependencias inyectadas, no hardcodeadas

Patrones Implementados:
    - Repository Pattern: Abstracción de acceso a datos
    - Facade Pattern: Interfaz unificada para subsistemas complejos
    - Strategy Pattern: Diferentes estrategias de consulta y validación
    - Factory Pattern: Creación de objetos especializados

Ejemplo de Uso Básico:
    ```python
    from planificador.repositories.status_code import StatusCodeRepositoryFacade
    from sqlalchemy.ext.asyncio import AsyncSession
    
    async def example_usage(session: AsyncSession):
        facade = StatusCodeRepositoryFacade(session)
        
        # Operaciones CRUD
        status_code = await facade.create_status_code({
            "code": "ACTIVE",
            "name": "Activo",
            "description": "Estado activo del sistema",
            "is_active": True,
            "is_default": False,
            "display_order": 1
        })
        
        # Consultas especializadas
        active_codes = await facade.find_active_status_codes()
        code_by_name = await facade.find_by_code("ACTIVE")
        
        # Validaciones
        is_unique = await facade.validate_unique_code("NEW_CODE")
        
        # Estadísticas
        stats = await facade.get_status_code_statistics()
        
        return status_code
    ```

Ejemplo de Uso Avanzado:
    ```python
    async def advanced_usage(session: AsyncSession):
        facade = StatusCodeRepositoryFacade(session)
        
        # Búsqueda con filtros avanzados
        filtered_codes = await facade.find_with_advanced_filters({
            "is_active": True,
            "search_text": "activo",
            "min_display_order": 1,
            "max_display_order": 10
        })
        
        # Paginación
        codes, total = await facade.get_status_codes_paginated(
            page=1, 
            page_size=10,
            filters={"is_active": True}
        )
        
        # Validación completa de datos
        validation_errors = await facade.validate_status_code_data({
            "code": "TEST",
            "name": "Test Status",
            "is_default": True
        })
        
        # Análisis de integridad
        integrity_report = await facade.get_data_integrity_report()
        
        return {
            "codes": filtered_codes,
            "paginated": codes,
            "total": total,
            "validation": validation_errors,
            "integrity": integrity_report
        }
    ```

Manejo de Errores:
    ```python
    from planificador.exceptions.repository import (
        StatusCodeRepositoryError,
        StatusCodeNotFoundError,
        StatusCodeValidationError
    )
    
    try:
        result = await facade.create_status_code(invalid_data)
    except StatusCodeValidationError as e:
        logger.error(f"Error de validación: {e}")
    except StatusCodeRepositoryError as e:
        logger.error(f"Error del repositorio: {e}")
    except Exception as e:
        logger.error(f"Error inesperado: {e}")
    ```

Health Check y Monitoreo:
    ```python
    # Verificar estado del sistema
    health = await facade.health_check()
    module_info = facade.get_module_info()
    
    # Métricas de rendimiento
    performance = await facade.get_usage_performance_metrics()
    health_check = await facade.get_status_code_health_check()
    ```

Compatibilidad:
    Este repositorio es compatible con:
    - SQLAlchemy 2.0+ (async)
    - Python 3.11+
    - Pydantic 2.0+
    - Loguru para logging estructurado
    - Pendulum para manejo de fechas
"""

# Facade principal - Punto de entrada recomendado
from .status_code_repository_facade import StatusCodeRepositoryFacade

# Interfaces especializadas
from .interfaces import (
    IStatusCodeCrudOperations,
    IStatusCodeQueryOperations,
    IStatusCodeValidationOperations,
    IStatusCodeStatisticsOperations
)

# Módulos especializados (para uso avanzado)
from .modules import (
    StatusCodeCrudModule,
    StatusCodeQueryModule,
    StatusCodeValidationModule,
    StatusCodeStatisticsModule
)

# Exportaciones principales
__all__ = [
    # Facade principal
    "StatusCodeRepositoryFacade",
    
    # Interfaces
    "IStatusCodeCrudOperations",
    "IStatusCodeQueryOperations", 
    "IStatusCodeValidationOperations",
    "IStatusCodeStatisticsOperations",
    
    # Módulos especializados
    "StatusCodeCrudModule",
    "StatusCodeQueryModule",
    "StatusCodeValidationModule",
    "StatusCodeStatisticsModule"
]

# Información del paquete
__version__ = "1.0.0"
__author__ = "Sistema de Modularización"
__description__ = "Repositorio modular para gestión de códigos de estado"

# Configuración de logging para el paquete
import logging
logging.getLogger(__name__).addHandler(logging.NullHandler())