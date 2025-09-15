from typing import Any, Dict, List, Optional
from datetime import date

from loguru import logger
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project
from planificador.exceptions.repository.base_repository_exceptions import RepositoryError, convert_sqlalchemy_error
from sqlalchemy.exc import SQLAlchemyError


class QueryOperations(BaseRepository[Project]):
    """
    Módulo para construir consultas de proyectos con SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(session, Project)
        self._logger = logger.bind(module="project_query_operations")
    
    async def get_by_unique_field(self, field_name: str, field_value: Any) -> Optional[Project]:
        """
        Obtiene un proyecto por un campo único específico.
        
        Args:
            field_name: Nombre del campo único
            field_value: Valor del campo único
            
        Returns:
            Optional[Project]: El proyecto encontrado o None
            
        Raises:
            RepositoryError: Si ocurre un error durante la consulta
        """
        try:
            if not hasattr(Project, field_name):
                raise ValueError(f"El campo '{field_name}' no existe en el modelo Project")
            
            field_attr = getattr(Project, field_name)
            query = select(Project).where(field_attr == field_value)
            result = await self.session.execute(query)
            return result.scalar_one_or_none()
            
        except SQLAlchemyError as e:
            self._logger.error(f"Error de base de datos al buscar proyecto por {field_name}={field_value}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value)
            )
        except Exception as e:
            self._logger.error(f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}")
            raise RepositoryError(
                message=f"Error inesperado al buscar proyecto por {field_name}={field_value}: {e}",
                operation="get_by_unique_field",
                entity_type="Project",
                entity_id=str(field_value),
                original_error=e
            )

    def _base_query(self, include_archived: bool = False):
        """
        Crea una consulta base para proyectos, excluyendo los archivados por defecto.
        """
        query = select(Project)
        if not include_archived:
            query = query.where(Project.is_archived == False)
        return query

    def with_client(self, query):
        """
        Añade la carga de la relación con el cliente.
        """
        return query.options(joinedload(Project.client))

    def with_assignments(self, query):
        """
        Añade la carga de la relación con las asignaciones.
        """
        return query.options(joinedload(Project.assignments))

    def with_full_details(self, query):
        """
        Añade la carga de todas las relaciones principales.
        """
        return query.options(
            joinedload(Project.client),
            joinedload(Project.assignments).joinedload(Assignment.employee),
        )

    def filter_by_reference(self, query, reference: str):
        """
        Filtra por número de referencia.
        """
        return query.where(Project.reference == reference)

    def filter_by_trigram(self, query, trigram: str):
        """
        Filtra por trigrama.
        """
        return query.where(Project.trigram == trigram)

    def filter_by_name(self, query, name: str):
        """
        Filtra por nombre (búsqueda parcial).
        """
        return query.where(Project.name.ilike(f"%{name}%"))

    def filter_by_client(self, query, client_id: int):
        """
        Filtra por ID de cliente.
        """
        return query.where(Project.client_id == client_id)

    def filter_by_status(self, query, status: str):
        """
        Filtra por estado.
        """
        return query.where(Project.status == status)

    def filter_by_priority(self, query, priority: str):
        """
        Filtra por prioridad.
        """
        return query.where(Project.priority == priority)

    def filter_by_date_range(self, query, start_date, end_date):
        """
        Filtra por rango de fechas.
        """
        return query.where(
            and_(Project.start_date >= start_date, Project.end_date <= end_date)
        )

    async def get_projects_by_status(
        self, status: str, limit: Optional[int] = None
    ) -> List[Project]:
        """
        Obtiene proyectos filtrados por estado.
        
        Args:
            status: Estado del proyecto a filtrar
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos con el estado especificado
        """
        try:
            query = self._base_query().where(Project.status == status)
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener proyectos por estado '{status}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_by_status",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al obtener proyectos por estado: {e}")
            raise RepositoryError(
                f"Error inesperado al obtener proyectos por estado: {str(e)}"
            ) from e

    async def get_projects_by_client(
        self, client_id: int, limit: Optional[int] = None
    ) -> List[Project]:
        """
        Obtiene proyectos filtrados por cliente.
        
        Args:
            client_id: ID del cliente
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos del cliente especificado
        """
        try:
            query = self._base_query().where(Project.client_id == client_id)
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener proyectos por cliente {client_id}: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_projects_by_client",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al obtener proyectos por cliente: {e}")
            raise RepositoryError(
                f"Error inesperado al obtener proyectos por cliente: {str(e)}"
            ) from e

    async def search_projects(
        self, search_term: str, limit: Optional[int] = None
    ) -> List[Project]:
        """
        Busca proyectos por término de búsqueda en nombre, referencia y descripción.
        
        Args:
            search_term: Término de búsqueda
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos que coinciden con la búsqueda
        """
        try:
            search_pattern = f"%{search_term}%"
            query = self._base_query().where(
                or_(
                    Project.name.ilike(search_pattern),
                    Project.reference.ilike(search_pattern),
                    Project.description.ilike(search_pattern)
                )
            )
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al buscar proyectos con término '{search_term}': {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_projects",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al buscar proyectos: {e}")
            raise RepositoryError(
                f"Error inesperado al buscar proyectos: {str(e)}"
            ) from e

    async def get_overdue_projects(self, limit: Optional[int] = None) -> List[Project]:
        """
        Obtiene proyectos que están vencidos (fecha de fin pasada).
        
        Args:
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos vencidos
        """
        try:
            from pendulum import now
            current_date = now().date()
            
            query = self._base_query().where(
                and_(
                    Project.end_date < current_date,
                    Project.status != "completed"
                )
            )
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener proyectos vencidos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_overdue_projects",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al obtener proyectos vencidos: {e}")
            raise RepositoryError(
                f"Error inesperado al obtener proyectos vencidos: {str(e)}"
            ) from e

    async def get_active_projects(self, limit: Optional[int] = None) -> List[Project]:
        """
        Obtiene proyectos activos (en progreso o pendientes).
        
        Args:
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos activos
        """
        try:
            query = self._base_query().where(
                Project.status.in_(["in_progress", "pending", "active"])
            )
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al obtener proyectos activos: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_active_projects",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al obtener proyectos activos: {e}")
            raise RepositoryError(
                f"Error inesperado al obtener proyectos activos: {str(e)}"
            ) from e

    async def filter_by_date_range(
        self, start_date: date, end_date: date, limit: Optional[int] = None
    ) -> List[Project]:
        """
        Filtra proyectos por rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            limit: Límite opcional de resultados
            
        Returns:
            List[Project]: Lista de proyectos en el rango de fechas
        """
        try:
            query = self.filter_by_dates(start_date, end_date)
            
            if limit is not None:
                query = query.limit(limit)
                
            result = await self.session.execute(query)
            return result.scalars().all()
            
        except SQLAlchemyError as e:
            logger.error(f"Error al filtrar por rango de fechas: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="filter_by_date_range",
                entity_type="Project",
            )
        except Exception as e:
            logger.error(f"Error inesperado al filtrar por rango de fechas: {e}")
            raise RepositoryError(
                f"Error inesperado al filtrar por rango de fechas: {str(e)}"
            ) from e