# src/planificador/repositories/vacation/modules/__init__.py

"""
Módulos de implementación del repositorio Vacation.

Este paquete contiene todos los módulos especializados que implementan
las operaciones del repositorio Vacation siguiendo el patrón de segregación
de interfaces y responsabilidad única.

Módulos Disponibles:
    - VacationCrudModule: Operaciones CRUD básicas (crear, leer, actualizar, eliminar)
    - VacationQueryModule: Operaciones de consulta y búsqueda avanzada
    - VacationValidationModule: Validaciones de datos y reglas de negocio
    - VacationRelationshipModule: Gestión de relaciones con otras entidades
    - VacationStatisticsModule: Análisis estadístico y reportes

Principios de Diseño:
    - Single Responsibility: Cada módulo tiene una responsabilidad específica
    - Interface Segregation: Interfaces pequeñas y cohesivas
    - Dependency Inversion: Dependencia de abstracciones, no implementaciones
    - Open/Closed: Abierto para extensión, cerrado para modificación

Uso:
    ```python
    from planificador.repositories.vacation.modules import (
        VacationCrudModule,
        VacationQueryModule,
        VacationValidationModule,
        VacationRelationshipModule,
        VacationStatisticsModule
    )
    
    # Inicializar módulos
    crud_module = VacationCrudModule(session)
    query_module = VacationQueryModule(session)
    validation_module = VacationValidationModule(session)
    relationship_module = VacationRelationshipModule(session)
    statistics_module = VacationStatisticsModule(session)
    ```

Ejemplo de Uso Integrado:
    ```python
    # Crear una nueva vacación con validaciones completas
    vacation_data = {
        'employee_id': 1,
        'vacation_type': 'ANNUAL',
        'start_date': date(2024, 6, 1),
        'end_date': date(2024, 6, 10),
        'days_requested': 8,
        'reason': 'Vacaciones familiares'
    }
    
    # Validar datos antes de crear
    validation_result = await validation_module.validate_vacation_data(vacation_data)
    if validation_result['is_valid']:
        # Verificar conflictos
        conflicts = await relationship_module.check_vacation_conflicts(
            vacation_data['employee_id'],
            vacation_data['start_date'],
            vacation_data['end_date']
        )
        
        if not conflicts:
            # Crear la vacación
            vacation = await crud_module.create_vacation(vacation_data)
            
            # Obtener estadísticas actualizadas
            stats = await statistics_module.get_employee_vacation_statistics(
                vacation_data['employee_id']
            )
    ```
"""

from .crud_module import VacationCrudModule
from .query_module import VacationQueryModule
from .validation_module import VacationValidationModule
from .relationship_module import VacationRelationshipModule
from .statistics_module import VacationStatisticsModule

__all__ = [
    'VacationCrudModule',
    'VacationQueryModule', 
    'VacationValidationModule',
    'VacationRelationshipModule',
    'VacationStatisticsModule'
]