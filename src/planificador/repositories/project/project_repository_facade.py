from typing import Any, Dict, List, Optional

from sqlalchemy.ext.asyncio import AsyncSession

from planificador.repositories.project.interfaces.project_repository_interface import (
    IProjectRepository,
)
from planificador.repositories.project.modules.crud_operations import (
    CrudOperations,
)
from planificador.repositories.project.modules.query_operations import QueryOperations
from planificador.repositories.project.modules.relationship_operations import (
    RelationshipOperations,
)
from planificador.repositories.project.modules.statistics_operations import (
    StatisticsOperations,
)
from planificador.repositories.project.modules.validation_operations import (
    ValidationOperations,
)
from planificador.models.project import Project


class ProjectRepositoryFacade(IProjectRepository):
    def __init__(self, session: AsyncSession):
        self.session = session
        self._query_operations = QueryOperations(session)
        self._validation_operations = ValidationOperations(session)
        self._relationship_operations = RelationshipOperations(self._query_operations)
        self._crud_operations = CrudOperations(
            session,
            self._validation_operations,
            self._query_operations,
            self._relationship_operations,
        )
        self._statistics_operations = StatisticsOperations(
            session, self._query_operations
        )

    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        return await self._crud_operations.create_project(project_data)

    async def get_project_by_id(self, project_id: int) -> Optional[Project]:
        query = self._query_operations._base_query().where(Project.id == project_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def update_project(
        self, project_id: int, updated_data: Dict[str, Any]
    ) -> Optional[Project]:
        return await self._crud_operations.update_project(project_id, updated_data)

    async def delete_project(self, project_id: int) -> bool:
        return await self._crud_operations.delete_project(project_id)

    async def get_all_projects(self) -> List[Project]:
        query = self._query_operations._base_query()
        result = await self.session.execute(query)
        return result.scalars().all()

    async def get_status_summary(self) -> Dict[str, int]:
        return await self._statistics_operations.get_status_summary()

    async def get_overdue_projects_summary(self) -> List[Dict[str, Any]]:
        return await self._statistics_operations.get_overdue_projects_summary()