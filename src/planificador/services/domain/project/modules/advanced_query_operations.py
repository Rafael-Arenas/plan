# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Consulta Avanzada para Proyectos

Implementa consultas complejas, agregaciones, análisis de datos
y operaciones de búsqueda sofisticadas para proyectos.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.schemas.project.project import (
    Project,
    ProjectWithAssignments,
    ProjectSearchFilter,
    ProjectWithDetails,
    ProjectAdvancedFilters,
    ProjectFullDetailsSchema,
    EmployeeWorkloadSchema,
    ProjectTimelineSchema
)
from planificador.schemas.common_schemas import (
    PaginationSchema,
    SortingSchema,
    DateRangeSchema
)
from planificador.repositories.project.project_repository_facade import ProjectRepositoryFacade
from planificador.exceptions.domain.project_domain_exceptions import (
    create_project_business_rule_error
)
from planificador.config.config import settings


class ProjectAdvancedQueryOperations:
    """
    Operaciones de consulta avanzada para proyectos.
    
    Maneja consultas complejas, análisis de datos, agregaciones
    y búsquedas sofisticadas con múltiples criterios.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de consulta avanzada.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="project_advanced_query_operations")

    async def get_projects_with_full_details(
        self, 
        include_assignments: bool = True,
        include_client_info: bool = True,
        filters: Optional[ProjectSearchFilter] = None,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[ProjectWithDetails], int]:
        """
        Obtiene proyectos con detalles completos incluyendo relaciones.
        
        Args:
            include_assignments: Incluir asignaciones
            include_client: Incluir información del cliente
            filters: Filtros opcionales
            
        Returns:
            List[ProjectWithAssignments]: Proyectos con detalles completos
        """
        self._logger.debug("Obteniendo proyectos con detalles completos")
        
        try:
            # Obtener proyectos con detalles completos
            projects = await self.repository.get_with_full_details()
            
            # Aplicar filtros si se proporcionan
            if filters:
                projects = await self._apply_advanced_filters(projects, filters)
            
            # Transformar a schemas con detalles completos
            result_schemas = []
            for project in projects:
                try:
                    schema = ProjectWithAssignments.model_validate(project)
                    result_schemas.append(schema)
                except Exception as validation_error:
                    self._logger.warning(
                        f"Error validando proyecto {project.id}: {validation_error}"
                    )
                    continue
            
            self._logger.debug(f"Proyectos con detalles completos: {len(result_schemas)} obtenidos")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error obteniendo proyectos con detalles completos: {e}")
            raise create_project_business_rule_error(
                message=f"Error obteniendo proyectos con detalles completos: {e}",
                operation="get_projects_with_full_details",
                original_error=e
            )

    async def search_projects_with_complex_criteria(
        self,
        criteria: ProjectAdvancedFilters
    ) -> Tuple[List[ProjectWithDetails], int]:
        """
        Búsqueda avanzada de proyectos con criterios complejos.
        
        Args:
            search_term: Término de búsqueda en nombre/descripción
            status_list: Lista de estados permitidos
            priority_list: Lista de prioridades permitidas
            client_ids: Lista de IDs de clientes
            date_range: Rango de fechas (inicio, fin)
            has_assignments: Filtrar por existencia de asignaciones
            is_overdue: Filtrar proyectos vencidos
            completion_percentage_range: Rango de porcentaje de completitud
            sort_by: Campo para ordenar
            sort_order: Orden (asc/desc)
            page: Número de página
            page_size: Tamaño de página
            
        Returns:
            Dict[str, Any]: Resultados paginados con metadatos
        """
        self._logger.debug("Ejecutando búsqueda avanzada de proyectos")
        
        try:
            # Construir filtros complejos
            filters = await self._build_complex_filters(
                search_term=search_term,
                status_list=status_list,
                priority_list=priority_list,
                client_ids=client_ids,
                date_range=date_range,
                has_assignments=has_assignments,
                is_overdue=is_overdue,
                completion_percentage_range=completion_percentage_range
            )
            
            # Ejecutar búsqueda base
            all_projects = await self.repository.search_projects(filters)
            
            # Aplicar filtros adicionales que no están en el repositorio
            filtered_projects = await self._apply_post_query_filters(
                all_projects,
                has_assignments=has_assignments,
                completion_percentage_range=completion_percentage_range
            )
            
            # Aplicar ordenamiento
            sorted_projects = await self._apply_advanced_sorting(
                filtered_projects, sort_by, sort_order
            )
            
            # Calcular metadatos de paginación
            total_count = len(sorted_projects)
            total_pages = (total_count + page_size - 1) // page_size
            
            # Aplicar paginación
            paginated_projects = await self._apply_pagination(
                sorted_projects, page, page_size
            )
            
            # Transformar a schemas
            result_schemas = [
                Project.model_validate(project) 
                for project in paginated_projects
            ]
            
            # Construir respuesta con metadatos
            result = {
                "projects": result_schemas,
                "pagination": {
                    "current_page": page,
                    "page_size": page_size,
                    "total_count": total_count,
                    "total_pages": total_pages,
                    "has_next": page < total_pages,
                    "has_previous": page > 1
                },
                "filters_applied": {
                    "search_term": search_term,
                    "status_count": len(status_list) if status_list else 0,
                    "priority_count": len(priority_list) if priority_list else 0,
                    "client_count": len(client_ids) if client_ids else 0,
                    "has_date_range": date_range is not None,
                    "has_assignments_filter": has_assignments is not None,
                    "is_overdue_filter": is_overdue is not None,
                    "has_completion_filter": completion_percentage_range is not None
                }
            }
            
            self._logger.debug(
                f"Búsqueda avanzada completada: {len(result_schemas)} proyectos "
                f"(página {page}/{total_pages})"
            )
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en búsqueda avanzada de proyectos: {e}")
            raise create_project_business_rule_error(
                message=f"Error en búsqueda avanzada de proyectos: {e}",
                operation="search_projects_with_complex_criteria",
                original_error=e
            )

    async def get_projects_dashboard_data(self) -> ProjectFullDetailsSchema:
        """
        Obtiene datos agregados para dashboard de proyectos.
        
        Returns:
            Dict[str, Any]: Datos del dashboard
        """
        self._logger.debug("Obteniendo datos del dashboard de proyectos")
        
        try:
            # Obtener todos los proyectos activos
            active_projects = await self.repository.get_by_status(ProjectStatus.ACTIVE)
            
            # Obtener proyectos vencidos
            overdue_projects = await self.repository.get_overdue_projects()
            
            # Obtener proyectos que terminan pronto (próximos 30 días)
            from pendulum import now
            upcoming_deadline = now().add(days=30).date()
            upcoming_projects = await self.repository.get_by_date_range(
                end_date=upcoming_deadline
            )
            upcoming_projects = [
                p for p in upcoming_projects 
                if p.status == ProjectStatus.ACTIVE and p.end_date
            ]
            
            # Calcular estadísticas por estado
            status_stats = await self._calculate_status_statistics()
            
            # Calcular estadísticas por prioridad
            priority_stats = await self._calculate_priority_statistics()
            
            # Calcular estadísticas por cliente
            client_stats = await self._calculate_client_statistics()
            
            # Calcular tendencias mensuales
            monthly_trends = await self._calculate_monthly_trends()
            
            dashboard_data = {
                "summary": {
                    "total_active": len(active_projects),
                    "total_overdue": len(overdue_projects),
                    "upcoming_deadlines": len(upcoming_projects),
                    "completion_rate": await self._calculate_overall_completion_rate()
                },
                "status_distribution": status_stats,
                "priority_distribution": priority_stats,
                "client_distribution": client_stats,
                "monthly_trends": monthly_trends,
                "recent_projects": await self._get_recent_projects(limit=10),
                "critical_alerts": await self._get_critical_alerts()
            }
            
            self._logger.debug("Datos del dashboard obtenidos exitosamente")
            return dashboard_data
            
        except Exception as e:
            self._logger.error(f"Error obteniendo datos del dashboard: {e}")
            raise create_project_business_rule_error(
                message=f"Error obteniendo datos del dashboard: {e}",
                operation="get_projects_dashboard_data",
                original_error=e
            )

    async def analyze_project_workload_distribution(self) -> EmployeeWorkloadSchema:
        """
        Analiza la distribución de carga de trabajo entre proyectos.
        
        Returns:
            Dict[str, Any]: Análisis de distribución de carga
        """
        self._logger.debug("Analizando distribución de carga de trabajo")
        
        try:
            # Obtener proyectos con asignaciones
            projects_with_assignments = await self.repository.get_with_assignments()
            
            # Calcular métricas de carga de trabajo
            workload_analysis = {
                "total_projects_with_assignments": 0,
                "total_assignments": 0,
                "average_assignments_per_project": 0,
                "projects_by_workload": {
                    "light": [],  # 1-2 asignaciones
                    "medium": [],  # 3-5 asignaciones
                    "heavy": [],  # 6+ asignaciones
                    "no_assignments": []
                },
                "workload_distribution": {},
                "capacity_utilization": {}
            }
            
            total_assignments = 0
            projects_with_work = 0
            
            for project in projects_with_assignments:
                assignment_count = len(project.assignments) if project.assignments else 0
                total_assignments += assignment_count
                
                if assignment_count == 0:
                    workload_analysis["projects_by_workload"]["no_assignments"].append({
                        "id": project.id,
                        "name": project.name,
                        "reference": project.reference
                    })
                elif assignment_count <= 2:
                    workload_analysis["projects_by_workload"]["light"].append({
                        "id": project.id,
                        "name": project.name,
                        "reference": project.reference,
                        "assignments": assignment_count
                    })
                    projects_with_work += 1
                elif assignment_count <= 5:
                    workload_analysis["projects_by_workload"]["medium"].append({
                        "id": project.id,
                        "name": project.name,
                        "reference": project.reference,
                        "assignments": assignment_count
                    })
                    projects_with_work += 1
                else:
                    workload_analysis["projects_by_workload"]["heavy"].append({
                        "id": project.id,
                        "name": project.name,
                        "reference": project.reference,
                        "assignments": assignment_count
                    })
                    projects_with_work += 1
            
            # Calcular promedios y distribuciones
            workload_analysis["total_projects_with_assignments"] = projects_with_work
            workload_analysis["total_assignments"] = total_assignments
            workload_analysis["average_assignments_per_project"] = (
                total_assignments / projects_with_work if projects_with_work > 0 else 0
            )
            
            # Calcular distribución porcentual
            total_projects = len(projects_with_assignments)
            if total_projects > 0:
                workload_analysis["workload_distribution"] = {
                    "light_percentage": len(workload_analysis["projects_by_workload"]["light"]) / total_projects * 100,
                    "medium_percentage": len(workload_analysis["projects_by_workload"]["medium"]) / total_projects * 100,
                    "heavy_percentage": len(workload_analysis["projects_by_workload"]["heavy"]) / total_projects * 100,
                    "no_assignments_percentage": len(workload_analysis["projects_by_workload"]["no_assignments"]) / total_projects * 100
                }
            
            self._logger.debug("Análisis de distribución de carga completado")
            return workload_analysis
            
        except Exception as e:
            self._logger.error(f"Error analizando distribución de carga: {e}")
            raise create_project_business_rule_error(
                message=f"Error analizando distribución de carga: {e}",
                operation="analyze_project_workload_distribution",
                original_error=e
            )

    async def get_projects_timeline_analysis(self) -> ProjectTimelineSchema:
        """
        Analiza la línea de tiempo de proyectos en un período específico.
        
        Args:
            start_date: Fecha de inicio del análisis
            end_date: Fecha de fin del análisis
            
        Returns:
            Dict[str, Any]: Análisis de línea de tiempo
        """
        self._logger.debug(f"Analizando línea de tiempo de proyectos: {start_date} - {end_date}")
        
        try:
            # Usar fechas por defecto si no se proporcionan
            if not start_date:
                from pendulum import now
                start_date = now().subtract(months=6).date()
            
            if not end_date:
                from pendulum import now
                end_date = now().add(months=6).date()
            
            # Obtener proyectos en el rango de fechas
            projects = await self.repository.get_by_date_range(start_date, end_date)
            
            # Analizar línea de tiempo
            timeline_analysis = {
                "period": {
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                    "total_days": (end_date - start_date).days
                },
                "projects_starting": [],
                "projects_ending": [],
                "projects_active_throughout": [],
                "monthly_breakdown": {},
                "overlapping_projects": [],
                "timeline_conflicts": []
            }
            
            # Clasificar proyectos por su relación con el período
            for project in projects:
                project_data = {
                    "id": project.id,
                    "name": project.name,
                    "reference": project.reference,
                    "start_date": project.start_date.isoformat() if project.start_date else None,
                    "end_date": project.end_date.isoformat() if project.end_date else None,
                    "status": project.status.value if project.status else None
                }
                
                # Proyectos que inician en el período
                if project.start_date and start_date <= project.start_date <= end_date:
                    timeline_analysis["projects_starting"].append(project_data)
                
                # Proyectos que terminan en el período
                if project.end_date and start_date <= project.end_date <= end_date:
                    timeline_analysis["projects_ending"].append(project_data)
                
                # Proyectos activos durante todo el período
                if (project.start_date and project.end_date and 
                    project.start_date <= start_date and project.end_date >= end_date):
                    timeline_analysis["projects_active_throughout"].append(project_data)
            
            # Calcular desglose mensual
            timeline_analysis["monthly_breakdown"] = await self._calculate_monthly_timeline_breakdown(
                projects, start_date, end_date
            )
            
            # Detectar proyectos superpuestos
            timeline_analysis["overlapping_projects"] = await self._detect_overlapping_projects(projects)
            
            # Detectar conflictos de línea de tiempo
            timeline_analysis["timeline_conflicts"] = await self._detect_timeline_conflicts(projects)
            
            self._logger.debug("Análisis de línea de tiempo completado")
            return timeline_analysis
            
        except Exception as e:
            self._logger.error(f"Error analizando línea de tiempo: {e}")
            raise create_project_business_rule_error(
                message=f"Error analizando línea de tiempo: {e}",
                operation="get_projects_timeline_analysis",
                details={"start_date": start_date, "end_date": end_date},
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================

    async def _build_complex_filters(self, **kwargs) -> Dict[str, Any]:
        """Construye filtros complejos para búsqueda avanzada."""
        filters = {}
        
        if kwargs.get("search_term"):
            filters["search_term"] = kwargs["search_term"]
        
        if kwargs.get("status_list"):
            filters["status_list"] = kwargs["status_list"]
        
        if kwargs.get("priority_list"):
            filters["priority_list"] = kwargs["priority_list"]
        
        if kwargs.get("client_ids"):
            filters["client_ids"] = kwargs["client_ids"]
        
        if kwargs.get("date_range"):
            start_date, end_date = kwargs["date_range"]
            if start_date:
                filters["start_date"] = start_date
            if end_date:
                filters["end_date"] = end_date
        
        if kwargs.get("is_overdue") is not None:
            filters["is_overdue"] = kwargs["is_overdue"]
        
        return filters

    async def _apply_advanced_filters(
        self, 
        projects: List[Project], 
        filters: ProjectSearchFilter
    ) -> List[Project]:
        """Aplica filtros avanzados a la lista de proyectos."""
        filtered_projects = projects
        
        # Aplicar filtros específicos del schema
        if filters.name:
            filtered_projects = [
                p for p in filtered_projects 
                if p.name and filters.name.lower() in p.name.lower()
            ]
        
        if filters.reference:
            filtered_projects = [
                p for p in filtered_projects 
                if p.reference and filters.reference.lower() in p.reference.lower()
            ]
        
        if filters.status:
            filtered_projects = [
                p for p in filtered_projects 
                if p.status == filters.status
            ]
        
        if filters.priority:
            filtered_projects = [
                p for p in filtered_projects 
                if p.priority == filters.priority
            ]
        
        if filters.client_id:
            filtered_projects = [
                p for p in filtered_projects 
                if p.client_id == filters.client_id
            ]
        
        return filtered_projects

    async def _apply_post_query_filters(
        self, 
        projects: List[Project], 
        **kwargs
    ) -> List[Project]:
        """Aplica filtros adicionales después de la consulta base."""
        filtered_projects = projects
        
        # Filtrar por existencia de asignaciones
        if kwargs.get("has_assignments") is not None:
            has_assignments = kwargs["has_assignments"]
            filtered_projects = [
                p for p in filtered_projects 
                if bool(p.assignments) == has_assignments
            ]
        
        # Filtrar por rango de porcentaje de completitud
        if kwargs.get("completion_percentage_range"):
            min_completion, max_completion = kwargs["completion_percentage_range"]
            filtered_projects = [
                p for p in filtered_projects 
                if min_completion <= (p.completion_percentage or 0) <= max_completion
            ]
        
        return filtered_projects

    async def _apply_advanced_sorting(
        self, 
        projects: List[Project], 
        sort_by: Optional[str], 
        sort_order: str
    ) -> List[Project]:
        """Aplica ordenamiento avanzado con múltiples criterios."""
        if not sort_by or not projects:
            return projects
        
        reverse = sort_order.lower() == "desc"
        
        try:
            if sort_by == "completion_percentage":
                return sorted(
                    projects, 
                    key=lambda p: p.completion_percentage or 0, 
                    reverse=reverse
                )
            elif sort_by == "assignment_count":
                return sorted(
                    projects, 
                    key=lambda p: len(p.assignments) if p.assignments else 0, 
                    reverse=reverse
                )
            elif sort_by == "days_until_deadline":
                from pendulum import now
                today = now().date()
                return sorted(
                    projects,
                    key=lambda p: (p.end_date - today).days if p.end_date else float('inf'),
                    reverse=reverse
                )
            else:
                # Usar ordenamiento básico para otros campos
                return await self._apply_basic_sorting(projects, sort_by, sort_order)
                
        except Exception as e:
            self._logger.warning(f"Error en ordenamiento avanzado: {e}")
            return projects

    async def _apply_basic_sorting(
        self, 
        projects: List[Project], 
        sort_by: str, 
        sort_order: str
    ) -> List[Project]:
        """Aplica ordenamiento básico."""
        reverse = sort_order.lower() == "desc"
        
        if sort_by == "name":
            return sorted(projects, key=lambda p: p.name or "", reverse=reverse)
        elif sort_by == "reference":
            return sorted(projects, key=lambda p: p.reference or "", reverse=reverse)
        elif sort_by == "start_date":
            return sorted(projects, key=lambda p: p.start_date or date.min, reverse=reverse)
        elif sort_by == "end_date":
            return sorted(projects, key=lambda p: p.end_date or date.max, reverse=reverse)
        else:
            return projects

    async def _apply_pagination(
        self, 
        projects: List[Project], 
        page: int, 
        page_size: int
    ) -> List[Project]:
        """Aplica paginación a la lista de proyectos."""
        if page < 1:
            page = 1
        
        if page_size < 1:
            page_size = 50
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        return projects[start_index:end_index]

    async def _calculate_status_statistics(self) -> Dict[str, int]:
        """Calcula estadísticas por estado."""
        try:
            stats = {}
            for status in ProjectStatus:
                projects = await self.repository.get_by_status(status)
                stats[status.value] = len(projects)
            return stats
        except Exception as e:
            self._logger.warning(f"Error calculando estadísticas de estado: {e}")
            return {}

    async def _calculate_priority_statistics(self) -> Dict[str, int]:
        """Calcula estadísticas por prioridad."""
        try:
            stats = {}
            for priority in ProjectPriority:
                projects = await self.repository.get_by_priority(priority)
                stats[priority.value] = len(projects)
            return stats
        except Exception as e:
            self._logger.warning(f"Error calculando estadísticas de prioridad: {e}")
            return {}

    async def _calculate_client_statistics(self) -> List[Dict[str, Any]]:
        """Calcula estadísticas por cliente."""
        try:
            # Obtener estadísticas del repositorio
            client_stats = await self.repository.get_client_project_stats()
            return client_stats
        except Exception as e:
            self._logger.warning(f"Error calculando estadísticas de cliente: {e}")
            return []

    async def _calculate_monthly_trends(self) -> Dict[str, Any]:
        """Calcula tendencias mensuales."""
        try:
            monthly_stats = await self.repository.get_monthly_project_stats()
            return monthly_stats
        except Exception as e:
            self._logger.warning(f"Error calculando tendencias mensuales: {e}")
            return {}

    async def _calculate_overall_completion_rate(self) -> float:
        """Calcula la tasa de completitud general."""
        try:
            # Obtener todos los proyectos activos
            active_projects = await self.repository.get_by_status(ProjectStatus.ACTIVE)
            
            if not active_projects:
                return 0.0
            
            total_completion = sum(
                p.completion_percentage or 0 for p in active_projects
            )
            
            return total_completion / len(active_projects)
            
        except Exception as e:
            self._logger.warning(f"Error calculando tasa de completitud: {e}")
            return 0.0

    async def _get_recent_projects(self, limit: int = 10) -> List[Dict[str, Any]]:
        """Obtiene proyectos recientes."""
        try:
            # Obtener proyectos ordenados por fecha de creación
            all_projects = await self.repository.search_projects({})
            
            # Ordenar por fecha de creación (asumiendo que existe created_at)
            recent_projects = sorted(
                all_projects,
                key=lambda p: getattr(p, 'created_at', date.min),
                reverse=True
            )[:limit]
            
            return [
                {
                    "id": p.id,
                    "name": p.name,
                    "reference": p.reference,
                    "status": p.status.value if p.status else None,
                    "start_date": p.start_date.isoformat() if p.start_date else None
                }
                for p in recent_projects
            ]
            
        except Exception as e:
            self._logger.warning(f"Error obteniendo proyectos recientes: {e}")
            return []

    async def _get_critical_alerts(self) -> List[Dict[str, Any]]:
        """Obtiene alertas críticas de proyectos."""
        try:
            alerts = []
            
            # Proyectos vencidos
            overdue_projects = await self.repository.get_overdue_projects()
            for project in overdue_projects:
                alerts.append({
                    "type": "overdue",
                    "severity": "high",
                    "project_id": project.id,
                    "project_name": project.name,
                    "message": f"Proyecto '{project.name}' está vencido",
                    "end_date": project.end_date.isoformat() if project.end_date else None
                })
            
            # Proyectos sin asignaciones
            all_projects = await self.repository.get_with_assignments()
            projects_without_assignments = [
                p for p in all_projects 
                if p.status == ProjectStatus.ACTIVE and not p.assignments
            ]
            
            for project in projects_without_assignments:
                alerts.append({
                    "type": "no_assignments",
                    "severity": "medium",
                    "project_id": project.id,
                    "project_name": project.name,
                    "message": f"Proyecto '{project.name}' no tiene asignaciones"
                })
            
            return alerts[:20]  # Limitar a 20 alertas
            
        except Exception as e:
            self._logger.warning(f"Error obteniendo alertas críticas: {e}")
            return []

    async def _calculate_monthly_timeline_breakdown(
        self, 
        projects: List[Project], 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Dict[str, int]]:
        """Calcula desglose mensual de la línea de tiempo."""
        try:
            from pendulum import parse
            
            monthly_breakdown = {}
            current_date = parse(start_date.isoformat()).start_of('month')
            end_period = parse(end_date.isoformat()).end_of('month')
            
            while current_date <= end_period:
                month_key = current_date.format('YYYY-MM')
                month_start = current_date.start_of('month').date()
                month_end = current_date.end_of('month').date()
                
                monthly_breakdown[month_key] = {
                    "starting": 0,
                    "ending": 0,
                    "active": 0
                }
                
                for project in projects:
                    # Proyectos que inician en el mes
                    if (project.start_date and 
                        month_start <= project.start_date <= month_end):
                        monthly_breakdown[month_key]["starting"] += 1
                    
                    # Proyectos que terminan en el mes
                    if (project.end_date and 
                        month_start <= project.end_date <= month_end):
                        monthly_breakdown[month_key]["ending"] += 1
                    
                    # Proyectos activos durante el mes
                    if (project.start_date and project.end_date and
                        project.start_date <= month_end and project.end_date >= month_start):
                        monthly_breakdown[month_key]["active"] += 1
                
                current_date = current_date.add(months=1)
            
            return monthly_breakdown
            
        except Exception as e:
            self._logger.warning(f"Error calculando desglose mensual: {e}")
            return {}

    async def _detect_overlapping_projects(self, projects: List[Project]) -> List[Dict[str, Any]]:
        """Detecta proyectos con fechas superpuestas."""
        try:
            overlapping = []
            
            for i, project1 in enumerate(projects):
                if not (project1.start_date and project1.end_date):
                    continue
                
                for project2 in projects[i+1:]:
                    if not (project2.start_date and project2.end_date):
                        continue
                    
                    # Verificar superposición
                    if (project1.start_date <= project2.end_date and 
                        project2.start_date <= project1.end_date):
                        
                        overlapping.append({
                            "project1": {
                                "id": project1.id,
                                "name": project1.name,
                                "start_date": project1.start_date.isoformat(),
                                "end_date": project1.end_date.isoformat()
                            },
                            "project2": {
                                "id": project2.id,
                                "name": project2.name,
                                "start_date": project2.start_date.isoformat(),
                                "end_date": project2.end_date.isoformat()
                            },
                            "overlap_days": min(project1.end_date, project2.end_date) - 
                                          max(project1.start_date, project2.start_date)
                        })
            
            return overlapping
            
        except Exception as e:
            self._logger.warning(f"Error detectando proyectos superpuestos: {e}")
            return []

    async def _detect_timeline_conflicts(self, projects: List[Project]) -> List[Dict[str, Any]]:
        """Detecta conflictos en la línea de tiempo."""
        try:
            conflicts = []
            
            for project in projects:
                project_conflicts = []
                
                # Verificar si la fecha de inicio es posterior a la de fin
                if (project.start_date and project.end_date and 
                    project.start_date > project.end_date):
                    project_conflicts.append("start_date_after_end_date")
                
                # Verificar si el proyecto está activo pero ya pasó su fecha de fin
                if (project.status == ProjectStatus.ACTIVE and project.end_date):
                    from pendulum import now
                    if project.end_date < now().date():
                        project_conflicts.append("active_but_past_end_date")
                
                # Verificar si el proyecto está completado pero no ha llegado a su fecha de fin
                if (project.status == ProjectStatus.COMPLETED and project.end_date):
                    from pendulum import now
                    if project.end_date > now().date():
                        project_conflicts.append("completed_before_end_date")
                
                if project_conflicts:
                    conflicts.append({
                        "project_id": project.id,
                        "project_name": project.name,
                        "conflicts": project_conflicts,
                        "start_date": project.start_date.isoformat() if project.start_date else None,
                        "end_date": project.end_date.isoformat() if project.end_date else None,
                        "status": project.status.value if project.status else None
                    })
            
            return conflicts
            
        except Exception as e:
            self._logger.warning(f"Error detectando conflictos de línea de tiempo: {e}")
            return []