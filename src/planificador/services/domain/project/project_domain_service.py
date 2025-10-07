"""
Servicio de dominio para la gestión de proyectos.

Este módulo proporciona la lógica de negocio para operaciones relacionadas con proyectos,
incluyendo CRUD, consultas, validaciones, estadísticas y diagnósticos.
"""

from datetime import date
from typing import List, Optional, Dict, Any, Tuple
from uuid import UUID

from loguru import logger
from pendulum import DateTime

from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.schemas.project.project import (
    ProjectCreate,
    ProjectUpdate,
    Project,
    ProjectSearchFilter,
    ProjectWithDetails,
    ProjectDurationSchema,
    ProjectPerformanceStatsSchema,
    ProjectTimelineSchema,
    EmployeeWorkloadSchema,
    ProjectFullDetailsSchema,
    ValidationResultSchema,
    HealthReportSchema,
    ClientProjectsSummarySchema,
    ClientProjectStatsSchema,
    ProjectCloneSchema,
    ProjectWithAssignments,
    ProjectDatesUpdateSchema,
    ProjectAdvancedFilters
)
from planificador.schemas.common_schemas import (
    PaginationSchema,
    SortingSchema,
    DateRangeSchema
)

from .interfaces.project_domain_interface import IProjectDomainService
from .modules.crud_operations import ProjectCrudOperations
from .modules.query_operations import ProjectQueryOperations
from .modules.advanced_query_operations import ProjectAdvancedQueryOperations
from .modules.date_planning_operations import ProjectDatePlanningOperations
from .modules.relationship_operations import ProjectRelationshipOperations
from .modules.statistics_operations import ProjectStatisticsOperations
from .modules.validation_operations import ProjectValidationOperations
from .modules.diagnostic_operations import ProjectDiagnosticOperations


