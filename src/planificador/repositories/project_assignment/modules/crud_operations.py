"""Módulo de operaciones CRUD para asignaciones de proyectos.

Este módulo implementa la interfaz ICrudOperations y contiene todas las
operaciones básicas de creación, lectura, actualización y eliminación
de asignaciones de proyectos, delegando la lógica al BaseRepository.
"""

from typing import Any

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models.project_assignment import ProjectAssignment
from planificador.repositories.base_repository import BaseRepository
from ..interfaces.crud_interface import ICrudOperations


class CrudOperations(BaseRepository[ProjectAssignment], ICrudOperations):
    """Implementación de operaciones CRUD para asignaciones de proyectos.
    
    Hereda de BaseRepository para reutilizar la lógica CRUD y se
    especializa para la entidad ProjectAssignment.
    """

    def __init__(self, session: AsyncSession):
        """Inicializa las operaciones CRUD.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        super().__init__(session, ProjectAssignment)
        self._logger = self._logger.bind(component="ProjectAssignmentCrudOperations")
        self._logger.debug("CrudOperations para ProjectAssignment inicializado")

    async def create_assignment(self, assignment_data: dict[str, Any]) -> ProjectAssignment:
        """Crea una nueva asignación de proyecto delegando en el repositorio base.
        
        Args:
            assignment_data: Datos de la asignación a crear
            
        Returns:
            Asignación creada
        """
        self._logger.debug(f"Creando asignación con datos: {assignment_data}")
        return await self.create(assignment_data)

    async def update_assignment(
        self, assignment_id: int, assignment_data: dict[str, Any]
    ) -> ProjectAssignment | None:
        """Actualiza una asignación existente delegando en el repositorio base.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            assignment_data: Datos actualizados de la asignación
            
        Returns:
            Asignación actualizada o None si no existe
        """
        self._logger.debug(
            f"Actualizando asignación ID {assignment_id} con datos: {assignment_data}"
        )
        return await self.update(assignment_id, assignment_data)

    async def delete_assignment(self, assignment_id: int) -> bool:
        """Elimina una asignación delegando en el repositorio base.
        
        Args:
            assignment_id: ID de la asignación a eliminar
            
        Returns:
            True si se eliminó correctamente, False en caso contrario
        """
        self._logger.debug(f"Eliminando asignación ID {assignment_id}")
        return await self.delete(assignment_id)

    async def get_assignment_by_id(self, assignment_id: int) -> ProjectAssignment | None:
        """Obtiene una asignación por su ID delegando en el repositorio base.
        
        Args:
            assignment_id: ID de la asignación
            
        Returns:
            Asignación encontrada o None si no existe
        """
        self._logger.debug(f"Obteniendo asignación por ID: {assignment_id}")
        return await self.get_by_id(assignment_id)