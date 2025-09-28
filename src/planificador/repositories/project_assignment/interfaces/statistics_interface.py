"""Interface para operaciones de estadísticas de asignaciones de proyectos.

Define el contrato para cálculos de métricas y estadísticas
relacionadas con las asignaciones de proyectos.
"""

from abc import ABC, abstractmethod
from datetime import date
from typing import Any


class IStatisticsOperations(ABC):
    """Interface para operaciones de estadísticas de asignaciones de proyectos."""

    @abstractmethod
    async def get_assignment_count(self) -> int:
        """Obtiene el número total de asignaciones.
        
        Returns:
            Número total de asignaciones
        """
        pass

    @abstractmethod
    async def get_active_assignment_count(self) -> int:
        """Obtiene el número de asignaciones activas.
        
        Returns:
            Número de asignaciones activas
        """
        pass

    @abstractmethod
    async def get_assignments_by_status(self) -> dict[str, int]:
        """Obtiene el conteo de asignaciones por estado.
        
        Returns:
            Diccionario con conteos por estado
        """
        pass

    @abstractmethod
    async def get_assignments_by_allocation_category(self) -> dict[str, int]:
        """Obtiene el conteo de asignaciones por categoría de dedicación.
        
        Returns:
            Diccionario con conteos por categoría de dedicación
        """
        pass

    @abstractmethod
    async def get_employee_assignment_stats(self, employee_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de asignaciones de un empleado específico.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con estadísticas del empleado
        """
        pass

    @abstractmethod
    async def get_project_assignment_stats(self, project_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de asignaciones de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con estadísticas del proyecto
        """
        pass

    @abstractmethod
    async def get_assignment_duration_stats(self) -> dict[str, Any]:
        """Obtiene estadísticas de duración de asignaciones.
        
        Returns:
            Diccionario con estadísticas de duración
        """
        pass

    @abstractmethod
    async def get_workload_distribution(self) -> dict[str, Any]:
        """Obtiene la distribución de carga de trabajo.
        
        Returns:
            Diccionario con distribución de carga de trabajo
        """
        pass

    @abstractmethod
    async def get_assignment_trends(
        self, days: int = 30, group_by: str = "day"
    ) -> list[dict[str, Any]]:
        """Obtiene tendencias de creación de asignaciones.
        
        Args:
            days: Número de días hacia atrás
            group_by: Agrupación temporal ("day", "week", "month")
            
        Returns:
            Lista de datos de tendencias
        """
        pass

    @abstractmethod
    async def get_overlap_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas de superposición de asignaciones.
        
        Returns:
            Diccionario con estadísticas de superposición
        """
        pass

    @abstractmethod
    async def get_role_distribution(self) -> dict[str, int]:
        """Obtiene la distribución de roles en proyectos.
        
        Returns:
            Diccionario con conteos por rol
        """
        pass

    @abstractmethod
    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """Obtiene métricas completas para dashboard.
        
        Returns:
            Diccionario con métricas completas
        """
        pass