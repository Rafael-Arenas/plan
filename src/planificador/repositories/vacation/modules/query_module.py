# src/planificador/repositories/vacation/modules/query_module.py

"""
Módulo de consultas para operaciones de búsqueda del repositorio Vacation.

Este módulo implementa las operaciones de consulta, búsqueda y recuperación
de registros de vacaciones desde la base de datos con filtros avanzados.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de consulta y búsqueda
    - Query Optimization: Uso de selectinload para relaciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    query_module = VacationQueryModule(session)
    vacation = await query_module.get_vacation_by_id(vacation_id)
    vacations = await query_module.search_vacations_by_criteria(criteria)
    employee_vacations = await query_module.get_vacations_by_employee(employee_id)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.vacation import Vacation
from planificador.repositories.vacation.interfaces.query_interface import IVacationQueryOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    VacationRepositoryError,
    convert_sqlalchemy_error
)


class VacationQueryModule(BaseRepository[Vacation], IVacationQueryOperations):
    """
    Módulo para operaciones de consulta del repositorio Vacation.
    
    Implementa las operaciones de consulta y recuperación de registros
    de vacaciones desde la base de datos con soporte para filtros avanzados,
    búsquedas por criterios y optimización de consultas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Vacation
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas para vacaciones.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Vacation)
        self._logger = self._logger.bind(component="VacationQueryModule")
        self._logger.debug("VacationQueryModule inicializado")

    async def get_vacation_by_id(self, vacation_id: int) -> Optional[Vacation]:
        """
        Obtiene una vacación por su ID usando BaseRepository.
        
        Args:
            vacation_id: ID de la vacación a buscar
        
        Returns:
            Optional[Vacation]: La vacación encontrada o None
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacación con ID: {vacation_id}")
        return await self.get_by_id(vacation_id)

    async def get_vacations_by_employee(self, employee_id: int) -> List[Vacation]:
        """
        Obtiene todas las vacaciones de un empleado específico.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[Vacation]: Lista de vacaciones del empleado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacaciones del empleado ID: {employee_id}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.employee_id == employee_id
            ).order_by(self.model_class.start_date.desc())
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(vacations)} vacaciones para empleado ID: {employee_id}"
            )
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones por empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones por empleado: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo vacaciones por empleado: {e}",
                operation="get_vacations_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_vacations_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Vacation]:
        """
        Obtiene vacaciones en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Vacation]: Lista de vacaciones en el rango
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacaciones entre {start_date} y {end_date}")
        
        try:
            stmt = select(self.model_class).where(
                and_(
                    self.model_class.start_date <= end_date,
                    self.model_class.end_date >= start_date
                )
            ).order_by(self.model_class.start_date)
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(vacations)} vacaciones en el rango {start_date} - {end_date}"
            )
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_by_date_range",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones por rango: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo vacaciones por rango: {e}",
                operation="get_vacations_by_date_range",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_vacations_by_status(self, status: str) -> List[Vacation]:
        """
        Obtiene vacaciones por estado específico.
        
        Args:
            status: Estado de las vacaciones (PENDING, APPROVED, REJECTED, etc.)
        
        Returns:
            List[Vacation]: Lista de vacaciones con el estado especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacaciones con estado: {status}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.status == status
            ).order_by(self.model_class.created_at.desc())
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(vacations)} vacaciones con estado: {status}"
            )
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_by_status",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones por estado: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo vacaciones por estado: {e}",
                operation="get_vacations_by_status",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_vacations_by_type(self, vacation_type: str) -> List[Vacation]:
        """
        Obtiene vacaciones por tipo específico.
        
        Args:
            vacation_type: Tipo de vacación (ANNUAL, SICK, PERSONAL, etc.)
        
        Returns:
            List[Vacation]: Lista de vacaciones del tipo especificado
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacaciones de tipo: {vacation_type}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.vacation_type == vacation_type
            ).order_by(self.model_class.start_date.desc())
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(vacations)} vacaciones de tipo: {vacation_type}"
            )
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones por tipo: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_by_type",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones por tipo: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo vacaciones por tipo: {e}",
                operation="get_vacations_by_type",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_vacations_by_criteria(
        self, 
        criteria: Dict[str, Any]
    ) -> List[Vacation]:
        """
        Busca vacaciones usando múltiples criterios de filtrado.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
                - employee_id: ID del empleado (opcional)
                - status: Estado de la vacación (opcional)
                - vacation_type: Tipo de vacación (opcional)
                - start_date_from: Fecha mínima de inicio (opcional)
                - start_date_to: Fecha máxima de inicio (opcional)
                - end_date_from: Fecha mínima de fin (opcional)
                - end_date_to: Fecha máxima de fin (opcional)
        
        Returns:
            List[Vacation]: Lista de vacaciones que cumplen los criterios
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la búsqueda
        """
        self._logger.debug(f"Buscando vacaciones con criterios: {criteria}")
        
        try:
            conditions = []
            
            # Filtro por empleado
            if 'employee_id' in criteria and criteria['employee_id'] is not None:
                conditions.append(self.model_class.employee_id == criteria['employee_id'])
            
            # Filtro por estado
            if 'status' in criteria and criteria['status'] is not None:
                conditions.append(self.model_class.status == criteria['status'])
            
            # Filtro por tipo
            if 'vacation_type' in criteria and criteria['vacation_type'] is not None:
                conditions.append(self.model_class.vacation_type == criteria['vacation_type'])
            
            # Filtros de fecha de inicio
            if 'start_date_from' in criteria and criteria['start_date_from'] is not None:
                conditions.append(self.model_class.start_date >= criteria['start_date_from'])
            
            if 'start_date_to' in criteria and criteria['start_date_to'] is not None:
                conditions.append(self.model_class.start_date <= criteria['start_date_to'])
            
            # Filtros de fecha de fin
            if 'end_date_from' in criteria and criteria['end_date_from'] is not None:
                conditions.append(self.model_class.end_date >= criteria['end_date_from'])
            
            if 'end_date_to' in criteria and criteria['end_date_to'] is not None:
                conditions.append(self.model_class.end_date <= criteria['end_date_to'])
            
            # Construir consulta
            stmt = select(self.model_class)
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(self.model_class.start_date.desc())
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(
                f"Encontradas {len(vacations)} vacaciones con los criterios especificados"
            )
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando vacaciones por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_vacations_by_criteria",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado buscando vacaciones por criterios: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado buscando vacaciones por criterios: {e}",
                operation="search_vacations_by_criteria",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_vacations_with_pagination(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Vacation]:
        """
        Obtiene vacaciones con paginación y filtros opcionales.
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a omitir
            filters: Filtros opcionales a aplicar
        
        Returns:
            List[Vacation]: Lista paginada de vacaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacaciones paginadas: limit={limit}, offset={offset}")
        
        try:
            stmt = select(self.model_class)
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'employee_id' in filters and filters['employee_id'] is not None:
                    conditions.append(self.model_class.employee_id == filters['employee_id'])
                
                if 'status' in filters and filters['status'] is not None:
                    conditions.append(self.model_class.status == filters['status'])
                
                if 'vacation_type' in filters and filters['vacation_type'] is not None:
                    conditions.append(self.model_class.vacation_type == filters['vacation_type'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            stmt = stmt.order_by(self.model_class.start_date.desc()).limit(limit).offset(offset)
            
            result = await self.session.execute(stmt)
            vacations = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(vacations)} vacaciones paginadas")
            
            return list(vacations)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo vacaciones paginadas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_vacations_with_pagination",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado obteniendo vacaciones paginadas: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado obteniendo vacaciones paginadas: {e}",
                operation="get_vacations_with_pagination",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def count_vacations(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número total de vacaciones con filtros opcionales.
        
        Args:
            filters: Filtros opcionales a aplicar
        
        Returns:
            int: Número total de vacaciones
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante el conteo
        """
        self._logger.debug("Contando vacaciones")
        
        try:
            stmt = select(func.count(self.model_class.id))
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'employee_id' in filters and filters['employee_id'] is not None:
                    conditions.append(self.model_class.employee_id == filters['employee_id'])
                
                if 'status' in filters and filters['status'] is not None:
                    conditions.append(self.model_class.status == filters['status'])
                
                if 'vacation_type' in filters and filters['vacation_type'] is not None:
                    conditions.append(self.model_class.vacation_type == filters['vacation_type'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            self._logger.debug(f"Total de vacaciones: {count}")
            
            return count or 0
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error contando vacaciones: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_vacations",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado contando vacaciones: {e}")
            raise VacationRepositoryError(
                message=f"Error inesperado contando vacaciones: {e}",
                operation="count_vacations",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_by_unique_field(
        self, 
        field_name: str, 
        value: Any
    ) -> Optional[Vacation]:
        """
        Obtiene una vacación por un campo único delegando en el repositorio base.
        
        Args:
            field_name: Nombre del campo único
            value: Valor a buscar
        
        Returns:
            Optional[Vacation]: La vacación si existe, None en caso contrario
        
        Raises:
            VacationRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo vacación por {field_name}: {value}")
        
        return await self.get_by_field(field_name, value)