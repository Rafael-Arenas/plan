# src/planificador/repositories/schedule/__init__.py

"""
Repositorio Schedule - Gestión de Horarios.

Este paquete implementa el patrón Repository para la gestión de horarios
en el sistema de planificación. Proporciona una interfaz unificada y
consistente para todas las operaciones relacionadas con horarios.

Arquitectura:
    - Facade Pattern: ScheduleRepositoryFacade como punto de entrada único
    - Interface Segregation: Interfaces especializadas por responsabilidad
    - Module Pattern: Módulos especializados para cada tipo de operación
    - Dependency Injection: Inyección de dependencias para flexibilidad

Componentes Principales:
    - ScheduleRepositoryFacade: Fachada principal del repositorio
    - Interfaces: Contratos para operaciones CRUD, consultas y validación
    - Modules: Implementaciones especializadas de las interfaces

Uso Básico:
    ```python
    from planificador.repositories.schedule import ScheduleRepositoryFacade
    from planificador.database.session import get_async_session
    
    async with get_async_session() as session:
        repository = ScheduleRepositoryFacade(session)
        
        # Crear horario
        schedule = await repository.create_schedule({
            'employee_id': 1,
            'project_id': 1,
            'date': date(2024, 1, 15),
            'start_time': time(9, 0),
            'end_time': time(17, 0)
        })
        
        # Consultar horarios
        schedules = await repository.get_schedules_by_employee(1)
        
        # Validar datos
        is_valid = await repository.validate_schedule_data(schedule_data)
    ```
"""

from .schedule_repository_facade import ScheduleRepositoryFacade

# Exportar la fachada principal
__all__ = [
    'ScheduleRepositoryFacade'
]

# Información del módulo
__version__ = '1.0.0'
__author__ = 'AkGroup Development Team'
__description__ = 'Repositorio Schedule para gestión de horarios'