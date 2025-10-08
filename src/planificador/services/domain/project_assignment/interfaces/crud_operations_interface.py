# src/planificador/services/domain/project_assignment/interfaces/crud_operations_interface.py

"""
Interfaz para Operaciones CRUD de Asignaciones de Proyecto

Define el contrato para operaciones de creación, lectura, actualización y eliminación
tanto básicas como especializadas para asignaciones de proyecto.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import datetime

from planificador.schemas import (
    ProjectAssignment,
    ProjectAssignmentCreate,
    ProjectAssignmentUpdate,
)


class ICrudOperations(ABC):
    """
    Interfaz para operaciones CRUD de asignaciones de proyecto.
    
    Incluye tanto operaciones básicas (crear, leer, actualizar, eliminar)
    como operaciones especializadas (bulk, duplicar, archivar).
    """
    
    # ============================================================================
    # OPERACIONES CRUD PRINCIPALES (4 métodos)
    # ============================================================================
    
    @abstractmethod
    async def create_assignment(
        self, 
        assignment_data: ProjectAssignmentCreate
    ) -> ProjectAssignment:
        """
        Crea una nueva asignación con validaciones completas de negocio.
        
        Args:
            assignment_data: Datos de la asignación a crear
            
        Returns:
            ProjectAssignment: Asignación creada con datos completos
            
        Raises:
            ValidationError: Si los datos no cumplen las reglas de negocio
            RepositoryError: Si hay errores en la persistencia
        """
        pass
    
    @abstractmethod
    async def update_assignment(
        self, 
        assignment_id: int, 
        update_data: ProjectAssignmentUpdate
    ) -> ProjectAssignment:
        """
        Actualiza una asignación existente con validaciones de solapamiento.
        
        Args:
            assignment_id: ID de la asignación a actualizar
            update_data: Datos de actualización
            
        Returns:
            ProjectAssignment: Asignación actualizada
            
        Raises:
            ValidationError: Si la actualización genera conflictos
            RepositoryError: Si hay errores en la persistencia
        """
        pass
    
    @abstractmethod
    async def delete_assignment(self, assignment_id: int) -> bool:
        """
        Elimina una asignación después de validar dependencias y impacto.
        
        Args:
            assignment_id: ID de la asignación a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía
            
        Raises:
            ValidationError: Si la eliminación afecta dependencias críticas
            RepositoryError: Si hay errores en la persistencia
        """
        pass
    
    @abstractmethod
    async def get_assignment_by_id(self, assignment_id: int) -> Optional[ProjectAssignment]:
        """
        Obtiene una asignación por su ID único con datos relacionados.
        
        Args:
            assignment_id: ID de la asignación a obtener
            
        Returns:
            Optional[ProjectAssignment]: Asignación encontrada o None
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    # ============================================================================
    # OPERACIONES CRUD ESPECIALIZADAS (3 métodos)
    # ============================================================================
    
    @abstractmethod
    async def bulk_create_assignments(
        self, 
        assignments_data: List[ProjectAssignmentCreate]
    ) -> List[ProjectAssignment]:
        """
        Crea múltiples asignaciones en una operación transaccional con validaciones cruzadas.
        
        Args:
            assignments_data: Lista de datos de asignaciones a crear
            
        Returns:
            List[ProjectAssignment]: Lista de asignaciones creadas
            
        Raises:
            ValidationError: Si alguna asignación no cumple las reglas
            RepositoryError: Si hay errores en la transacción
        """
        pass
    
    @abstractmethod
    async def duplicate_assignment(
        self, 
        source_assignment_id: int, 
        modifications: Optional[dict] = None
    ) -> ProjectAssignment:
        """
        Duplica una asignación existente con nuevos parámetros.
        
        Args:
            source_assignment_id: ID de la asignación a duplicar
            modifications: Modificaciones opcionales para la nueva asignación
            
        Returns:
            ProjectAssignment: Nueva asignación duplicada
            
        Raises:
            NotFoundError: Si la asignación original no existe
            ValidationError: Si los nuevos datos no son válidos
            RepositoryError: Si hay errores en la persistencia
        """
        pass
    
    @abstractmethod
    async def archive_assignment(self, assignment_id: int) -> ProjectAssignment:
        """
        Archiva una asignación manteniendo el historial para auditoría.
        
        Args:
            assignment_id: ID de la asignación a archivar
            
        Returns:
            ProjectAssignment: Asignación archivada
            
        Raises:
            ValidationError: Si la asignación no puede ser archivada
            RepositoryError: Si hay errores en la persistencia
        """
        pass