# src/planificador/services/domain/client/interfaces/__init__.py

"""
Interfaces para los servicios de dominio de clientes.

Este módulo contiene las interfaces que definen los contratos
para los servicios de dominio relacionados con la gestión de clientes.
"""

from .client_service_interface import IClientDomainService

__all__ = [
    'IClientDomainService',
]