# src/planificador/services/domain/client/__init__.py

"""
Módulo de servicios de dominio para la gestión integral de clientes.

Este módulo contiene los servicios de dominio específicos para clientes,
implementando lógica de negocio compleja que coordina operaciones entre
múltiples repositorios y dominios relacionados con la gestión de clientes.

Funcionalidades principales:
- Gestión completa del ciclo de vida del cliente
- Análisis de rentabilidad y portafolio de clientes
- Coordinación con proyectos y asignaciones
- Validaciones de reglas de negocio específicas
- Reportes y métricas de negocio
- Transferencia y gestión de proyectos de clientes
"""

from .client_domain_service import ClientDomainService
from .interfaces.client_service_interface import IClientDomainService

# Exportar servicios y interfaces del dominio de clientes
__all__ = [
    # Interfaz del servicio
    'IClientDomainService',
    
    # Implementación del servicio
    'ClientDomainService',
]

# Metadatos del módulo
__version__ = '1.0.0'
__author__ = 'Planificador Development Team'
__description__ = 'Servicios de dominio para gestión integral de clientes'

# Configuración del módulo de clientes
CLIENT_DOMAIN_CONFIG = {
    'service_name': 'ClientDomainService',
    'interface': IClientDomainService,
    'implementation': ClientDomainService,
    'description': 'Servicio de dominio para gestión integral de clientes',
    'dependencies': [
        'ClientRepositoryFacade',
        'ProjectRepositoryFacade', 
        'ProjectAssignmentRepositoryFacade'
    ],
    'capabilities': [
        'client_lifecycle_management',
        'portfolio_analysis',
        'project_coordination',
        'business_rule_validation',
        'reporting_and_metrics',
        'cross_domain_coordination'
    ]
}

def get_client_service_info():
    """
    Retorna información sobre el servicio de dominio de clientes.
    
    Returns:
        Dict con información del servicio de clientes
    """
    return CLIENT_DOMAIN_CONFIG

def create_client_service(session):
    """
    Factory method para crear una instancia del servicio de dominio de clientes.
    
    Args:
        session: Sesión de base de datos SQLAlchemy
        
    Returns:
        Instancia de ClientDomainService
    """
    return ClientDomainService(session)