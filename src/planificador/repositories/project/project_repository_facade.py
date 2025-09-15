from typing import Any, Dict, List, Optional
from datetime import date

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
from planificador.models.project import Project, ProjectStatus, ProjectPriority


class ProjectRepositoryFacade(IProjectRepository):
    def __init__(
        self,
        session: AsyncSession,
        query_operations: Optional[QueryOperations] = None,
        validation_operations: Optional[ValidationOperations] = None,
        relationship_operations: Optional[RelationshipOperations] = None,
        crud_operations: Optional[CrudOperations] = None,
        statistics_operations: Optional[StatisticsOperations] = None,
    ):
        self.session = session
        
        # Permitir inyección de dependencias para testing
        if query_operations is not None:
            self._query_operations = query_operations
        else:
            self._query_operations = QueryOperations(session)
            
        if validation_operations is not None:
            self._validation_operations = validation_operations
        else:
            self._validation_operations = ValidationOperations(session)
            
        if relationship_operations is not None:
            self._relationship_operations = relationship_operations
        else:
            self._relationship_operations = RelationshipOperations(self._query_operations)
            
        if crud_operations is not None:
            self._crud_operations = crud_operations
        else:
            self._crud_operations = CrudOperations(
                session,
                self._validation_operations,
                self._query_operations,
                self._relationship_operations,
            )
            
        if statistics_operations is not None:
            self._statistics_operations = statistics_operations
        else:
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

    def filter_by_reference(self, query, reference: str):
        """Filtra por número de referencia."""
        return self._query_operations.filter_by_reference(query, reference)

    def filter_by_name(self, query, name: str):
        """Filtra por nombre (búsqueda parcial)."""
        return self._query_operations.filter_by_name(query, name)

    def filter_by_dates(self, start_date: date, end_date: date):
        """Filtra por rango de fechas."""
        return self._query_operations.filter_by_dates(start_date, end_date)

    async def get_projects_by_status(self, status: str, limit: Optional[int] = None) -> List[Project]:
        """Obtiene proyectos filtrados por estado."""
        return await self._query_operations.get_projects_by_status(status, limit)

    async def get_projects_by_client(self, client_id: int, limit: Optional[int] = None) -> List[Project]:
        """Obtiene proyectos filtrados por cliente."""
        return await self._query_operations.get_projects_by_client(client_id, limit)

    async def search_projects(self, search_term: str, limit: Optional[int] = None) -> List[Project]:
        """Busca proyectos por término de búsqueda en nombre, referencia y descripción."""
        return await self._query_operations.search_projects(search_term, limit)

    async def get_overdue_projects(self, limit: Optional[int] = None) -> List[Project]:
        """Obtiene proyectos que están vencidos."""
        return await self._query_operations.get_overdue_projects(limit)

    async def get_active_projects(self, limit: Optional[int] = None) -> List[Project]:
        """Obtiene proyectos activos."""
        return await self._query_operations.get_active_projects(limit)

    async def filter_by_date_range(self, start_date: date, end_date: date, limit: Optional[int] = None) -> List[Project]:
        """Filtra proyectos por rango de fechas."""
        return await self._query_operations.filter_by_date_range(start_date, end_date, limit)

    async def get_by_id(self, project_id: int) -> Optional[Project]:
        """Obtiene un proyecto por su ID."""
        return await self._query_operations.get_by_id(project_id)
    
    def format_project_dates(self, project: Project) -> Dict[str, Optional[str]]:
        """Formatea las fechas de un proyecto."""
        return self._query_operations.format_project_dates(project)
    
    async def get_by_reference(self, reference: str) -> Optional[Project]:
        """Obtiene un proyecto por su referencia."""
        return await self._query_operations.get_by_reference(reference)
    
    async def get_by_trigram(self, trigram: str) -> Optional[Project]:
        """Obtiene un proyecto por su trigrama."""
        return await self._query_operations.get_by_trigram(trigram)
    
    async def search_by_name(self, search_term: str) -> List[Project]:
        """Busca proyectos por nombre."""
        return await self._query_operations.search_by_name(search_term)
    
    async def get_by_client(self, client_id: int) -> List[Project]:
        """Obtiene proyectos por cliente."""
        return await self._query_operations.get_by_client(client_id)
    
    async def get_by_status(self, status: ProjectStatus) -> List[Project]:
        """Obtiene proyectos por estado."""
        return await self._query_operations.get_by_status(status)
    
    async def get_active_projects(self) -> List[Project]:
        """Obtiene todos los proyectos activos."""
        return await self._query_operations.get_active_projects()
    
    async def get_by_priority(self, priority: ProjectPriority) -> List[Project]:
        """Obtiene proyectos por prioridad."""
        return await self._query_operations.get_by_priority(priority)
    
    async def get_by_date_range(
        self, start_date: Optional[date] = None, end_date: Optional[date] = None
    ) -> List[Project]:
        """Obtiene proyectos en un rango de fechas."""
        return await self._query_operations.get_by_date_range(start_date, end_date)
    
    async def get_overdue_projects(
        self, reference_date: Optional[date] = None
    ) -> List[Project]:
        """Obtiene proyectos atrasados."""
        return await self._query_operations.get_overdue_projects(reference_date)
    
    async def get_projects_starting_current_week(self, **kwargs) -> List[Project]:
        """Obtiene proyectos que inician en la semana actual."""
        return await self._query_operations.get_projects_starting_current_week(**kwargs)
    
    async def get_projects_ending_current_week(self, **kwargs) -> List[Project]:
        """Obtiene proyectos que terminan en la semana actual."""
        return await self._query_operations.get_projects_ending_current_week(**kwargs)
    
    async def get_projects_starting_current_month(self, **kwargs) -> List[Project]:
        """Obtiene proyectos que inician en el mes actual."""
        return await self._query_operations.get_projects_starting_current_month(**kwargs)
    
    async def get_projects_starting_business_days_only(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
        **kwargs,
    ) -> List[Project]:
        """Obtiene proyectos que inician en días hábiles."""
        return await self._query_operations.get_projects_starting_business_days_only(
            start_date, end_date, **kwargs
        )
    
    async def get_with_client(self, project_id: int) -> Optional[Project]:
        """Obtiene un proyecto con su cliente."""
        return await self._query_operations.get_with_client(project_id)
    
    async def get_with_assignments(self, project_id: int) -> Optional[Project]:
        """Obtiene un proyecto con sus asignaciones."""
        return await self._query_operations.get_with_assignments(project_id)
    
    async def get_with_full_details(self, project_id: int) -> Optional[Project]:
        """Obtiene un proyecto con todos sus detalles."""
        return await self._query_operations.get_with_full_details(project_id)
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

    async def get_project_performance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento de proyectos."""
        return await self._statistics_operations.get_project_performance_stats()

    async def get_projects_by_status_summary(self, status: str) -> Dict[str, Any]:
        """Obtiene un resumen de proyectos por estado específico."""
        return await self._statistics_operations.get_projects_by_status_summary(status)

    async def get_project_workload_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de proyectos."""
        return await self._statistics_operations.get_project_workload_stats()

    async def get_project_duration_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de duración de proyectos."""
        return await self._statistics_operations.get_project_duration_stats()

    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Obtiene estadísticas de proyectos por mes."""
        return await self._statistics_operations.get_monthly_project_stats(year, month)

    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de proyectos por cliente."""
        return await self._statistics_operations.get_client_project_stats(client_id)

    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas detalladas de proyectos vencidos."""
        return await self._statistics_operations.get_overdue_projects_stats()

    async def get_project_performance_stats(self, project_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento de un proyecto."""
        return await self._statistics_operations.get_project_performance_stats(project_id)
    
    async def get_projects_by_status_summary(self) -> Dict[str, int]:
        """Obtiene un resumen de proyectos por estado."""
        return await self._statistics_operations.get_projects_by_status_summary()
    
    async def get_project_workload_stats(
        self,
        project_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None,
    ) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo de un proyecto."""
        return await self._statistics_operations.get_project_workload_stats(
            project_id, start_date, end_date
        )
    
    async def get_project_duration_stats(self, project_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de duración de un proyecto."""
        return await self._statistics_operations.get_project_duration_stats(project_id)
    
    async def get_monthly_project_stats(
        self, year: int, month: int
    ) -> Dict[str, Any]:
        """Obtiene estadísticas mensuales de proyectos."""
        return await self._statistics_operations.get_monthly_project_stats(year, month)
    
    async def get_client_project_stats(self, client_id: int) -> Dict[str, Any]:
        """Obtiene estadísticas de proyectos de un cliente."""
        return await self._statistics_operations.get_client_project_stats(client_id)
    
    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de proyectos atrasados."""
        return await self._statistics_operations.get_overdue_projects_stats()

    # ============================================================================
    # OPERACIONES DE VALIDACIÓN - Delegación a _validation_operations
    # ============================================================================
    async def validate_project_creation(self, data: Dict[str, Any]) -> None:
        """Valida los datos para la creación de un nuevo proyecto."""
        return await self._validation_operations.validate_project_creation(data)

    async def validate_project_update(self, project_id: int, data: Dict[str, Any]) -> None:
        """Valida los datos para la actualización de un proyecto."""
        return await self._validation_operations.validate_project_update(project_id, data)

    async def reference_exists(self, reference: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si una referencia de proyecto existe."""
        return await self._validation_operations.reference_exists(reference, exclude_id)

    async def trigram_exists(self, trigram: str, exclude_id: Optional[int] = None) -> bool:
        """Verifica si un trigrama de proyecto existe."""
        return await self._validation_operations.trigram_exists(trigram, exclude_id)

    async def reference_exists(
        self, reference: str, exclude_id: Optional[int] = None
    ) -> bool:
        """Verifica si una referencia de proyecto existe."""
        return await self._validation_operations.reference_exists(reference, exclude_id)
    
    async def trigram_exists(
        self, trigram: str, exclude_id: Optional[int] = None
    ) -> bool:
        """Verifica si un trigrama de proyecto existe."""
        return await self._validation_operations.trigram_exists(trigram, exclude_id)

