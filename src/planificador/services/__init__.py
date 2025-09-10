# src/planificador/services/__init__.py

"""
Servicios - Services

Este módulo contiene la capa de servicios de la aplicación, que implementa
la lógica de negocio y coordina las operaciones entre diferentes componentes.

La capa de servicios se divide en dos categorías principales:

## Domain Services (Servicios de Dominio)
Implementan la lógica de negocio específica del dominio de la aplicación.
Son responsables de:
- Validaciones de reglas de negocio
- Coordinación entre múltiples repositorios
- Transformaciones de datos específicas del dominio
- Orquestación de transacciones complejas

## Infrastructure Services (Servicios de Infraestructura)
Manejan aspectos técnicos e infraestructura de la aplicación.
Son responsables de:
- Envío de emails y notificaciones
- Almacenamiento de archivos
- Integración con APIs externas
- Logging y monitoreo
- Caché y optimizaciones de performance

Arquitectura:
    UI/API → Domain Services → Repositories → Database
             ↕
        Infrastructure Services

Ejemplos:
- Domain: ClientService, ProjectService, EmployeeService
- Infrastructure: EmailService, FileStorageService, NotificationService
"""

# Importaciones de servicios de dominio
from .domain import (
    BaseDomainService,
    ClientService,
    ProjectService,
    EmployeeService,
    TeamService,
    AssignmentService,
    ScheduleService,
    WorkloadService,
    VacationService,
    AlertService,
)

# Importaciones de servicios de infraestructura
# (Se agregarán cuando se implementen)

__all__ = [
    # Domain Services
    "BaseDomainService",
    "ClientService",
    "ProjectService",
    "EmployeeService",
    "TeamService",
    "AssignmentService",
    "ScheduleService",
    "WorkloadService",
    "VacationService",
    "AlertService",
    
    # Infrastructure Services
    # (Se agregarán cuando se implementen)
]