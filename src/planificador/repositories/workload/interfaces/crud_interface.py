# src/planificador/repositories/workload/interfaces/crud_interface.py

"""
Interfaz para operaciones CRUD del repositorio Workload.

Este módulo define la interfaz abstracta para las operaciones básicas
de creación, lectura, actualización y eliminación de cargas de trabajo.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para operaciones CRUD
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones CRUD básicas

Uso:
    ```python
    class WorkloadCrudModule(IWorkloadCrudOperations):
        async def create_workload(self, workload_data: Dict[str, Any]) -> Workload:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional

from planificador.models.workload import Workload
from planificador.exceptions.repository import WorkloadRepositoryError


class IWorkloadCrudOperations(ABC):
    """
    Interfaz abstracta para operaciones CRUD de cargas de trabajo.
    
    Define los métodos básicos que debe implementar cualquier módulo
    que maneje operaciones de creación, lectura, actualización y
    eliminación de cargas de trabajo.
    
    Métodos:
        create: Crea una nueva carga de trabajo
        create_workload: Alias para crear carga de trabajo
        get_workload_by_id: Obtiene una carga de trabajo por ID
        update: Actualiza una carga de trabajo existente
        update_workload: Alias para actualizar carga de trabajo
        delete: Elimina una carga de trabajo
        delete_workload: Alias para eliminar carga de trabajo
    """

    @abstractmethod
    async def create(self, workload_data: Dict[str, Any]) -> Workload:
        """
        Crea una nueva carga de trabajo con validación completa.
        
        Args:
            workload_data: Diccionario con los datos de la carga de trabajo
        
        Returns:
            Workload: La carga de trabajo creada
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la creación
        """
        pass

    @abstractmethod
    async def create_workload(self, workload_data: Dict[str, Any]) -> Workload:
        """
        Alias para crear carga de trabajo.
        
        Args:
            workload_data: Diccionario con los datos de la carga de trabajo
        
        Returns:
            Workload: La carga de trabajo creada
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la creación
        """
        pass

    @abstractmethod
    async def get_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """
        Obtiene una carga de trabajo por su ID con relaciones cargadas.
        
        Args:
            workload_id: ID de la carga de trabajo
        
        Returns:
            Optional[Workload]: La carga de trabajo encontrada o None si no existe
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        pass

    @abstractmethod
    async def update(self, workload_id: int, update_data: Dict[str, Any]) -> Workload:
        """
        Actualiza una carga de trabajo existente.
        
        Args:
            workload_id: ID de la carga de trabajo a actualizar
            update_data: Diccionario con los datos a actualizar
        
        Returns:
            Workload: La carga de trabajo actualizada
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la actualización
        """
        pass

    @abstractmethod
    async def update_workload(self, workload_id: int, update_data: Dict[str, Any]) -> Workload:
        """
        Alias para actualizar carga de trabajo.
        
        Args:
            workload_id: ID de la carga de trabajo a actualizar
            update_data: Diccionario con los datos a actualizar
        
        Returns:
            Workload: La carga de trabajo actualizada
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la actualización
        """
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """
        Elimina una carga de trabajo por ID.
        
        Args:
            entity_id: ID de la carga de trabajo a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la eliminación
        """
        pass

    @abstractmethod
    async def delete_workload(self, workload_id: int) -> bool:
        """
        Alias para eliminar carga de trabajo.
        
        Args:
            workload_id: ID de la carga de trabajo a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False en caso contrario
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la eliminación
        """
        pass