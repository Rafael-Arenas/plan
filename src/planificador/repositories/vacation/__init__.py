# src/planificador/repositories/vacation/__init__.py

"""
Repositorio Vacation - Sistema de Gestión de Vacaciones.

Este paquete implementa un sistema completo de gestión de vacaciones de empleados
siguiendo principios de arquitectura limpia y patrones de diseño modernos.

Arquitectura:
    - Patrón Facade: Interfaz unificada para todas las operaciones
    - Segregación de Interfaces: Interfaces específicas por responsabilidad
    - Módulos Especializados: Implementaciones separadas por funcionalidad
    - Manejo Robusto de Errores: Sistema de excepciones específicas

Componentes Principales:
    - VacationRepositoryFacade: Punto de entrada principal
    - Interfaces: Contratos para operaciones especializadas
    - Módulos: Implementaciones concretas de las interfaces
    - Excepciones: Sistema de errores específicos del dominio

Funcionalidades Disponibles:
    ✅ CRUD completo de vacaciones
    ✅ Consultas avanzadas con filtros y paginación
    ✅ Validaciones de datos y reglas de negocio
    ✅ Gestión de relaciones con empleados
    ✅ Análisis estadístico y reportes
    ✅ Detección de conflictos y solapamientos
    ✅ Operaciones en lote
    ✅ Dashboard de datos integrado

Uso Básico:
    ```python
    from planificador.repositories.vacation import VacationRepositoryFacade
    from planificador.database.session import get_async_session
    
    async with get_async_session() as session:
        vacation_repo = VacationRepositoryFacade(session)
        
        # Crear vacación con validación completa
        result = await vacation_repo.create_vacation_with_validation({
            'employee_id': 1,
            'vacation_type': 'ANNUAL',
            'start_date': date(2024, 6, 1),
            'end_date': date(2024, 6, 10),
            'days_requested': 8,
            'reason': 'Vacaciones familiares'
        })
        
        # Obtener vacaciones del empleado
        vacations = await vacation_repo.get_vacations_by_employee(1)
        
        # Verificar conflictos
        conflicts = await vacation_repo.check_vacation_conflicts(
            employee_id=1,
            start_date=date(2024, 6, 15),
            end_date=date(2024, 6, 20)
        )
        
        # Obtener estadísticas
        stats = await vacation_repo.get_employee_vacation_statistics(1, 2024)
        
        # Dashboard completo
        dashboard = await vacation_repo.get_vacation_dashboard_data(employee_id=1)
    ```

Uso Avanzado:
    ```python
    # Operaciones en lote
    vacation_data_list = [
        {'employee_id': 1, 'vacation_type': 'ANNUAL', ...},
        {'employee_id': 2, 'vacation_type': 'SICK', ...},
        {'employee_id': 3, 'vacation_type': 'PERSONAL', ...}
    ]
    
    results = await vacation_repo.bulk_vacation_operation('create', vacation_data_list)
    
    # Análisis de patrones
    patterns = await vacation_repo.get_vacation_patterns_analysis(
        team_id=5, 
        year=2024
    )
    
    # Tendencias temporales
    trends = await vacation_repo.get_vacation_trends(
        start_date=date(2024, 1, 1),
        end_date=date(2024, 12, 31),
        granularity="monthly"
    )
    
    # Reporte completo
    report = await vacation_repo.generate_vacation_summary_report(
        year=2024,
        include_projections=True
    )
    ```

Interfaces Disponibles:
    - IVacationCrudOperations: Operaciones CRUD básicas
    - IVacationQueryOperations: Consultas y búsquedas avanzadas
    - IVacationValidationOperations: Validaciones y reglas de negocio
    - IVacationRelationshipOperations: Gestión de relaciones
    - IVacationStatisticsOperations: Análisis estadístico y reportes

Módulos de Implementación:
    - VacationCrudModule: Implementa operaciones CRUD
    - VacationQueryModule: Implementa consultas avanzadas
    - VacationValidationModule: Implementa validaciones
    - VacationRelationshipModule: Implementa gestión de relaciones
    - VacationStatisticsModule: Implementa análisis estadístico

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Open/Closed: Abierto para extensión, cerrado para modificación
    - Liskov Substitution: Las implementaciones son intercambiables
    - Interface Segregation: Interfaces pequeñas y cohesivas
    - Dependency Inversion: Dependencia de abstracciones

Manejo de Errores:
    - VacationRepositoryError: Error base del repositorio
    - Logging estructurado con Loguru
    - Contexto enriquecido en excepciones
    - Rollback automático en transacciones

Performance:
    - Consultas optimizadas con SQLAlchemy
    - Lazy/Eager loading apropiado
    - Paginación eficiente
    - Índices de base de datos optimizados
    - Cache de consultas frecuentes

Seguridad:
    - Validación de entrada robusta
    - Sanitización de datos
    - Prevención de inyección SQL
    - Logging de operaciones sensibles
"""

from .vacation_repository_facade import VacationRepositoryFacade

# Importar interfaces para uso directo si es necesario
from .interfaces import (
    IVacationCrudOperations,
    IVacationQueryOperations,
    IVacationValidationOperations,
    IVacationRelationshipOperations,
    IVacationStatisticsOperations
)

# Importar módulos para uso directo si es necesario
from .modules import (
    VacationCrudModule,
    VacationQueryModule,
    VacationValidationModule,
    VacationRelationshipModule,
    VacationStatisticsModule
)

__all__ = [
    # Fachada principal (punto de entrada recomendado)
    'VacationRepositoryFacade',
    
    # Interfaces (para tipado y contratos)
    'IVacationCrudOperations',
    'IVacationQueryOperations',
    'IVacationValidationOperations',
    'IVacationRelationshipOperations',
    'IVacationStatisticsOperations',
    
    # Módulos (para uso directo si es necesario)
    'VacationCrudModule',
    'VacationQueryModule',
    'VacationValidationModule',
    'VacationRelationshipModule',
    'VacationStatisticsModule'
]