# src/planificador/repositories/status_code/modules/query_module.py

"""
Módulo de consultas para operaciones de búsqueda del repositorio StatusCode.

Este módulo implementa las operaciones de consulta, búsqueda y recuperación
de registros de códigos de estado desde la base de datos con filtros avanzados.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de consulta y búsqueda
    - Query Optimization: Consultas optimizadas para performance
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    query_module = StatusCodeQueryModule(session)
    status_code = await query_module.get_by_code("ACTIVE")
    status_codes = await query_module.search_by_name("activ")
    active_codes = await query_module.get_by_is_active(True)
    ```
"""

from typing import List, Optional, Dict, Any
from sqlalchemy import select, and_, or_, func
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.status_code import StatusCode
from planificador.repositories.status_code.interfaces.query_interface import IStatusCodeQueryOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    StatusCodeRepositoryError,
    convert_sqlalchemy_error
)


class StatusCodeQueryModule(BaseRepository[StatusCode], IStatusCodeQueryOperations):
    """
    Módulo para operaciones de consulta del repositorio StatusCode.
    
    Implementa las operaciones de consulta y recuperación de registros
    de códigos de estado desde la base de datos con soporte para filtros avanzados,
    búsquedas por criterios y optimización de consultas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo StatusCode
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas para StatusCode.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, StatusCode)

    async def get_by_code(self, code: str) -> Optional[StatusCode]:
        """
        Busca un código de estado por su código único.
        
        Args:
            code: Código único del status code
            
        Returns:
            Optional[StatusCode]: El código de estado encontrado o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando código de estado por código: {code}")
            
            stmt = select(StatusCode).where(StatusCode.code == code)
            result = await self.session.execute(stmt)
            status_code = result.scalar_one_or_none()
            
            if status_code:
                self._logger.debug(f"Código de estado encontrado: {status_code.name}")
            else:
                self._logger.debug(f"No se encontró código de estado con código: {code}")
                
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar por código: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_code",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por código: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al buscar por código: {e}",
                operation="get_by_code",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_name(self, name: str) -> Optional[StatusCode]:
        """
        Busca un código de estado por su nombre exacto.
        
        Args:
            name: Nombre exacto del status code
            
        Returns:
            Optional[StatusCode]: El código de estado encontrado o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando código de estado por nombre: {name}")
            
            stmt = select(StatusCode).where(StatusCode.name == name)
            result = await self.session.execute(stmt)
            status_code = result.scalar_one_or_none()
            
            if status_code:
                self._logger.debug(f"Código de estado encontrado: {status_code.code}")
            else:
                self._logger.debug(f"No se encontró código de estado con nombre: {name}")
                
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar por nombre: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_name",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por nombre: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al buscar por nombre: {e}",
                operation="get_by_name",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_by_name(self, name_pattern: str) -> List[StatusCode]:
        """
        Busca códigos de estado por patrón de nombre (búsqueda parcial).
        
        Args:
            name_pattern: Patrón de texto para buscar en el nombre
            
        Returns:
            List[StatusCode]: Lista de códigos de estado que coinciden
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando códigos de estado por patrón de nombre: {name_pattern}")
            
            stmt = select(StatusCode).where(
                StatusCode.name.ilike(f"%{name_pattern}%")
            )
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado con patrón: {name_pattern}")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar por patrón de nombre: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_name",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por patrón de nombre: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al buscar por patrón de nombre: {e}",
                operation="search_by_name",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_by_description(self, description_pattern: str) -> List[StatusCode]:
        """
        Busca códigos de estado por patrón en la descripción.
        
        Args:
            description_pattern: Patrón de texto para buscar en la descripción
            
        Returns:
            List[StatusCode]: Lista de códigos de estado que coinciden
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando códigos de estado por patrón de descripción: {description_pattern}")
            
            stmt = select(StatusCode).where(
                StatusCode.description.ilike(f"%{description_pattern}%")
            )
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado con patrón en descripción: {description_pattern}")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar por patrón de descripción: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_description",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por patrón de descripción: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al buscar por patrón de descripción: {e}",
                operation="search_by_description",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_is_active(self, is_active: bool) -> List[StatusCode]:
        """
        Obtiene códigos de estado filtrados por estado activo/inactivo.
        
        Args:
            is_active: True para activos, False para inactivos
            
        Returns:
            List[StatusCode]: Lista de códigos de estado filtrados
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo códigos de estado por is_active: {is_active}")
            
            stmt = select(StatusCode).where(StatusCode.is_active == is_active)
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado con is_active={is_active}")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al filtrar por is_active: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_is_active",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al filtrar por is_active: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al filtrar por is_active: {e}",
                operation="get_by_is_active",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_is_default(self, is_default: bool) -> List[StatusCode]:
        """
        Obtiene códigos de estado filtrados por estado por defecto.
        
        Args:
            is_default: True para por defecto, False para no por defecto
            
        Returns:
            List[StatusCode]: Lista de códigos de estado filtrados
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Obteniendo códigos de estado por is_default: {is_default}")
            
            stmt = select(StatusCode).where(StatusCode.is_default == is_default)
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado con is_default={is_default}")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al filtrar por is_default: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_is_default",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al filtrar por is_default: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al filtrar por is_default: {e}",
                operation="get_by_is_default",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_by_criteria(self, criteria: Dict[str, Any]) -> List[StatusCode]:
        """
        Busca códigos de estado usando múltiples criterios de filtrado.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
            
        Returns:
            List[StatusCode]: Lista de códigos de estado que coinciden
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug(f"Buscando códigos de estado por criterios: {criteria}")
            
            stmt = select(StatusCode)
            conditions = []
            
            # Filtros exactos
            if "code" in criteria:
                conditions.append(StatusCode.code == criteria["code"])
            if "name" in criteria:
                conditions.append(StatusCode.name == criteria["name"])
            if "is_active" in criteria:
                conditions.append(StatusCode.is_active == criteria["is_active"])
            if "is_default" in criteria:
                conditions.append(StatusCode.is_default == criteria["is_default"])
            if "display_order" in criteria:
                conditions.append(StatusCode.display_order == criteria["display_order"])
                
            # Filtros de texto parcial
            if "name_pattern" in criteria:
                conditions.append(StatusCode.name.ilike(f"%{criteria['name_pattern']}%"))
            if "description_pattern" in criteria:
                conditions.append(StatusCode.description.ilike(f"%{criteria['description_pattern']}%"))
            
            # Aplicar condiciones
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado con los criterios especificados")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_by_criteria",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar por criterios: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al buscar por criterios: {e}",
                operation="search_by_criteria",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_ordered_by_display_order(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado ordenados por display_order.
        
        Returns:
            List[StatusCode]: Lista ordenada de códigos de estado
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error durante la consulta
        """
        try:
            self._logger.debug("Obteniendo códigos de estado ordenados por display_order")
            
            stmt = select(StatusCode).order_by(StatusCode.display_order)
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Obtenidos {len(status_codes)} códigos de estado ordenados")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener ordenados por display_order: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_ordered_by_display_order",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener ordenados por display_order: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener ordenados por display_order: {e}",
                operation="get_ordered_by_display_order",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_sort_order(self, sort_order: int) -> Optional[StatusCode]:
        """
        Obtiene un código de estado por su orden de clasificación.
        
        Args:
            sort_order: Orden de clasificación del código de estado
            
        Returns:
            Optional[StatusCode]: El código de estado encontrado o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug(f"Buscando código de estado con sort_order: {sort_order}")
            
            stmt = select(StatusCode).where(StatusCode.sort_order == sort_order)
            result = await self.session.execute(stmt)
            status_code = result.scalar_one_or_none()
            
            if status_code:
                self._logger.debug(f"Código de estado encontrado: {status_code.code}")
            else:
                self._logger.debug(f"No se encontró código de estado con sort_order: {sort_order}")
                
            return status_code
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener código por sort_order: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_sort_order",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener código por sort_order: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener código por sort_order: {e}",
                operation="get_by_sort_order",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    # ==========================================
    # IMPLEMENTACIÓN DE MÉTODOS ABSTRACTOS DE INTERFAZ
    # ==========================================

    async def get_active_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado activos ordenados por sort_order.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado activos
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug("Obteniendo códigos de estado activos")
            
            stmt = select(StatusCode).where(
                StatusCode.is_active == True
            ).order_by(StatusCode.sort_order)
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado activos")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener códigos activos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_status_codes",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener códigos activos: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener códigos activos: {e}",
                operation="get_active_status_codes",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_billable_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado facturables y activos.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado facturables
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug("Obteniendo códigos de estado facturables")
            
            stmt = select(StatusCode).where(
                and_(
                    StatusCode.is_active == True,
                    StatusCode.is_billable == True
                )
            ).order_by(StatusCode.sort_order)
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado facturables")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener códigos facturables: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_billable_status_codes",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener códigos facturables: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener códigos facturables: {e}",
                operation="get_billable_status_codes",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_productive_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado productivos y activos.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado productivos
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug("Obteniendo códigos de estado productivos")
            
            stmt = select(StatusCode).where(
                and_(
                    StatusCode.is_active == True,
                    StatusCode.is_productive == True
                )
            ).order_by(StatusCode.sort_order)
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos de estado productivos")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener códigos productivos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_productive_status_codes",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener códigos productivos: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener códigos productivos: {e}",
                operation="get_productive_status_codes",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_status_codes_requiring_approval(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado que requieren aprobación y están activos.
        
        Returns:
            List[StatusCode]: Lista de códigos que requieren aprobación
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug("Obteniendo códigos de estado que requieren aprobación")
            
            stmt = select(StatusCode).where(
                and_(
                    StatusCode.is_active == True,
                    StatusCode.requires_approval == True
                )
            ).order_by(StatusCode.sort_order)
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos que requieren aprobación")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener códigos que requieren aprobación: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_status_codes_requiring_approval",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener códigos que requieren aprobación: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al obtener códigos que requieren aprobación: {e}",
                operation="get_status_codes_requiring_approval",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def filter_by_criteria(
        self,
        is_active: Optional[bool] = None,
        is_billable: Optional[bool] = None,
        is_productive: Optional[bool] = None,
        requires_approval: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> List[StatusCode]:
        """
        Filtra códigos de estado por múltiples criterios.
        
        Args:
            is_active: Filtrar por estado activo/inactivo
            is_billable: Filtrar por códigos facturables
            is_productive: Filtrar por códigos productivos
            requires_approval: Filtrar por códigos que requieren aprobación
            search_term: Término de búsqueda en nombre o descripción
            
        Returns:
            List[StatusCode]: Lista de códigos que cumplen los criterios
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            self._logger.debug(f"Filtrando códigos por criterios: active={is_active}, billable={is_billable}, productive={is_productive}, approval={requires_approval}, search='{search_term}'")
            
            # Construir condiciones dinámicamente
            conditions = []
            
            if is_active is not None:
                conditions.append(StatusCode.is_active == is_active)
            
            if is_billable is not None:
                conditions.append(StatusCode.is_billable == is_billable)
            
            if is_productive is not None:
                conditions.append(StatusCode.is_productive == is_productive)
            
            if requires_approval is not None:
                conditions.append(StatusCode.requires_approval == requires_approval)
            
            if search_term:
                search_pattern = f"%{search_term}%"
                conditions.append(
                    or_(
                        StatusCode.name.ilike(search_pattern),
                        StatusCode.description.ilike(search_pattern)
                    )
                )
            
            # Construir consulta
            stmt = select(StatusCode)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(StatusCode.sort_order)
            
            result = await self.session.execute(stmt)
            status_codes = list(result.scalars().all())
            
            self._logger.debug(f"Encontrados {len(status_codes)} códigos que cumplen los criterios")
            return status_codes
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al filtrar por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="filter_by_criteria",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al filtrar por criterios: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado al filtrar por criterios: {e}",
                operation="filter_by_criteria",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_unique_field(self, field_name: str, value: Any) -> Optional[StatusCode]:
        """
        Obtiene un código de estado por un campo único específico.
        
        Args:
            field_name: Nombre del campo único (code, name, etc.)
            value: Valor a buscar
            
        Returns:
            Optional[StatusCode]: El código de estado encontrado o None
            
        Raises:
            StatusCodeRepositoryError: Si ocurre un error en la base de datos
        """
        try:
            # Validar que el campo existe en el modelo
            if not hasattr(StatusCode, field_name):
                raise ValueError(f"Campo '{field_name}' no existe en StatusCode")
            
            field = getattr(StatusCode, field_name)
            result = await self.session.execute(
                select(StatusCode).where(field == value)
            )
            return result.scalar_one_or_none()
            
        except ValueError as e:
            self._logger.error(f"Campo inválido en get_by_unique_field: {e}")
            raise StatusCodeRepositoryError(
                message=f"Campo inválido: {e}",
                operation="get_by_unique_field",
                entity_type="StatusCode",
                original_error=e
            )
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo StatusCode por {field_name}={value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="StatusCode"
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en get_by_unique_field: {e}")
            raise StatusCodeRepositoryError(
                message=f"Error inesperado: {e}",
                operation="get_by_unique_field",
                entity_type="StatusCode",
                original_error=e
            )