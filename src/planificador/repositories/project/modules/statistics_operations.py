from collections import Counter
from typing import Any, Dict, List

import pendulum
from loguru import logger
from sqlalchemy import func, select

from planificador.repositories.base_repository import BaseRepository
from planificador.models.project import Project


class StatisticsOperations(BaseRepository):
    """
    Módulo para calcular estadísticas de proyectos.
    """

    def __init__(self, session, query_builder):
        self.session = session
        self.query_builder = query_builder
        self._logger = logger

    async def get_status_summary(self) -> Dict[str, int]:
        """
        Calcula un resumen del número de proyectos por estado.
        """
        query = select(Project.status, func.count(Project.id)).group_by(Project.status)
        result = await self.session.execute(query)
        return {status: count for status, count in result.all()}

    async def get_overdue_projects_summary(self) -> List[Dict[str, Any]]:
        """
        Obtiene un resumen de proyectos vencidos.
        """
        today = pendulum.now().start_of("day")
        query = (
            self.query_builder._base_query()
            .where(Project.end_date < today)
            .where(Project.status.notin_(["Completed", "Archived"]))
        )
        result = await self.session.execute(query)
        projects = result.scalars().all()
        return [
            {
                "id": p.id,
                "name": p.name,
                "end_date": p.end_date,
                "days_overdue": (today - p.end_date).in_days(),
            }
            for p in projects
        ]