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

    # ============================================================================
    # OPERACIONES CRUD - Delegación a _crud
    # ============================================================================
    async def create_project(self, project_data: Dict[str, Any]) -> Project:
        """Crea un nuevo proyecto después de validar los datos de entrada."""
        return await self._crud_operations.create_project(project_data)

    async def update_project(
        self, project_id: int, updated_data: Dict[str, Any]
    ) -> Optional[Project]:
        """Actualiza un proyecto existente después de validar los datos."""
        return await self._crud_operations.update_project(project_id, updated_data)

    async def delete_project(self, project_id: int) -> bool:
        """Elimina un proyecto por su ID."""
        return await self._crud_operations.delete_project(project_id)

    async def archive_project(self, project_id: int) -> Optional[Project]:
        """Archiva un proyecto después de validar que puede ser archivado."""
        return await self._crud_operations.archive_project(project_id)

    # ============================================================================
    # OPERACIONES DE CONSULTA - Delegación a _query_operations
    # ============================================================================
    def _base_query(self, include_archived: bool = False):
        """Crea una consulta base para proyectos, excluyendo los archivados por defecto."""
        return self._query_operations._base_query(include_archived)

    def with_client(self, query):
        """Añade la carga de la relación con el cliente."""
        return self._query_operations.with_client(query)

    def with_assignments(self, query):
        """Añade la carga de la relación con las asignaciones."""
        return self._query_operations.with_assignments(query)

    def with_full_details(self, query):
        """Añade la carga de todas las relaciones principales."""
        return self._query_operations.with_full_details(query)

    def filter_by_reference(self, query, reference: str):
        """Filtra por número de referencia."""
        return self._query_operations.filter_by_reference(query, reference)

    def filter_by_trigram(self, query, trigram: str):
        """Filtra por trigrama."""
        return self._query_operations.filter_by_trigram(query, trigram)

    def filter_by_name(self, query, name: str):
        """Filtra por nombre (búsqueda parcial)."""
        return self._query_operations.filter_by_name(query, name)

    def filter_by_client(self, query, client_id: int):
        """Filtra por ID de cliente."""
        return self._query_operations.filter_by_client(query, client_id)

    def filter_by_status(self, query, status: str):
        """Filtra por estado."""
        return self._query_operations.filter_by_status(query, status)

    def filter_by_priority(self, query, priority: str):
        """Filtra por prioridad."""
        return self._query_operations.filter_by_priority(query, priority)

    def filter_by_date_range(self, query, start_date, end_date):
        """Filtra por rango de fechas."""
        return self._query_operations.filter_by_date_range(query, start_date, end_date)

    # ============================================================================
    # OPERACIONES DE RELACIONES - Delegación a _relationship_operations
    # ============================================================================
    def with_client_relationship(self, query):
        """Añade la carga de la relación con el cliente usando relationship operations."""
        return self._relationship_operations.with_client(query)

    def with_assignments_relationship(self, query):
        """Añade la carga de la relación con las asignaciones usando relationship operations."""
        return self._relationship_operations.with_assignments(query)

    def with_full_details_relationship(self, query):
        """Añade la carga de todas las relaciones principales usando relationship operations."""
        return self._relationship_operations.with_full_details(query)

    # ============================================================================
    # OPERACIONES DE ESTADÍSTICAS - Delegación a _statistics_operations
    # ============================================================================
    async def get_status_summary(self) -> Dict[str, int]:
        """Calcula un resumen del número de proyectos por estado."""
        return await self._statistics_operations.get_status_summary()

    async def get_overdue_projects_summary(self) -> List[Dict[str, Any]]:
        """Obtiene un resumen de proyectos vencidos."""
        return await self._statistics_operations.get_overdue_projects_summary()

    # ============================================================================
    # OPERACIONES DE VALIDACIÓN - Delegación a _validation_operations
    # ============================================================================
    async def validate_project_creation(self, data: Dict[str, Any]) -> None:
        """Valida los datos para la creación de un nuevo proyecto."""
        return await self._validation_operations.validate_project_creation(data)

    async def validate_project_update(self, project_id: int, data: Dict[str, Any]) -> None:
        """Valida los datos para la actualización de un proyecto."""
        return await self._validation_operations.validate_project_update(project_id, data)

