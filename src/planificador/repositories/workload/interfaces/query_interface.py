# src/planificador/repositories/workload/interfaces/query_interface.py

"""
Interfaz para operaciones de consulta del repositorio Workload.

Este módulo define la interfaz abstracta para las operaciones de consulta,
búsqueda y recuperación de cargas de trabajo con filtros avanzados.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para operaciones de consulta
    - Query Optimization: Definición de métodos optimizados para consultas
    - Single Responsibility: Solo operaciones de consulta y búsqueda

Uso:
    ```python
    class WorkloadQueryModule(IWorkloadQueryOperations):
        async def get_by_employee(self, employee_id: int) -> List[Workload]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.workload import Workload
from planificador.exceptions.repository import WorkloadRepositoryError


class IWorkloadQueryOperations(ABC):
    """
    Interfaz abstracta para operaciones de consulta de cargas de trabajo.
    
    Define los métodos de consulta que debe implementar cualquier módulo
    que maneje operaciones de búsqueda y recuperación de cargas de trabajo.
    
    Métodos incluyen consultas por empleado, proyecto, fecha, equipo y
    análisis especializados como empleados sobrecargados o subutilizados.
    """

    # Consultas Básicas
    @abstractmethod
    async def get_by_employee(self, employee_id: int) -> List[Workload]:
        """Obtiene todas las cargas de trabajo de un empleado."""
        pass

    @abstractmethod
    async def get_by_employee_and_date(self, employee_id: int, workload_date: date) -> Optional[Workload]:
        """Busca carga de trabajo específica por empleado y fecha."""
        pass

    @abstractmethod
    async def get_by_employee_date_range(self, employee_id: int, start_date: date, end_date: date) -> List[Workload]:
        """Obtiene cargas de empleado en rango de fechas."""
        pass

    @abstractmethod
    async def get_by_project_and_date(self, project_id: int, workload_date: date) -> List[Workload]:
        """Obtiene cargas de proyecto en fecha específica."""
        pass

    @abstractmethod
    async def get_by_date_range(self, start_date: date, end_date: date) -> List[Workload]:
        """Obtiene todas las cargas en rango de fechas."""
        pass

    @abstractmethod
    async def get_by_project(self, project_id: int) -> List[Workload]:
        """Obtiene todas las cargas de trabajo de un proyecto."""
        pass

    @abstractmethod
    async def get_by_project_date_range(self, project_id: int, start_date: date, end_date: date) -> List[Workload]:
        """Obtiene cargas de proyecto en rango de fechas."""
        pass

    # Consultas Especializadas
    @abstractmethod
    async def get_overloaded_employees(self, target_date: date, threshold_hours: float = 8.0) -> List[Workload]:
        """Obtiene empleados sobrecargados en fecha."""
        pass

    @abstractmethod
    async def get_underutilized_employees(self, target_date: date, threshold_hours: float = 4.0) -> List[Workload]:
        """Obtiene empleados subutilizados en fecha."""
        pass

    @abstractmethod
    async def get_with_relations(self, workload_id: int) -> Optional[Workload]:
        """Obtiene carga con todas las relaciones cargadas."""
        pass

    @abstractmethod
    async def get_team_workload(self, team_id: int, target_date: date) -> List[Dict[str, Any]]:
        """Obtiene carga de trabajo de equipo en fecha específica."""
        pass

    # Métodos de Delegación desde WorkloadRepository
    @abstractmethod
    async def get_workloads_by_employee(self, employee_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]:
        """Obtiene cargas de trabajo de un empleado en rango de fechas."""
        pass

    @abstractmethod
    async def get_workloads_by_date_range(self, start_date: date, end_date: date) -> List[Workload]:
        """Obtiene todas las cargas de trabajo en rango de fechas."""
        pass

    @abstractmethod
    async def get_workloads_by_project(self, project_id: int, start_date: Optional[date] = None, end_date: Optional[date] = None) -> List[Workload]:
        """Obtiene cargas de trabajo de un proyecto específico."""
        pass

    @abstractmethod
    async def get_overloaded_employees_summary(self, target_date: date, threshold_hours: float = 8.0) -> List[Dict[str, Any]]:
        """Identifica empleados con sobrecarga de trabajo."""
        pass

    @abstractmethod
    async def get_underutilized_employees_summary(self, target_date: date, threshold_hours: float = 4.0) -> List[Dict[str, Any]]:
        """Identifica empleados con baja utilización."""
        pass

    @abstractmethod
    async def get_team_workloads(self, team_id: int, start_date: date, end_date: date) -> List[Workload]:
        """Obtiene cargas de trabajo de un equipo en rango de fechas."""
        pass

    @abstractmethod
    async def get_team_workload_summary(self, team_id: int, target_date: date) -> Dict[str, Any]:
        """Obtiene resumen de carga de trabajo de un equipo."""
        pass

    @abstractmethod
    async def get_weekly_workload(self, employee_id: int, week_start: date) -> float:
        """Calcula total de horas trabajadas por empleado en una semana."""
        pass