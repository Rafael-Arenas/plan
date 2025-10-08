# src/planificador/services/domain/schedule/interfaces/schedule_domain_interface.py

"""
Interfaz Principal del Servicio de Dominio de Horarios (Schedule)

Esta interfaz define el contrato completo para el servicio de dominio de horarios,
integrando todas las categorías de operaciones siguiendo el patrón Facade.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import date

from .crud_operations import IScheduleDomainCrudOperations
from .employee_operations import IScheduleDomainEmployeeOperations
from .project_operations import IScheduleDomainProjectOperations
from .team_operations import IScheduleDomainTeamOperations
from .search_operations import IScheduleDomainSearchOperations
from .confirmation_operations import IScheduleDomainConfirmationOperations
from .statistics_operations import IScheduleDomainStatisticsOperations
from .productivity_operations import IScheduleDomainProductivityOperations
from .validation_operations import IScheduleDomainValidationOperations
from .diagnostic_operations import IScheduleDomainDiagnosticOperations


class IScheduleDomainService(
    IScheduleDomainCrudOperations,
    IScheduleDomainEmployeeOperations,
    IScheduleDomainProjectOperations,
    IScheduleDomainTeamOperations,
    IScheduleDomainSearchOperations,
    IScheduleDomainConfirmationOperations,
    IScheduleDomainStatisticsOperations,
    IScheduleDomainProductivityOperations,
    IScheduleDomainValidationOperations,
    IScheduleDomainDiagnosticOperations,
    ABC
):
    """
    Interfaz principal del servicio de dominio de horarios.
    
    Esta interfaz actúa como Facade, proporcionando un punto único de acceso
    a todas las funcionalidades del dominio de horarios. Integra las
    siguientes categorías de operaciones:
    
    - CRUD Operations: Operaciones básicas de creación, lectura, actualización y eliminación
    - Employee Operations: Consultas y operaciones centradas en empleados
    - Project Operations: Consultas y operaciones centradas en proyectos
    - Team Operations: Consultas y operaciones centradas en equipos
    - Search Operations: Búsquedas y filtrado avanzado de horarios
    - Confirmation Operations: Operaciones de confirmación y aprobación
    - Statistics Operations: Estadísticas básicas y avanzadas de horarios
    - Productivity Operations: Análisis de productividad y rendimiento
    - Validation Operations: Validación de reglas de negocio y conflictos
    - Diagnostic Operations: Diagnóstico y salud del servicio
    
    Principios del Facade implementados:
    1. Simplificación: Interfaz unificada para subsistemas complejos
    2. Punto único de acceso: Todas las operaciones disponibles desde una sola clase
    3. Encapsulación: Oculta la complejidad de la coordinación entre repositorios
    4. Mantenibilidad: Facilita cambios sin afectar clientes del servicio
    """

    @abstractmethod
    async def initialize_service(self) -> None:
        """
        Inicializa el servicio de dominio y sus dependencias.
        
        Este método debe ser llamado antes de usar cualquier funcionalidad
        del servicio para garantizar que todas las dependencias estén
        correctamente configuradas.
        """
        pass

    @abstractmethod
    def get_service_info(self) -> Dict[str, Any]:
        """
        Obtiene información general del servicio.
        
        Returns:
            Dict con información del servicio incluyendo versión,
            configuración y estado de las dependencias.
        """
        pass