class ProjectDomainService(IProjectDomainService):
    """
    Servicio de dominio para la gestión de proyectos.
    
    Proporciona una interfaz unificada para todas las operaciones relacionadas
    con proyectos, delegando a módulos especializados.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """Inicializa el servicio de dominio de proyectos."""
        self._logger = logger.bind(service="ProjectDomainService")
        self._crud_ops = ProjectCrudOperations(repository_facade)
        self._query_ops = ProjectQueryOperations(repository_facade)
        self._advanced_query_ops = ProjectAdvancedQueryOperations(repository_facade)
        self._date_planning_ops = ProjectDatePlanningOperations(repository_facade)
        self._relationship_ops = ProjectRelationshipOperations(repository_facade)
        self._statistics_ops = ProjectStatisticsOperations(repository_facade)
        self._validation_ops = ProjectValidationOperations(repository_facade)
        self._diagnostic_ops = ProjectDiagnosticOperations(repository_facade)

    # ==================== OPERACIONES CRUD ====================

    async def create_project(self, project_data: ProjectCreate) -> Project:
        """Crea un nuevo proyecto."""
        self._logger.info(f"Creando proyecto: {project_data.name}")
        return await self._crud_ops.create_project(project_data)

    async def create_project_with_validation(
        self,
        project_data: Dict[str, Any],
        validate_business_rules: bool = True
    ) -> Project:
        """Crea un proyecto con validación completa."""
        self._logger.info("Creando proyecto con validación")
        return await self._crud_ops.create_project_with_validation(project_data, validate_business_rules)

    async def bulk_create_projects(self, projects_data: List[ProjectCreate]) -> List[Project]:
        """Crea múltiples proyectos en lote."""
        self._logger.info(f"Creando {len(projects_data)} proyectos en lote")
        return await self._crud_ops.bulk_create_projects(projects_data)

    async def get_project_by_id(self, project_id: UUID) -> Optional[Project]:
        """Obtiene un proyecto por su ID."""
        self._logger.info(f"Obteniendo proyecto por ID: {project_id}")
        return await self._crud_ops.get_project_by_id(project_id)

    async def update_project(
        self, 
        project_id: UUID, 
        project_data: ProjectUpdate
    ) -> Project:
        """Actualiza un proyecto existente."""
        self._logger.info(f"Actualizando proyecto: {project_id}")
        return await self._crud_ops.update_project(project_id, project_data)

    async def delete_project(self, project_id: UUID) -> bool:
        """Elimina un proyecto."""
        self._logger.info(f"Eliminando proyecto: {project_id}")
        return await self._crud_ops.delete_project(project_id)

    async def restore_project(self, project_id: UUID) -> bool:
        """Restaura un proyecto eliminado."""
        self._logger.info(f"Restaurando proyecto: {project_id}")
        return await self._crud_ops.restore_project(project_id)

    async def archive_project(self, project_id: UUID) -> Project:
        """Archiva un proyecto."""
        self._logger.info(f"Archivando proyecto: {project_id}")
        return await self._crud_ops.archive_project(project_id)

    async def duplicate_project(
        self, 
        project_id: UUID, 
        new_project_data: ProjectCloneSchema
    ) -> Project:
        """
        Duplica un proyecto existente con nuevos datos.
        
        Args:
            project_id: ID del proyecto a duplicar
            new_project_data: Datos para el nuevo proyecto duplicado
            
        Returns:
            Project: El proyecto duplicado
            
        Raises:
            ProjectNotFoundError: Si el proyecto original no existe
            ProjectCodeDuplicateError: Si la referencia ya existe
            ProjectTrigramDuplicateError: Si el trigrama ya existe
        """
        self._logger.info(f"Duplicando proyecto {project_id} con nombre: {new_project_data.name}")
        return await self._crud_ops.duplicate_project(project_id, new_project_data)

    # ==================== CONSULTAS BÁSICAS ====================

    async def search_projects(
        self,
        filters: Optional[ProjectSearchFilter] = None,
        pagination: Optional[PaginationSchema] = None,
        sorting: Optional[SortingSchema] = None
    ) -> Tuple[List[Project], int]:
        """Busca proyectos con filtros opcionales."""
        self._logger.info("Buscando proyectos")
        return await self._query_ops.search_projects(filters, pagination, sorting)

    async def get_projects_by_status(
        self,
        status: str,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos por estado."""
        self._logger.info(f"Obteniendo proyectos por estado: {status}")
        return await self._query_ops.get_projects_by_status(status, pagination)

    async def get_projects_by_client(
        self,
        client_id: UUID,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos por cliente."""
        self._logger.info(f"Obteniendo proyectos por cliente: {client_id}")
        return await self._query_ops.get_projects_by_client(client_id, pagination)

    async def get_projects_by_priority(
        self,
        priority: str,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos por prioridad."""
        self._logger.info(f"Obteniendo proyectos por prioridad: {priority}")
        return await self._query_ops.get_projects_by_priority(priority, pagination)

    async def get_active_projects(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos activos."""
        self._logger.info("Obteniendo proyectos activos")
        return await self._query_ops.get_active_projects(pagination)

    async def get_overdue_projects(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos vencidos."""
        self._logger.info("Obteniendo proyectos vencidos")
        return await self._query_ops.get_overdue_projects(pagination)

    async def get_projects_by_date_range(
        self,
        date_range: DateRangeSchema,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos en un rango de fechas."""
        self._logger.info("Obteniendo proyectos por rango de fechas")
        return await self._query_ops.get_projects_by_date_range(date_range, pagination)

    async def get_projects_ending_soon(
        self,
        days_ahead: int = 7,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos que terminan pronto."""
        self._logger.info(f"Obteniendo proyectos que terminan en {days_ahead} días")
        return await self._query_ops.get_projects_ending_soon(days_ahead, pagination)

    async def get_project_by_reference(self, reference: str) -> Optional[Project]:
        """Obtiene un proyecto por referencia."""
        self._logger.info(f"Obteniendo proyecto por referencia: {reference}")
        return await self._query_ops.get_project_by_reference(reference)

    async def get_project_by_trigram(self, trigram: str) -> Optional[Project]:
        """Obtiene un proyecto por trigrama."""
        self._logger.info(f"Obteniendo proyecto por trigrama: {trigram}")
        return await self._query_ops.get_project_by_trigram(trigram)

    async def get_projects_starting_current_week(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos que inician esta semana."""
        self._logger.info("Obteniendo proyectos que inician esta semana")
        return await self._query_ops.get_projects_starting_current_week(pagination)

    async def get_projects_ending_current_week(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos que terminan esta semana."""
        self._logger.info("Obteniendo proyectos que terminan esta semana")
        return await self._query_ops.get_projects_ending_current_week(pagination)

    async def get_projects_starting_current_month(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """Obtiene proyectos que inician este mes."""
        self._logger.info("Obteniendo proyectos que inician este mes")
        return await self._query_ops.get_projects_starting_current_month(pagination)

    # ==================== CONSULTAS AVANZADAS ====================

    async def get_projects_with_full_details(
        self,
        include_assignments: bool = True,
        include_client_info: bool = True,
        filters: Optional[ProjectSearchFilter] = None,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[ProjectWithDetails], int]:
        """Obtiene proyectos con detalles completos."""
        self._logger.info("Obteniendo proyectos con detalles completos")
        return await self._advanced_query_ops.get_projects_with_full_details(
            include_assignments, include_client_info, filters, pagination
        )

    async def search_projects_with_complex_criteria(
        self,
        criteria: ProjectAdvancedFilters
    ) -> Tuple[List[ProjectWithDetails], int]:
        """Busca proyectos con criterios complejos."""
        self._logger.info("Realizando búsqueda compleja de proyectos")
        return await self._advanced_query_ops.search_projects_with_complex_criteria(criteria)

    async def get_projects_dashboard_data(self) -> ProjectFullDetailsSchema:
        """Obtiene datos para el dashboard de proyectos."""
        self._logger.info("Obteniendo datos del dashboard de proyectos")
        return await self._advanced_query_ops.get_projects_dashboard_data()

    async def analyze_project_workload_distribution(self) -> EmployeeWorkloadSchema:
        """Analiza la distribución de carga de trabajo en proyectos."""
        self._logger.info("Analizando distribución de carga de trabajo")
        return await self._advanced_query_ops.analyze_project_workload_distribution()

    async def get_projects_timeline_analysis(self) -> ProjectTimelineSchema:
        """Obtiene análisis de cronograma de proyectos."""
        self._logger.info("Obteniendo análisis de cronograma")
        return await self._advanced_query_ops.get_projects_timeline_analysis()

    # ==================== PLANIFICACIÓN DE FECHAS ====================

    async def calculate_project_duration(
        self,
        start_date: DateTime,
        end_date: DateTime,
        include_weekends: bool = False
    ) -> ProjectDurationSchema:
        """Calcula la duración de un proyecto."""
        self._logger.info("Calculando duración del proyecto")
        return await self._date_planning_ops.calculate_project_duration(
            start_date, end_date, include_weekends
        )

    async def suggest_optimal_start_date(
        self,
        desired_end_date: DateTime,
        estimated_duration_days: int,
        avoid_weekends: bool = True,
        check_conflicts: bool = True
    ) -> ProjectDatesUpdateSchema:
        """Sugiere fecha de inicio óptima."""
        self._logger.info("Sugiriendo fecha de inicio óptima")
        return await self._date_planning_ops.suggest_optimal_start_date(
            desired_end_date, estimated_duration_days, avoid_weekends, check_conflicts
        )

    async def suggest_optimal_end_date(
        self,
        start_date: DateTime,
        estimated_duration_days: int,
        avoid_weekends: bool = True,
        check_conflicts: bool = True
    ) -> ProjectDatesUpdateSchema:
        """Sugiere fecha de fin óptima."""
        self._logger.info("Sugiriendo fecha de fin óptima")
        return await self._date_planning_ops.suggest_optimal_end_date(
            start_date, estimated_duration_days, avoid_weekends, check_conflicts
        )

    async def analyze_timeline_feasibility(
        self,
        start_date: DateTime,
        end_date: DateTime,
        check_resource_availability: bool = True,
        check_holidays: bool = True
    ) -> ValidationResultSchema:
        """Analiza la viabilidad del cronograma."""
        self._logger.info("Analizando viabilidad del cronograma")
        return await self._date_planning_ops.analyze_timeline_feasibility(
            start_date, end_date, check_resource_availability, check_holidays
        )

    async def get_optimal_project_schedule(
        self,
        project_ids: List[UUID],
        optimization_criteria: ProjectAdvancedFilters
    ) -> ProjectTimelineSchema:
        """Obtiene cronograma óptimo para proyectos."""
        self._logger.info("Obteniendo cronograma óptimo")
        return await self._date_planning_ops.get_optimal_project_schedule(
            project_ids, optimization_criteria
        )

    async def validate_project_dates(
        self,
        start_date: DateTime,
        end_date: DateTime,
        project_id: Optional[UUID] = None
    ) -> ValidationResultSchema:
        """Valida fechas del proyecto."""
        self._logger.info("Validando fechas del proyecto")
        return await self._date_planning_ops.validate_project_dates(
            start_date, end_date, project_id
        )

    # ==================== RELACIONES ====================

    async def get_project_with_client(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """Obtiene proyecto con información del cliente."""
        self._logger.info(f"Obteniendo proyecto con cliente: {project_id}")
        return await self._relationship_ops.get_project_with_client(project_id)

    async def get_project_with_assignments(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """Obtiene proyecto con asignaciones."""
        self._logger.info(f"Obteniendo proyecto con asignaciones: {project_id}")
        return await self._relationship_ops.get_project_with_assignments(project_id)

    async def get_project_with_full_details(self, project_id: UUID) -> Optional[ProjectWithDetails]:
        """Obtiene proyecto con detalles completos."""
        self._logger.info(f"Obteniendo proyecto con detalles completos: {project_id}")
        return await self._relationship_ops.get_project_with_full_details(project_id)

    async def get_projects_by_client_detailed(
        self,
        client_id: UUID,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[ProjectWithDetails], int]:
        """Obtiene proyectos detallados por cliente."""
        self._logger.info(f"Obteniendo proyectos detallados por cliente: {client_id}")
        return await self._relationship_ops.get_projects_by_client_detailed(client_id, pagination)

    async def get_client_project_summary(self, client_id: UUID) -> ClientProjectStatsSchema:
        """Obtiene resumen de proyectos del cliente."""
        self._logger.info(f"Obteniendo resumen de proyectos del cliente: {client_id}")
        return await self._relationship_ops.get_client_project_summary(client_id)

    async def analyze_client_project_relationships(self) -> ClientProjectsSummarySchema:
        """Analiza relaciones cliente-proyecto."""
        self._logger.info("Analizando relaciones cliente-proyecto")
        return await self._relationship_ops.analyze_client_project_relationships()

    async def get_project_assignments_summary(self, project_id: UUID) -> ProjectWithAssignments:
        """Obtiene resumen de asignaciones del proyecto."""
        self._logger.info(f"Obteniendo resumen de asignaciones: {project_id}")
        return await self._relationship_ops.get_project_assignments_summary(project_id)

    async def validate_client_relationship(
        self,
        project_id: UUID,
        client_id: UUID
    ) -> ValidationResultSchema:
        """Valida relación cliente-proyecto."""
        self._logger.info(f"Validando relación cliente-proyecto: {project_id} - {client_id}")
        return await self._relationship_ops.validate_client_relationship(project_id, client_id)

    async def get_related_projects(
        self,
        project_id: UUID,
        relationship_type: str = "client"
    ) -> List[Project]:
        """Obtiene proyectos relacionados."""
        self._logger.info(f"Obteniendo proyectos relacionados: {project_id}")
        return await self._relationship_ops.get_related_projects(project_id, relationship_type)

    async def analyze_project_dependencies(self, project_id: UUID) -> ValidationResultSchema:
        """Analiza dependencias del proyecto."""
        self._logger.info(f"Analizando dependencias del proyecto: {project_id}")
        return await self._relationship_ops.analyze_project_dependencies(project_id)

    # ==================== ESTADÍSTICAS ====================

    async def get_status_summary(self) -> Dict[str, int]:
        """Obtiene resumen de estados."""
        self._logger.info("Obteniendo resumen de estados")
        return await self._statistics_ops.get_status_summary()

    async def get_overdue_projects_summary(self) -> Dict[str, Any]:
        """Obtiene resumen de proyectos vencidos."""
        self._logger.info("Obteniendo resumen de proyectos vencidos")
        return await self._statistics_ops.get_overdue_projects_summary()

    async def get_project_performance_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de rendimiento."""
        self._logger.info("Obteniendo estadísticas de rendimiento")
        return await self._statistics_ops.get_project_performance_stats()

    async def get_projects_by_status_summary(self) -> Dict[str, List[Project]]:
        """Obtiene resumen de proyectos por estado."""
        self._logger.info("Obteniendo resumen de proyectos por estado")
        return await self._statistics_ops.get_projects_by_status_summary()

    async def get_project_workload_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de carga de trabajo."""
        self._logger.info("Obteniendo estadísticas de carga de trabajo")
        return await self._statistics_ops.get_project_workload_stats()

    async def get_project_duration_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de duración."""
        self._logger.info("Obteniendo estadísticas de duración")
        return await self._statistics_ops.get_project_duration_stats()

    async def get_monthly_project_stats(self, year: int, month: int) -> Dict[str, Any]:
        """Obtiene estadísticas mensuales."""
        self._logger.info(f"Obteniendo estadísticas mensuales: {year}-{month}")
        return await self._statistics_ops.get_monthly_project_stats(year, month)

    async def get_client_project_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas por cliente."""
        self._logger.info("Obteniendo estadísticas por cliente")
        return await self._statistics_ops.get_client_project_stats()

    async def get_overdue_projects_stats(self) -> Dict[str, Any]:
        """Obtiene estadísticas de proyectos vencidos."""
        self._logger.info("Obteniendo estadísticas de proyectos vencidos")
        return await self._statistics_ops.get_overdue_projects_stats()

    async def generate_dashboard_summary(self) -> Dict[str, Any]:
        """Genera resumen del dashboard."""
        self._logger.info("Generando resumen del dashboard")
        return await self._statistics_ops.generate_dashboard_summary()

    # ==================== VALIDACIONES ====================

    async def validate_project_creation(
        self,
        project_data: ProjectCreate
    ) -> ValidationResultSchema:
        """Valida creación de proyecto."""
        self._logger.info("Validando creación de proyecto")
        return await self._validation_ops.validate_project_creation(project_data)

    async def validate_project_update(
        self,
        project_id: UUID,
        project_data: ProjectUpdate
    ) -> ValidationResultSchema:
        """Valida actualización de proyecto."""
        self._logger.info(f"Validando actualización de proyecto: {project_id}")
        return await self._validation_ops.validate_project_update(project_id, project_data)

    async def validate_status_transition(
        self,
        project_id: UUID,
        new_status: str
    ) -> ValidationResultSchema:
        """Valida transición de estado."""
        self._logger.info(f"Validando transición de estado: {project_id} -> {new_status}")
        return await self._validation_ops.validate_status_transition(project_id, new_status)

    async def validate_project_dates_detailed(
        self,
        start_date: DateTime,
        end_date: DateTime,
        project_id: Optional[UUID] = None
    ) -> ValidationResultSchema:
        """Valida fechas del proyecto detalladamente."""
        self._logger.info("Validando fechas del proyecto detalladamente")
        return await self._validation_ops.validate_project_dates_detailed(
            start_date, end_date, project_id
        )

    async def validate_project_code(self, code: str, project_id: Optional[UUID] = None) -> ValidationResultSchema:
        """Valida código del proyecto."""
        self._logger.info(f"Validando código del proyecto: {code}")
        return await self._validation_ops.validate_project_code(code, project_id)

    async def validate_project_trigram(self, trigram: str, project_id: Optional[UUID] = None) -> ValidationResultSchema:
        """Valida trigrama del proyecto."""
        self._logger.info(f"Validando trigrama del proyecto: {trigram}")
        return await self._validation_ops.validate_project_trigram(trigram, project_id)

    async def validate_business_rules(
        self,
        project_data: ProjectCreate
    ) -> ValidationResultSchema:
        """Valida reglas de negocio."""
        self._logger.info("Validando reglas de negocio")
        return await self._validation_ops.validate_business_rules(project_data)

    async def validate_data_integrity(self, project_id: UUID) -> ValidationResultSchema:
        """Valida integridad de datos."""
        self._logger.info(f"Validando integridad de datos: {project_id}")
        return await self._validation_ops.validate_data_integrity(project_id)

    # ==================== DIAGNÓSTICOS ====================

    async def diagnose_project_health(self, project_id: UUID) -> ProjectDurationSchema:
        """Diagnostica salud del proyecto."""
        self._logger.info(f"Diagnosticando salud del proyecto: {project_id}")
        return await self._diagnostic_ops.diagnose_project_health(project_id)

    async def detect_project_anomalies(self, project_id: UUID) -> ValidationResultSchema:
        """Detecta anomalías en el proyecto."""
        self._logger.info(f"Detectando anomalías del proyecto: {project_id}")
        return await self._diagnostic_ops.detect_project_anomalies(project_id)

    async def analyze_project_performance(self, project_id: UUID) -> ProjectPerformanceStatsSchema:
        """Analiza rendimiento del proyecto."""
        self._logger.info(f"Analizando rendimiento del proyecto: {project_id}")
        return await self._diagnostic_ops.analyze_project_performance(project_id)

    async def generate_project_status_report(self, project_id: UUID) -> HealthReportSchema:
        """Genera reporte de estado del proyecto."""
        self._logger.info(f"Generando reporte de estado: {project_id}")
        return await self._diagnostic_ops.generate_project_status_report(project_id)

    async def diagnose_multiple_projects(self, project_ids: List[UUID]) -> HealthReportSchema:
        """Diagnostica múltiples proyectos."""
        self._logger.info(f"Diagnosticando {len(project_ids)} proyectos")
        return await self._diagnostic_ops.diagnose_multiple_projects(project_ids)

    async def get_diagnostic_summary(self) -> HealthReportSchema:
        """Obtiene resumen de diagnósticos."""
        self._logger.info("Obteniendo resumen de diagnósticos")
        return await self._diagnostic_ops.get_diagnostic_summary()