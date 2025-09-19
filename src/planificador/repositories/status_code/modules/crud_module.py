# src/planificador/repositories/status_code/modules/crud_module.py

"""
Módulo CRUD para operaciones básicas del repositorio StatusCode.

Este módulo implementa las operaciones básicas de creación, lectura, actualización
y eliminación de registros de códigos de estado en la base de datos.

Principios de Diseño:
    - Single Responsibility: Solo operaciones CRUD básicas
    - Transaction Management: Manejo automático de transacciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    crud_module = StatusCodeCrudModule(session)
    status_code = await crud_module.create_status_code(status_code_data)
    status_code = await crud_module.get_status_code_by_id(status_code_id)
    updated = await crud_module.update_status_code(status_code_id, update_data)
    deleted = await crud_module.delete_status_code(status_code_id)
    ```
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.status_code import StatusCode
from planificador.repositories.status_code.interfaces.crud_interface import IStatusCodeCrudOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    StatusCodeRepositoryError,
    convert_sqlalchemy_error
)


class StatusCodeCrudModule(BaseRepository[StatusCode], IStatusCodeCrudOperations):
    """
    Módulo para operaciones CRUD del repositorio StatusCode.
    
    Implementa las operaciones básicas de creación, lectura, actualización
    y eliminación de registros de códigos de estado en la base de datos.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo StatusCode
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo CRUD para StatusCode.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, StatusCode)

    async def create_status_code(self, status_code_data: Dict[str, Any]) -> StatusCode:
        """
        Crea un nuevo código de estado en la base de datos.
        
        Args:
            status_code_data: Diccionario con los datos del código de estado
            
        Returns:
            StatusCode: El código de estado creado
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la creación
        """
        try:
            self._logger.info(f"Creando nuevo código de estado: {status_code_data.get('code', 'N/A')}")
            
            status_code = StatusCode(**status_code_data)
            self.session.add(status_code)
            await self.session.commit()
            await self.session.refresh(status_code)
            
            self._logger.info(f"Código de estado creado exitosamente con ID: {status_code.id}")
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al crear código de estado: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_status_code",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al crear código de estado: {e}")
            await self.session.rollback()
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al crear código de estado: {e}",
                operation="create_status_code",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_status_code_by_id(self, status_code_id: int) -> Optional[StatusCode]:
        """
        Obtiene un código de estado por su ID.
        
        Args:
            status_code_id: ID del código de estado
            
        Returns:
            Optional[StatusCode]: El código de estado encontrado o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando código de estado con ID: {status_code_id}")
            
            stmt = select(StatusCode).where(StatusCode.id == status_code_id)
            result = await self.session.execute(stmt)
            status_code = result.scalar_one_or_none()
            
            if status_code:
                self._logger.debug(f"Código de estado encontrado: {status_code.code}")
            else:
                self._logger.debug(f"No se encontró código de estado con ID: {status_code_id}")
                
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener código de estado por ID: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_status_code_by_id",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener código de estado por ID: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener código de estado por ID: {e}",
                operation="get_status_code_by_id",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id,
                original_error=e
            )

    async def get_all_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado.
        
        Returns:
            List[StatusCode]: Lista de todos los códigos de estado
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo todos los códigos de estado")
            
            stmt = select(StatusCode)
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener todos los códigos de estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_all_status_codes",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener todos los códigos de estado: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener todos los códigos de estado: {e}",
                operation="get_all_status_codes",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def update_status_code(
        self, 
        status_code_id: int, 
        update_data: Dict[str, Any]
    ) -> Optional[StatusCode]:
        """
        Actualiza un código de estado existente.
        
        Args:
            status_code_id: ID del código de estado a actualizar
            update_data: Diccionario con los datos a actualizar
            
        Returns:
            Optional[StatusCode]: El código de estado actualizado o None si no existe
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la actualización
        """
        try:
            self._logger.info(f"Actualizando código de estado con ID: {status_code_id}")
            
            status_code = await self.get_status_code_by_id(status_code_id)
            if not status_code:
                self._logger.warning(f"No se encontró código de estado con ID: {status_code_id}")
                return None
            
            # Actualizar campos
            for field, value in update_data.items():
                if hasattr(status_code, field):
                    setattr(status_code, field, value)
            
            await self.session.commit()
            await self.session.refresh(status_code)
            
            self._logger.info(f"Código de estado actualizado exitosamente: {status_code.code}")
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al actualizar código de estado: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="update_status_code",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al actualizar código de estado: {e}")
            await self.session.rollback()
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al actualizar código de estado: {e}",
                operation="update_status_code",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id,
                original_error=e
            )

    async def delete_status_code(self, status_code_id: int) -> bool:
        """
        Elimina un código de estado por su ID.
        
        Args:
            status_code_id: ID del código de estado a eliminar
            
        Returns:
            bool: True si se eliminó exitosamente, False si no existía
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la eliminación
        """
        try:
            self._logger.info(f"Eliminando código de estado con ID: {status_code_id}")
            
            status_code = await self.get_status_code_by_id(status_code_id)
            if not status_code:
                self._logger.warning(f"No se encontró código de estado con ID: {status_code_id}")
                return False
            
            await self.session.delete(status_code)
            await self.session.commit()
            
            self._logger.info(f"Código de estado eliminado exitosamente: {status_code.code}")
            return True
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al eliminar código de estado: {e}")
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="delete_status_code",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al eliminar código de estado: {e}")
            await self.session.rollback()
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al eliminar código de estado: {e}",
                operation="delete_status_code",
                entity_type=self.model_class.__name__,
                entity_id=status_code_id,
                original_error=e
            )