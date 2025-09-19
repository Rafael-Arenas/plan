# src/planificador/repositories/workload/interfaces/relationship_interface.py

"""
Interfaz para operaciones de relaciones del repositorio Workload.

Este módulo define la interfaz abstracta para las operaciones de gestión
de relaciones entre cargas de trabajo y otras entidades del sistema.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para relaciones
    - Relationship Management: Gestión de asociaciones entre entidades
    - Single Responsibility: Solo operaciones de relaciones

Uso:
    ```python
    class WorkloadRelationshipModule(IWorkloadRelationshipOperations):
        async def get_employee_workloads(self, employee_id: int) -> List[Workload]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.workload import Workload
from planificador.exceptions.repository import WorkloadRepositoryError


class IWorkloadRelationshipOperations(ABC):
    """
    Interfaz abstracta para operaciones de relaciones de cargas de trabajo.
    
    Define los métodos de gestión de relaciones que debe implementar cualquier
    módulo que maneje asociaciones entre cargas de trabajo y otras entidades
    como empleados, proyectos y equipos.
    
    Incluye operaciones para obtener relaciones, validar asociaciones y
    gestionar dependencias entre entidades.
    """

    # Relaciones con Empleados
    @abstractmethod
    async def get_employee_workloads(self, employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo asociadas a un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del empleado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_employee_projects(self, employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proyectos en los que trabaja un empleado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de proyectos con información de carga
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    # Relaciones con Proyectos
    @abstractmethod
    async def get_project_workloads(self, project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo asociadas a un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_project_employees(self, project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los empleados que trabajan en un proyecto.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de empleados con información de carga
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    # Relaciones con Equipos
    @abstractmethod
    async def get_team_workloads(self, team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo de los miembros de un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def get_team_projects(self, team_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Dict[str, Any]]:
        """
        Obtiene todos los proyectos en los que trabaja un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del filtro (opcional)
            end_date: Fecha de fin del filtro (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de proyectos con información de carga del equipo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    # Validación de Relaciones
    @abstractmethod
    async def validate_employee_project_assignment(self, employee_id: int, project_id: int) -> bool:
        """
        Valida si un empleado puede ser asignado a un proyecto.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
        
        Returns:
            bool: True si la asignación es válida
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la validación
        """
        pass

    @abstractmethod
    async def check_workload_conflicts(self, employee_id: int, workload_date: date, hours: float, exclude_workload_id: Optional[int] = None) -> List[Dict[str, Any]]:
        """
        Verifica conflictos de carga de trabajo para un empleado en una fecha.
        
        Args:
            employee_id: ID del empleado
            workload_date: Fecha de la carga de trabajo
            hours: Horas a asignar
            exclude_workload_id: ID de carga a excluir de la verificación (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de conflictos encontrados
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la verificación
        """
        pass

    # Análisis de Relaciones
    @abstractmethod
    async def get_cross_project_employees(self, start_date: date, end_date: date) -> List[Dict[str, Any]]:
        """
        Identifica empleados que trabajan en múltiples proyectos.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
        
        Returns:
            List[Dict[str, Any]]: Empleados con múltiples proyectos y sus cargas
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass

    @abstractmethod
    async def get_project_dependencies(self, project_id: int) -> Dict[str, Any]:
        """
        Analiza las dependencias de recursos de un proyecto.
        
        Args:
            project_id: ID del proyecto
        
        Returns:
            Dict[str, Any]: Información de dependencias y recursos críticos
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el análisis
        """
        pass