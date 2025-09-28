# src/planificador/services/domain/__init__.py

"""
Módulo de servicios de dominio del sistema Planificador.

Este módulo contiene los servicios de dominio que implementan la lógica de negocio
compleja y coordinan operaciones entre múltiples repositorios y dominios.

Los servicios de dominio proporcionan:
- Lógica de negocio compleja que trasciende entidades individuales
- Coordinación entre múltiples repositorios
- Validaciones de reglas de negocio complejas
- Análisis y reportes de negocio
- Gestión del ciclo de vida de entidades
- Sincronización entre dominios

Estructura modular:
- client/: Servicios de dominio para gestión integral de clientes
- employee/: Servicios de dominio para gestión de empleados (futuro)
- project/: Servicios de dominio para gestión de proyectos (futuro)
- planning/: Servicios de dominio para planificación de recursos (futuro)
- resource_management/: Servicios de gestión de recursos humanos (futuro)
- analytics/: Servicios de análisis y métricas de negocio (futuro)
"""

from .base_domain_service import BaseDomainService
from .client import IClientDomainService, ClientDomainService

# Exportar servicios de dominio disponibles
__all__ = [
    # Servicio base
    'BaseDomainService',
    
    # Servicios de dominio de clientes
    'IClientDomainService',
    'ClientDomainService',
]

# Metadatos del módulo
__version__ = '1.0.0'
__author__ = 'Planificador Development Team'
__description__ = 'Servicios de dominio para lógica de negocio compleja'

# Configuración de servicios disponibles
AVAILABLE_DOMAIN_SERVICES = {
    'client': {
        'interface': IClientDomainService,
        'implementation': ClientDomainService,
        'description': 'Servicio de dominio para gestión integral de clientes',
        'module': 'client',
        'capabilities': [
            'client_lifecycle_management',
            'portfolio_analysis', 
            'project_coordination',
            'business_rule_validation',
            'reporting_and_metrics',
            'cross_domain_coordination'
        ]
    }
    # Futuros servicios de dominio se agregarán aquí siguiendo la misma estructura:
    # 'employee': {...},
    # 'project': {...},
    # 'planning': {...},
    # 'resource_management': {...},
    # 'analytics': {...}
}

def get_available_services():
    """
    Retorna información sobre los servicios de dominio disponibles.
    
    Returns:
        Dict con información de servicios disponibles
    """
    return AVAILABLE_DOMAIN_SERVICES

def get_service_info(service_name: str):
    """
    Obtiene información específica de un servicio de dominio.
    
    Args:
        service_name: Nombre del servicio
        
    Returns:
        Información del servicio o None si no existe
    """
    return AVAILABLE_DOMAIN_SERVICES.get(service_name)

def get_service_capabilities(service_name: str):
    """
    Obtiene las capacidades de un servicio de dominio específico.
    
    Args:
        service_name: Nombre del servicio
        
    Returns:
        Lista de capacidades del servicio o None si no existe
    """
    service_info = AVAILABLE_DOMAIN_SERVICES.get(service_name)
    return service_info.get('capabilities', []) if service_info else None

def list_available_modules():
    """
    Lista todos los módulos de servicios de dominio disponibles.
    
    Returns:
        Lista de nombres de módulos disponibles
    """
    return [service['module'] for service in AVAILABLE_DOMAIN_SERVICES.values()]