from typing import Any, Dict, List, Optional

from loguru import logger
from sqlalchemy import and_, or_, select
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import contains_eager, joinedload

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project


class QueryOperations(BaseRepository):
    """
    Módulo para construir consultas de proyectos con SQLAlchemy.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger

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