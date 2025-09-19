# src/planificador/repositories/workload/modules/crud_module.py

"""
Módulo CRUD para operaciones básicas del repositorio Workload.

Este módulo implementa las operaciones CRUD (Create, Read, Update, Delete)
para la gestión de cargas de trabajo en la base de datos.

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD básicas
    - Dependency Inversion: Depende de abstracciones, no implementaciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    crud_module = WorkloadCrudModule(session)
    workload = await crud_module.create_workload(workload_data)
    updated = await crud_module.update_workload(workload_id, updates)
    await crud_module.delete_workload(workload_id)
    ```
"""

from typing import Optional, Dict, Any
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces.crud_interface import IWorkloadCrudOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    convert_sqlalchemy_error
)


class WorkloadCrudModule(BaseRepository[Workload], IWorkloadCrudOperations):
    """
    Módulo para operaciones CRUD del repositorio Workload.
    
    Implementa las operaciones básicas de creación, lectura, actualización
    y eliminación de registros de cargas de trabajo en la base de datos.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Workload
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD para cargas de trabajo.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Workload)
        self._logger = self._logger.bind(component="WorkloadCrudModule")
        self._logger.debug("WorkloadCrudModule inicializado")

    async def create_workload(self, workload_data: Dict[str, Any]) -> Workload:
        """
        Crea una nueva carga de trabajo en la base de datos.
        
        Args:
            workload_data: Diccionario con los datos de la carga de trabajo
        
        Returns:
            Workload: La carga de trabajo creada
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la creación
        """
        self._logger.debug(f"Creando nueva carga de trabajo: {workload_data}")
        
        try:
            workload = self.model_class(**workload_data)
            return await self.create(workload)
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al crear carga de trabajo: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_workload",
                entity_type=self.model_class.__name__,
                entity_data=workload_data
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al crear carga de trabajo: {e}")
            await self.session.rollback()
            raise WorkloadRepositoryError(
                message=f"Error inesperado al crear carga de trabajo: {e}",
                operation="create_workload",
                entity_type=self.model_class.__name__,
                entity_data=workload_data,
                original_error=e
            )

    async def update_workload(
        self, 
        workload_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[Workload]:
        """
        Actualiza una carga de trabajo existente.
        
        Args:
            workload_id: ID de la carga de trabajo a actualizar
            update_data: Diccionario con los datos a actualizar
        
        Returns:
            Optional[Workload]: La carga de trabajo actualizada o None si no existe
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la actualización
        """
        self._logger.debug(f"Actualizando carga de trabajo ID {workload_id}: {update_data}")
        
        try:
            return await self.update(workload_id, update_data)
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al actualizar carga de trabajo: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_workload",
                entity_type=self.model_class.__name__,
                entity_id=workload_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar carga de trabajo: {e}")
            await self.session.rollback()
            raise WorkloadRepositoryError(
                message=f"Error inesperado al actualizar carga de trabajo: {e}",
                operation="update_workload",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )

    async def delete_workload(self, workload_id: int) -> bool:
        """
        Elimina una carga de trabajo por su ID.
        
        Args:
            workload_id: ID de la carga de trabajo a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False si no existía
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la eliminación
        """
        self._logger.debug(f"Eliminando carga de trabajo con ID: {workload_id}")
        
        try:
            return await self.delete(workload_id)
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al eliminar carga de trabajo: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_workload",
                entity_type=self.model_class.__name__,
                entity_id=workload_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar carga de trabajo: {e}")
            await self.session.rollback()
            raise WorkloadRepositoryError(
                message=f"Error inesperado al eliminar carga de trabajo: {e}",
                operation="delete_workload",
                entity_type=self.model_class.__name__,
                entity_id=workload_id,
                original_error=e
            )

    async def get_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """
        Obtiene una carga de trabajo por su ID.
        
        Args:
            workload_id: ID de la carga de trabajo a buscar
        
        Returns:
            Optional[Workload]: La carga de trabajo encontrada o None
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo carga de trabajo con ID: {workload_id}")
        return await self.get_by_id(workload_id)

    async def get_by_unique_field(
        self, 
        field_name: str, 
        value: Any
    ) -> Optional[Workload]:
        """
        Obtiene una carga de trabajo por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
        
        Returns:
            Optional[Workload]: La carga de trabajo encontrada o None
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo carga de trabajo por {field_name}: {value}")
        return await self.get_by_field(field_name, value)

    # Métodos alias para compatibilidad con la interfaz
    async def add_workload(self, workload_data: Dict[str, Any]) -> Workload:
        """Alias para create_workload."""
        return await self.create_workload(workload_data)

    async def find_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """Alias para get_workload_by_id."""
        return await self.get_workload_by_id(workload_id)

    async def modify_workload(
        self, 
        workload_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[Workload]:
        """Alias para update_workload."""
        return await self.update_workload(workload_id, update_data)

    async def remove_workload(self, workload_id: int) -> bool:
        """Alias para delete_workload."""
        return await self.delete_workload(workload_id)