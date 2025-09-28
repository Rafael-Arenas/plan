"""Interface para operaciones de consulta de asignaciones de proyectos.

Define el contrato para consultas complejas y búsquedas especializadas
de la entidad ProjectAssignment.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any

from planificador.models.project_assignment import ProjectAssignment


class IQueryOperations(ABC):
    """Interface para operaciones de consulta de asignaciones de proyectos."""

    @abstractmethod
    async def get_all_assignments(
        self, limit: int | None = None, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones con paginación opcional.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones
        """
        pass

    @abstractmethod
    async def get_assignments_by_employee(
        self, employee_id: int, include_inactive: bool = False
    ) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            Lista de asignaciones del empleado
        """
        pass

    @abstractmethod
    async def get_assignments_by_project(
        self, project_id: int, include_inactive: bool = False
    ) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones de un proyecto.
        
        Args:
            project_id: ID del proyecto
            include_inactive: Si incluir asignaciones inactivas
            
        Returns:
            Lista de asignaciones del proyecto
        """
        pass

    @abstractmethod
    async def get_active_assignments(self) -> list[ProjectAssignment]:
        """Obtiene todas las asignaciones activas en la fecha actual.
        
        Returns:
            Lista de asignaciones activas
        """
        pass

    @abstractmethod
    async def get_assignments_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones que se superponen con un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            Lista de asignaciones en el rango
        """
        pass

    @abstractmethod
    async def get_assignments_by_role(self, role: str) -> list[ProjectAssignment]:
        """Obtiene asignaciones por rol en el proyecto.
        
        Args:
            role: Rol a buscar
            
        Returns:
            Lista de asignaciones con ese rol
        """
        pass

    @abstractmethod
    async def search_assignments_by_filters(
        self, filters: dict[str, Any], limit: int = 50, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Busca asignaciones usando múltiples filtros.
        
        Args:
            filters: Diccionario de filtros a aplicar
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones que coinciden con los filtros
        """
        pass

    @abstractmethod
    async def get_overlapping_assignments(
        self, employee_id: int, start_date: date, end_date: date | None = None
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones que se superponen con un período dado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período (opcional)
            
        Returns:
            Lista de asignaciones superpuestas
        """
        pass