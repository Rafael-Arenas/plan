# src/planificador/repositories/vacation/interfaces/crud_interface.py

"""
Interfaz para operaciones CRUD del repositorio Vacation.

Este módulo define la interfaz abstracta para las operaciones básicas
de creación, lectura, actualización y eliminación de vacaciones.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para operaciones CRUD
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones CRUD básicas

Uso:
    ```python
    class VacationCrudModule(IVacationCrudOperations):
        async def create_vacation(self, vacation_data: Dict[str, Any]) -> Vacation:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from planificador.models.vacation import Vacation
from planificador.exceptions.repository import VacationRepositoryError


class IVacationCrudOperations(ABC):
    """
    Interfaz abstracta para operaciones CRUD de vacaciones.
    
    Define los métodos básicos que debe implementar cualquier módulo
    que maneje operaciones de creación, lectura, actualización y
    eliminación de vacaciones.
    
    Métodos:
        create_vacation: Crea una nueva vacación
        get_vacation_by_id: Obtiene una vacación por ID
        update_vacation: Actualiza una vacación existente
        delete_vacation: Elimina una vacación
    """

    @abstractmethod
    async def create_vacation(self, vacation_data: Dict[str, Any]) -> Vacation:
        """
        Crea una nueva vacación con validación completa.
        
        Args:
            vacation_data: Diccionario con los datos de la vacación
        
        Returns:
            Vacation: La vacación creada
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la creación
        """
        pass

    @abstractmethod
    async def get_vacation_by_id(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene una vacación por su ID con relaciones cargadas.
        
        Args:
            vacation_id: ID de la vacación
        
        Returns:
            Optional[Vacation]: La vacación encontrada o None si no existe
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def update_vacation(self, vacation_id: int, update_data: Dict[str, Any]) -> Vacation:
        """
        Actualiza una vacación existente.
        
        Args:
            vacation_id: ID de la vacación a actualizar
            update_data: Diccionario con los datos a actualizar
        
        Returns:
            Vacation: La vacación actualizada
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la actualización
        """
        pass

    @abstractmethod
    async def delete_vacation(self, vacation_id: int) -> bool:
        """
        Elimina una vacación por ID.
        
        Args:
            vacation_id: ID de la vacación a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la eliminación
        """
        pass