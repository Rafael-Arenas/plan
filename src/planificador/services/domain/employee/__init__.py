# -*- coding: utf-8 -*-
"""
Employee Domain Service Package

Servicio de dominio completo para la gestión de empleados en el sistema Planificador.
Proporciona una interfaz unificada para todas las operaciones relacionadas con empleados.

Main Components:
    - EmployeeDomainService: Servicio principal que actúa como fachada
    - Interfaces: Contratos para operaciones especializadas
    - Modules: Implementaciones concretas de las interfaces

Features:
    - Operaciones CRUD completas con validaciones de negocio
    - Consultas avanzadas y filtros complejos
    - Gestión de relaciones jerárquicas (manager-subordinado)
    - Operaciones especializadas en fechas y tiempo
    - Generación de estadísticas y reportes
    - Validaciones robustas de reglas de negocio
    - Monitoreo de salud del servicio
    - Manejo de errores estructurado
    - Logging detallado con Loguru

Architecture:
    - Patrón Facade para simplificar la interfaz
    - Separación de responsabilidades por módulos
    - Inyección de dependencias
    - Interfaces bien definidas
    - Implementación asíncrona completa
"""

from .employee_domain_service import EmployeeDomainService

__all__ = [
    "EmployeeDomainService",
]