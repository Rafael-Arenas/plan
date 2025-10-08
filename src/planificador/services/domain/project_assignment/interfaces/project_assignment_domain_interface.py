# src/planificador/services/domain/project_assignment/interfaces/project_assignment_domain_interface.py

"""
Interfaz Principal del Servicio de Dominio de Asignaciones de Proyecto

Esta interfaz define el contrato completo para el servicio de dominio de asignaciones,
integrando todas las categorías de operaciones siguiendo el patrón Facade.
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional, List
from datetime import date

from .crud_operations_interface import ICrudOperations
from .employee_queries_interface import IEmployeeQueries
from .project_queries_interface import IProjectQueries
from .search_operations_interface import ISearchOperations
from .resource_management_interface import IResourceManagement
from .statistics_operations_interface import IStatisticsOperations
from .validation_operations_interface import IValidationOperations
from .diagnostic_operations_interface import IDiagnosticOperations


class IProjectAssignmentDomainService(
    ICrudOperations,
    IEmployeeQueries,
    IProjectQueries,
    ISearchOperations,
    IResourceManagement,
    IStatisticsOperations,
    IValidationOperations,
    IDiagnosticOperations,
    ABC
):
    """
    Interfaz principal del servicio de dominio de asignaciones de proyecto.
    
    Esta interfaz actúa como Facade, proporcionando un punto único de acceso
    a todas las funcionalidades del dominio de asignaciones. Integra las
    siguientes categorías de operaciones:
    
    - CRUD Operations: Operaciones básicas y especializadas
    - Employee Queries: Consultas centradas en empleados
    - Project Queries: Consultas centradas en proyectos
    - Search Operations: Búsquedas y filtrado avanzado
    - Resource Management: Gestión de recursos y transferencias
    - Statistics Operations: Estadísticas básicas y avanzadas
    - Validation Operations: Validación de reglas de negocio
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
    async def cleanup_service(self) -> None:
        """
        Limpia recursos y conexiones del servicio.
        
        Este método debe ser llamado al finalizar el uso del servicio
        para liberar recursos y cerrar conexiones de manera adecuada.
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