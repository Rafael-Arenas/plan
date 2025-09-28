"""Interface para operaciones de relaciones de asignaciones de proyectos.

Define el contrato para gestionar las relaciones entre asignaciones,
empleados y proyectos.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.project_assignment import ProjectAssignment


class IRelationshipOperations(ABC):
    """Interface para operaciones de relaciones de asignaciones de proyectos."""

    @abstractmethod
    async def get_assignments_with_employee_data(
        self, limit: int = 50, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con datos del empleado cargados.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones con datos del empleado
        """
        pass

    @abstractmethod
    async def get_assignments_with_project_data(
        self, limit: int = 50, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con datos del proyecto cargados.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones con datos del proyecto
        """
        pass

    @abstractmethod
    async def get_assignments_with_full_data(
        self, limit: int = 50, offset: int = 0
    ) -> list[ProjectAssignment]:
        """Obtiene asignaciones con todos los datos relacionados cargados.
        
        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Lista de asignaciones con datos completos
        """
        pass

    @abstractmethod
    async def transfer_employee_assignments(
        self, from_employee_id: int, to_employee_id: int, project_id: int | None = None
    ) -> bool:
        """Transfiere asignaciones de un empleado a otro.
        
        Args:
            from_employee_id: ID del empleado origen
            to_employee_id: ID del empleado destino
            project_id: ID del proyecto específico (opcional)
            
        Returns:
            True si se transfirieron correctamente
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la transferencia
        """
        pass

    @abstractmethod
    async def reassign_project_assignments(
        self, from_project_id: int, to_project_id: int
    ) -> bool:
        """Reasigna todas las asignaciones de un proyecto a otro.
        
        Args:
            from_project_id: ID del proyecto origen
            to_project_id: ID del proyecto destino
            
        Returns:
            True si se reasignaron correctamente
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la reasignación
        """
        pass

    @abstractmethod
    async def get_employee_workload_summary(self, employee_id: int) -> dict[str, Any]:
        """Obtiene un resumen de la carga de trabajo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con resumen de carga de trabajo
        """
        pass

    @abstractmethod
    async def get_project_team_summary(self, project_id: int) -> dict[str, Any]:
        """Obtiene un resumen del equipo asignado a un proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Diccionario con resumen del equipo
        """
        pass