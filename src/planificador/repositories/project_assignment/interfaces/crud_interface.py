"""Interface para operaciones CRUD de asignaciones de proyectos.

Define el contrato que deben cumplir las implementaciones de operaciones
CRUD (Create, Read, Update, Delete) para la entidad ProjectAssignment.
"""

from abc import ABC, abstractmethod
from typing import Any

from planificador.models.project_assignment import ProjectAssignment


class ICrudOperations(ABC):
    """Interface para operaciones CRUD de asignaciones de proyectos."""

    @abstractmethod
    async def create_assignment(self, assignment_data: dict[str, Any]) -> ProjectAssignment:
        """Crea una nueva asignación de proyecto.
        
        Args:
            assignment_data: Datos de la asignación a crear
            
        Returns:
            Asignación creada
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la creación
        """
        pass

    @abstractmethod
    async def update_assignment(
        self, assignment_id: int, assignment_data: dict[str, Any]
    ) -> ProjectAssignment | None:
        """Actualiza una asignación existente.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            assignment_data: Datos actualizados de la asignación
            
        Returns:
            Asignación actualizada o None si no existe
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la actualización
        """
        pass

    @abstractmethod
    async def delete_assignment(self, assignment_id: int) -> bool:
        """Elimina una asignación.
        
        Args:
            assignment_id: ID de la asignación a eliminar
            
        Returns:
            True si se eliminó correctamente, False si no existe
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la eliminación
        """
        pass

    @abstractmethod
    async def get_assignment_by_id(self, assignment_id: int) -> ProjectAssignment | None:
        """Obtiene una asignación por su ID.
        
        Args:
            assignment_id: ID de la asignación
            
        Returns:
            Asignación encontrada o None si no existe
            
        Raises:
            ProjectAssignmentRepositoryError: Si ocurre un error en la consulta
        """
        pass