# src/planificador/repositories/status_code/interfaces/crud_interface.py

"""
Interfaz para operaciones CRUD de códigos de estado.

Define los métodos básicos de creación, lectura, actualización y eliminación
para la entidad StatusCode, siguiendo el principio de segregación de interfaces.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from planificador.models.status_code import StatusCode


class IStatusCodeCrudOperations(ABC):
    """
    Interfaz abstracta para operaciones CRUD de códigos de estado.
    
    Define los métodos básicos de gestión de datos que debe implementar
    cualquier módulo que maneje operaciones de creación, lectura,
    actualización y eliminación de códigos de estado.
    
    Métodos incluyen operaciones básicas heredadas del BaseRepository
    y operaciones específicas para la gestión de códigos de estado.
    """

    # ==========================================
    # OPERACIONES CRUD BÁSICAS
    # ==========================================

    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> StatusCode:
        """
        Crea un nuevo código de estado.
        
        Args:
            entity_data: Diccionario con los datos del código de estado
            
        Returns:
            StatusCode: El código de estado creado
            
        Raises:
            ValidationError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def update(self, entity_id: int, **update_data) -> StatusCode:
        """
        Actualiza un código de estado existente.
        
        Args:
            entity_id: ID del código de estado a actualizar
            **update_data: Datos a actualizar
            
        Returns:
            StatusCode: El código de estado actualizado
            
        Raises:
            NotFoundError: Si el código de estado no existe
            ValidationError: Si los datos no son válidos
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[StatusCode]:
        """
        Obtiene un código de estado por su ID.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            Optional[StatusCode]: El código de estado o None si no existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """
        Elimina un código de estado.
        
        Args:
            entity_id: ID del código de estado a eliminar
            
        Returns:
            bool: True si se eliminó correctamente, False si no existía
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_all(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado.
        
        Returns:
            List[StatusCode]: Lista de todos los códigos de estado
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def exists(self, entity_id: int) -> bool:
        """
        Verifica si existe un código de estado por ID.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            bool: True si existe, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass