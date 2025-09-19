# src/planificador/repositories/workload/modules/query_module.py

"""
Módulo de consultas para operaciones de búsqueda del repositorio Workload.

Este módulo implementa las operaciones de consulta, búsqueda y recuperación
de registros de cargas de trabajo desde la base de datos con filtros avanzados.

Principios de Diseño:
    - Single Responsibility: Solo operaciones de consulta y búsqueda
    - Query Optimization: Uso de selectinload para relaciones
    - Error Handling: Manejo robusto de errores con logging estructurado

Uso:
    ```python
    query_module = WorkloadQueryModule(session)
    workload = await query_module.get_workload_by_id(workload_id)
    workloads = await query_module.search_workloads_by_criteria(criteria)
    employee_workloads = await query_module.get_workloads_by_employee(employee_id)
    ```
"""

from typing import List, Optional, Dict, Any
from datetime import date
from sqlalchemy import select, and_, or_, func
from sqlalchemy.orm import selectinload
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.exc import SQLAlchemyError

from planificador.models.workload import Workload
from planificador.repositories.workload.interfaces.query_interface import IWorkloadQueryOperations
from planificador.repositories.base_repository import BaseRepository
from planificador.exceptions.repository import (
    WorkloadRepositoryError,
    convert_sqlalchemy_error
)


class WorkloadQueryModule(BaseRepository[Workload], IWorkloadQueryOperations):
    """
    Módulo para operaciones de consulta del repositorio Workload.
    
    Implementa las operaciones de consulta y recuperación de registros
    de cargas de trabajo desde la base de datos con soporte para filtros avanzados,
    búsquedas por criterios y optimización de consultas.
    
    Attributes:
        session: Sesión de base de datos asíncrona
        model_class: Clase del modelo Workload
        _logger: Logger estructurado con contexto del módulo
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el módulo de consultas para cargas de trabajo.
        
        Args:
            session: Sesión de base de datos asíncrona
        """
        super().__init__(session, Workload)
        self._logger = self._logger.bind(component="WorkloadQueryModule")
        self._logger.debug("WorkloadQueryModule inicializado")

    async def get_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """
        Obtiene una carga de trabajo por su ID usando BaseRepository.
        
        Args:
            workload_id: ID de la carga de trabajo a buscar
        
        Returns:
            Optional[Workload]: La carga de trabajo encontrada o None
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo carga de trabajo con ID: {workload_id}")
        return await self.get_by_id(workload_id)

    async def get_workloads_by_employee(self, employee_id: int) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo de un empleado específico.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del empleado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo del empleado ID: {employee_id}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.employee_id == employee_id
            ).order_by(self.model_class.workload_date.desc())
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas de trabajo para empleado {employee_id}")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas por empleado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workloads_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas por empleado: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas por empleado: {e}",
                operation="get_workloads_by_employee",
                entity_type=self.model_class.__name__,
                entity_id=employee_id,
                original_error=e
            )

    async def get_workloads_by_project(self, project_id: int) -> List[Workload]:
        """
        Obtiene todas las cargas de trabajo de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
        
        Returns:
            List[Workload]: Lista de cargas de trabajo del proyecto
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo del proyecto ID: {project_id}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.project_id == project_id
            ).order_by(self.model_class.workload_date.desc())
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas de trabajo para proyecto {project_id}")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas por proyecto: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workloads_by_project",
                entity_type=self.model_class.__name__,
                entity_id=project_id
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas por proyecto: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas por proyecto: {e}",
                operation="get_workloads_by_project",
                entity_type=self.model_class.__name__,
                entity_id=project_id,
                original_error=e
            )

    async def get_workloads_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Workload]:
        """
        Obtiene cargas de trabajo en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
        
        Returns:
            List[Workload]: Lista de cargas de trabajo en el rango
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo entre {start_date} y {end_date}")
        
        try:
            stmt = select(self.model_class).where(
                and_(
                    self.model_class.workload_date >= start_date,
                    self.model_class.workload_date <= end_date
                )
            ).order_by(self.model_class.workload_date.asc())
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas de trabajo en el rango")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workloads_by_date_range",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas por rango de fechas: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas por rango de fechas: {e}",
                operation="get_workloads_by_date_range",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_workloads_by_status(self, status: str) -> List[Workload]:
        """
        Obtiene cargas de trabajo por estado específico.
        
        Args:
            status: Estado de las cargas de trabajo a buscar
        
        Returns:
            List[Workload]: Lista de cargas de trabajo con el estado especificado
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo con estado: {status}")
        
        try:
            stmt = select(self.model_class).where(
                self.model_class.status == status
            ).order_by(self.model_class.workload_date.desc())
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas de trabajo con estado {status}")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas por estado: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workloads_by_status",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas por estado: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas por estado: {e}",
                operation="get_workloads_by_status",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def search_workloads_by_criteria(
        self, 
        criteria: Dict[str, Any]
    ) -> List[Workload]:
        """
        Busca cargas de trabajo usando múltiples criterios de filtrado.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
                - employee_id: ID del empleado (opcional)
                - project_id: ID del proyecto (opcional)
                - start_date: Fecha de inicio (opcional)
                - end_date: Fecha de fin (opcional)
                - status: Estado de la carga (opcional)
                - min_hours: Horas mínimas (opcional)
                - max_hours: Horas máximas (opcional)
        
        Returns:
            List[Workload]: Lista de cargas de trabajo que cumplen los criterios
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la búsqueda
        """
        self._logger.debug(f"Buscando cargas de trabajo con criterios: {criteria}")
        
        try:
            stmt = select(self.model_class)
            conditions = []
            
            # Filtro por empleado
            if 'employee_id' in criteria and criteria['employee_id'] is not None:
                conditions.append(self.model_class.employee_id == criteria['employee_id'])
            
            # Filtro por proyecto
            if 'project_id' in criteria and criteria['project_id'] is not None:
                conditions.append(self.model_class.project_id == criteria['project_id'])
            
            # Filtro por rango de fechas
            if 'start_date' in criteria and criteria['start_date'] is not None:
                conditions.append(self.model_class.workload_date >= criteria['start_date'])
            
            if 'end_date' in criteria and criteria['end_date'] is not None:
                conditions.append(self.model_class.workload_date <= criteria['end_date'])
            
            # Filtro por estado
            if 'status' in criteria and criteria['status'] is not None:
                conditions.append(self.model_class.status == criteria['status'])
            
            # Filtro por horas mínimas
            if 'min_hours' in criteria and criteria['min_hours'] is not None:
                conditions.append(self.model_class.hours >= criteria['min_hours'])
            
            # Filtro por horas máximas
            if 'max_hours' in criteria and criteria['max_hours'] is not None:
                conditions.append(self.model_class.hours <= criteria['max_hours'])
            
            # Aplicar condiciones si existen
            if conditions:
                stmt = stmt.where(and_(*conditions))
            
            # Ordenar por fecha descendente
            stmt = stmt.order_by(self.model_class.workload_date.desc())
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Encontradas {len(workloads)} cargas de trabajo con los criterios especificados")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al buscar cargas por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_workloads_by_criteria",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar cargas por criterios: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al buscar cargas por criterios: {e}",
                operation="search_workloads_by_criteria",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def get_workloads_with_pagination(
        self, 
        limit: int = 10, 
        offset: int = 0,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Workload]:
        """
        Obtiene cargas de trabajo con paginación y filtros opcionales.
        
        Args:
            limit: Número máximo de registros a retornar
            offset: Número de registros a omitir
            filters: Filtros opcionales a aplicar
        
        Returns:
            List[Workload]: Lista paginada de cargas de trabajo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante la consulta
        """
        self._logger.debug(f"Obteniendo cargas de trabajo paginadas: limit={limit}, offset={offset}")
        
        try:
            stmt = select(self.model_class)
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'employee_id' in filters and filters['employee_id'] is not None:
                    conditions.append(self.model_class.employee_id == filters['employee_id'])
                
                if 'project_id' in filters and filters['project_id'] is not None:
                    conditions.append(self.model_class.project_id == filters['project_id'])
                
                if 'status' in filters and filters['status'] is not None:
                    conditions.append(self.model_class.status == filters['status'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            # Aplicar paginación y ordenamiento
            stmt = stmt.order_by(self.model_class.workload_date.desc()).limit(limit).offset(offset)
            
            result = await self.session.execute(stmt)
            workloads = result.scalars().all()
            
            self._logger.debug(f"Obtenidas {len(workloads)} cargas de trabajo paginadas")
            return list(workloads)
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al obtener cargas paginadas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_workloads_with_pagination",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al obtener cargas paginadas: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al obtener cargas paginadas: {e}",
                operation="get_workloads_with_pagination",
                entity_type=self.model_class.__name__,
                original_error=e
            )

    async def count_workloads(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número total de cargas de trabajo con filtros opcionales.
        
        Args:
            filters: Filtros opcionales a aplicar
        
        Returns:
            int: Número total de cargas de trabajo
        
        Raises:
            WorkloadRepositoryError: Si ocurre un error durante el conteo
        """
        self._logger.debug("Contando cargas de trabajo")
        
        try:
            stmt = select(func.count(self.model_class.id))
            
            # Aplicar filtros si se proporcionan
            if filters:
                conditions = []
                
                if 'employee_id' in filters and filters['employee_id'] is not None:
                    conditions.append(self.model_class.employee_id == filters['employee_id'])
                
                if 'project_id' in filters and filters['project_id'] is not None:
                    conditions.append(self.model_class.project_id == filters['project_id'])
                
                if 'status' in filters and filters['status'] is not None:
                    conditions.append(self.model_class.status == filters['status'])
                
                if conditions:
                    stmt = stmt.where(and_(*conditions))
            
            result = await self.session.execute(stmt)
            count = result.scalar()
            
            self._logger.debug(f"Total de cargas de trabajo: {count}")
            return count or 0
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error SQLAlchemy al contar cargas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="count_workloads",
                entity_type=self.model_class.__name__
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al contar cargas: {e}")
            raise WorkloadRepositoryError(
                message=f"Error inesperado al contar cargas: {e}",
                operation="count_workloads",
                entity_type=self.model_class.__name__,
                original_error=e
            )

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
    async def find_workload_by_id(self, workload_id: int) -> Optional[Workload]:
        """Alias para get_workload_by_id."""
        return await self.get_workload_by_id(workload_id)

    async def find_workloads_by_employee(self, employee_id: int) -> List[Workload]:
        """Alias para get_workloads_by_employee."""
        return await self.get_workloads_by_employee(employee_id)

    async def find_workloads_by_project(self, project_id: int) -> List[Workload]:
        """Alias para get_workloads_by_project."""
        return await self.get_workloads_by_project(project_id)

    async def find_workloads_by_date_range(
        self, 
        start_date: date, 
        end_date: date
    ) -> List[Workload]:
        """Alias para get_workloads_by_date_range."""
        return await self.get_workloads_by_date_range(start_date, end_date)

    async def find_workloads_by_status(self, status: str) -> List[Workload]:
        """Alias para get_workloads_by_status."""
        return await self.get_workloads_by_status(status)