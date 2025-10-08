"""
Paquete del Servicio de Dominio Schedule.

Este paquete contiene toda la lógica de dominio para la gestión de horarios,
incluyendo interfaces, implementaciones y el servicio principal integrado.

El servicio de dominio Schedule proporciona:
- Operaciones CRUD básicas
- Consultas especializadas por empleado, proyecto y equipo
- Búsqueda y filtrado avanzado
- Gestión de confirmaciones y flujos de trabajo
- Estadísticas y análisis de productividad
- Validaciones de reglas de negocio
- Diagnósticos y monitoreo del sistema

Uso típico:
    from planificador.services.domain.schedule import ScheduleDomainService
    
    # Crear instancia del servicio
    schedule_service = ScheduleDomainService()
    
    # Usar operaciones específicas
    await schedule_service.crud.create_schedule(schedule_data)
    await schedule_service.employee.get_employee_schedules(employee_id)
    await schedule_service.statistics.generate_weekly_hours_report(week_start)
"""

from .schedule_domain_service import ScheduleDomainService

# Importar interfaces para uso externo si es necesario
from .interfaces import (
    IScheduleDomainCrudOperations,
    IScheduleDomainEmployeeOperations,
    IScheduleDomainProjectOperations,
    IScheduleDomainTeamOperations,
    IScheduleDomainSearchOperations,
    IScheduleDomainConfirmationOperations,
    IScheduleDomainStatisticsOperations,
    IScheduleDomainProductivityOperations,
    IScheduleDomainValidationOperations,
    IScheduleDomainDiagnosticOperations
)

# Importar implementaciones para uso externo si es necesario
from .module import (
    ScheduleDomainCrudOperations,
    ScheduleDomainEmployeeOperations,
    ScheduleDomainProjectOperations,
    ScheduleDomainTeamOperations,
    ScheduleDomainSearchOperations,
    ScheduleDomainConfirmationOperations,
    ScheduleDomainStatisticsOperations,
    ScheduleDomainProductivityOperations,
    ScheduleDomainValidationOperations,
    ScheduleDomainDiagnosticOperations
)

__all__ = [
    # Servicio principal (punto de entrada recomendado)
    "ScheduleDomainService",
    
    # Interfaces (para implementaciones personalizadas)
    "IScheduleDomainCrudOperations",
    "IScheduleDomainEmployeeOperations",
    "IScheduleDomainProjectOperations",
    "IScheduleDomainTeamOperations",
    "IScheduleDomainSearchOperations",
    "IScheduleDomainConfirmationOperations",
    "IScheduleDomainStatisticsOperations",
    "IScheduleDomainProductivityOperations",
    "IScheduleDomainValidationOperations",
    "IScheduleDomainDiagnosticOperations",
    
    # Implementaciones (para uso directo si es necesario)
    "ScheduleDomainCrudOperations",
    "ScheduleDomainEmployeeOperations",
    "ScheduleDomainProjectOperations",
    "ScheduleDomainTeamOperations",
    "ScheduleDomainSearchOperations",
    "ScheduleDomainConfirmationOperations",
    "ScheduleDomainStatisticsOperations",
    "ScheduleDomainProductivityOperations",
    "ScheduleDomainValidationOperations",
    "ScheduleDomainDiagnosticOperations",
]

# Información del paquete
__version__ = "1.0.0"
__author__ = "Planificador Development Team"
__description__ = "Servicio de Dominio para gestión integral de horarios"