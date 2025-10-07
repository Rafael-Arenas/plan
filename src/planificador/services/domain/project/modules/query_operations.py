# -*- coding: utf-8 -*-
"""
Módulo de Operaciones de Consulta para Proyectos

Implementa las operaciones básicas de consulta y búsqueda de proyectos
con filtros estándar y transformación de resultados.
"""

from typing import Optional, List, Dict, Any, Tuple
from datetime import date
from uuid import UUID
from sqlalchemy.ext.asyncio import AsyncSession
from loguru import logger

from planificador.models.project import Project, ProjectStatus, ProjectPriority
from planificador.schemas.project.project import (
    Project,
    ProjectSearchFilter
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


class ProjectQueryOperations:
    """
    Operaciones de consulta básica para proyectos.
    
    Maneja las consultas estándar de proyectos con filtros básicos,
    transformación de resultados y optimización de consultas.
    """

    def __init__(self, repository_facade: ProjectRepositoryFacade):
        """
        Inicializa las operaciones de consulta.
        
        Args:
            repository_facade: Fachada del repositorio de proyectos
        """
        self.repository = repository_facade
        self._logger = logger.bind(module="project_query_operations")

    async def search_projects(
        self,
        filters: Optional[ProjectSearchFilter] = None,
        pagination: Optional[PaginationSchema] = None,
        sorting: Optional[SortingSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Busca proyectos con filtros básicos.
        
        Args:
            filters: Filtros de búsqueda
            
        Returns:
            List[Project]: Lista de proyectos encontrados
        """
        self._logger.debug(f"Iniciando búsqueda de proyectos con filtros: {filters}")
        
        try:
            # Construir filtros para el repositorio
            repository_filters = await self._build_search_filters(filters)
            
            # Ejecutar búsqueda en repositorio
            projects = await self.repository.search_projects(repository_filters)
            
            # Transformar resultados
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Búsqueda completada: {len(result_schemas)} proyectos encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error en búsqueda de proyectos: {e}")
            raise create_project_business_rule_error(
                message=f"Error en búsqueda de proyectos: {e}",
                operation="search_projects",
                original_error=e
            )

    async def get_projects_by_status(
        self,
        status: str,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos filtrados por estado.
        
        Args:
            status: Estado del proyecto
            
        Returns:
            List[Project]: Lista de proyectos
        """
        self._logger.debug(f"Obteniendo proyectos por estado: {status}")
        
        try:
            projects = await self.repository.get_by_status(status)
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos por estado {status}: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos por estado {status}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos por estado: {e}",
                operation="get_projects_by_status",
                details={"status": status},
                original_error=e
            )

    async def get_projects_by_client(
        self,
        client_id: UUID,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos de un cliente específico.
        
        Args:
            client_id: ID del cliente
            
        Returns:
            List[Project]: Lista de proyectos del cliente
        """
        self._logger.debug(f"Obteniendo proyectos del cliente: {client_id}")
        
        try:
            projects = await self.repository.get_by_client(client_id)
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos del cliente {client_id}: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos del cliente {client_id}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos del cliente: {e}",
                operation="get_projects_by_client",
                details={"client_id": client_id},
                original_error=e
            )

    async def get_projects_by_priority(
        self,
        priority: str,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos filtrados por prioridad.
        
        Args:
            priority: Prioridad del proyecto
            
        Returns:
            List[Project]: Lista de proyectos
        """
        self._logger.debug(f"Obteniendo proyectos por prioridad: {priority}")
        
        try:
            projects = await self.repository.get_by_priority(priority)
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos por prioridad {priority}: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos por prioridad {priority}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos por prioridad: {e}",
                operation="get_projects_by_priority",
                details={"priority": priority},
                original_error=e
            )

    async def get_active_projects(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene todos los proyectos activos.
        
        Returns:
            List[Project]: Lista de proyectos activos
        """
        self._logger.debug("Obteniendo proyectos activos")
        
        try:
            return await self.get_projects_by_status(ProjectStatus.ACTIVE)
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos activos: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos activos: {e}",
                operation="get_active_projects",
                original_error=e
            )

    async def get_overdue_projects(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos vencidos o atrasados.
        
        Returns:
            List[Project]: Lista de proyectos vencidos
        """
        self._logger.debug("Obteniendo proyectos vencidos")
        
        try:
            projects = await self.repository.get_overdue_projects()
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos vencidos: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos vencidos: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos vencidos: {e}",
                operation="get_overdue_projects",
                original_error=e
            )

    async def get_projects_by_date_range(
        self,
        date_range: DateRangeSchema,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            
        Returns:
            List[Project]: Proyectos en el rango
        """
        self._logger.debug(f"Obteniendo proyectos por rango de fechas: {start_date} - {end_date}")
        
        try:
            projects = await self.repository.get_by_date_range(start_date, end_date)
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos en rango de fechas: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos por rango de fechas: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos por rango de fechas: {e}",
                operation="get_projects_by_date_range",
                details={"start_date": start_date, "end_date": end_date},
                original_error=e
            )

    async def get_projects_ending_soon(
        self,
        days_ahead: int = 7,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos que terminan pronto.
        
        Args:
            days_ahead: Días hacia adelante para considerar
            
        Returns:
            List[Project]: Proyectos que terminan pronto
        """
        self._logger.debug(f"Obteniendo proyectos que terminan en {days_ahead} días")
        
        try:
            # Calcular fecha límite
            from pendulum import now
            limit_date = now().add(days=days_ahead).date()
            
            # Obtener proyectos activos que terminan antes de la fecha límite
            projects = await self.repository.get_by_date_range(end_date=limit_date)
            
            # Filtrar solo proyectos activos
            active_projects = [
                project for project in projects 
                if project.status == ProjectStatus.ACTIVE and project.end_date
            ]
            
            result_schemas = [
                Project.model_validate(project) 
                for project in active_projects
            ]
            
            self._logger.debug(f"Proyectos que terminan pronto: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos que terminan pronto: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos que terminan pronto: {e}",
                operation="get_projects_ending_soon",
                details={"days_ahead": days_ahead},
                original_error=e
            )

    async def get_project_by_reference(self, reference: str) -> Optional[Project]:
        """
        Obtiene un proyecto por su referencia.
        
        Args:
            reference: Referencia del proyecto
            
        Returns:
            Optional[Project]: Proyecto encontrado o None
        """
        self._logger.debug(f"Obteniendo proyecto por referencia: {reference}")
        
        try:
            project = await self.repository.get_by_reference(reference)
            
            if not project:
                self._logger.debug(f"Proyecto no encontrado con referencia: {reference}")
                return None
            
            result_schema = Project.model_validate(project)
            self._logger.debug(f"Proyecto encontrado por referencia {reference}: ID {project.id}")
            return result_schema
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyecto por referencia {reference}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyecto por referencia: {e}",
                operation="get_project_by_reference",
                details={"reference": reference},
                original_error=e
            )

    async def get_project_by_trigram(self, trigram: str) -> Optional[Project]:
        """
        Obtiene un proyecto por su trigrama.
        
        Args:
            trigram: Trigrama del proyecto
            
        Returns:
            Optional[Project]: Proyecto encontrado o None
        """
        self._logger.debug(f"Obteniendo proyecto por trigrama: {trigram}")
        
        try:
            project = await self.repository.get_by_trigram(trigram)
            
            if not project:
                self._logger.debug(f"Proyecto no encontrado con trigrama: {trigram}")
                return None
            
            result_schema = Project.model_validate(project)
            self._logger.debug(f"Proyecto encontrado por trigrama {trigram}: ID {project.id}")
            return result_schema
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyecto por trigrama {trigram}: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyecto por trigrama: {e}",
                operation="get_project_by_trigram",
                details={"trigram": trigram},
                original_error=e
            )

    async def get_projects_starting_current_week(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos que inician en la semana actual.
        
        Returns:
            List[Project]: Proyectos que inician esta semana
        """
        self._logger.debug("Obteniendo proyectos que inician esta semana")
        
        try:
            projects = await self.repository.get_projects_starting_current_week()
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos que inician esta semana: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos que inician esta semana: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos que inician esta semana: {e}",
                operation="get_projects_starting_current_week",
                original_error=e
            )

    async def get_projects_ending_current_week(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos que terminan en la semana actual.
        
        Returns:
            List[Project]: Proyectos que terminan esta semana
        """
        self._logger.debug("Obteniendo proyectos que terminan esta semana")
        
        try:
            projects = await self.repository.get_projects_ending_current_week()
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos que terminan esta semana: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos que terminan esta semana: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos que terminan esta semana: {e}",
                operation="get_projects_ending_current_week",
                original_error=e
            )

    async def get_projects_starting_current_month(
        self,
        pagination: Optional[PaginationSchema] = None
    ) -> Tuple[List[Project], int]:
        """
        Obtiene proyectos que inician en el mes actual.
        
        Returns:
            List[Project]: Proyectos que inician este mes
        """
        self._logger.debug("Obteniendo proyectos que inician este mes")
        
        try:
            projects = await self.repository.get_projects_starting_current_month()
            
            result_schemas = [
                Project.model_validate(project) 
                for project in projects
            ]
            
            self._logger.debug(f"Proyectos que inician este mes: {len(result_schemas)} encontrados")
            return result_schemas
            
        except Exception as e:
            self._logger.error(f"Error al obtener proyectos que inician este mes: {e}")
            raise create_project_business_rule_error(
                message=f"Error al obtener proyectos que inician este mes: {e}",
                operation="get_projects_starting_current_month",
                original_error=e
            )

    # ============================================================================
    # MÉTODOS PRIVADOS DE UTILIDAD
    # ============================================================================

    async def _build_search_filters(self, filters: ProjectSearchFilter) -> Dict[str, Any]:
        """
        Construye filtros para el repositorio basados en el schema de filtros.
        
        Args:
            filters: Filtros del schema
            
        Returns:
            Dict[str, Any]: Filtros para el repositorio
        """
        repository_filters = {}
        
        # Convertir filtros del schema a formato del repositorio
        if filters.name:
            repository_filters["name"] = filters.name
        
        if filters.reference:
            repository_filters["reference"] = filters.reference
        
        if filters.status:
            repository_filters["status"] = filters.status
        
        if filters.priority:
            repository_filters["priority"] = filters.priority
        
        if filters.client_id:
            repository_filters["client_id"] = filters.client_id
        
        if filters.start_date:
            repository_filters["start_date"] = filters.start_date
        
        if filters.end_date:
            repository_filters["end_date"] = filters.end_date
        
        if filters.search_term:
            repository_filters["search_term"] = filters.search_term
        
        return repository_filters

    async def _apply_sorting(
        self, 
        projects: List[Project], 
        sort_by: Optional[str] = None, 
        sort_order: str = "asc"
    ) -> List[Project]:
        """
        Aplica ordenamiento a la lista de proyectos.
        
        Args:
            projects: Lista de proyectos
            sort_by: Campo por el cual ordenar
            sort_order: Orden (asc/desc)
            
        Returns:
            List[Project]: Lista ordenada
        """
        if not sort_by or not projects:
            return projects
        
        reverse = sort_order.lower() == "desc"
        
        try:
            if sort_by == "name":
                return sorted(projects, key=lambda p: p.name or "", reverse=reverse)
            elif sort_by == "reference":
                return sorted(projects, key=lambda p: p.reference or "", reverse=reverse)
            elif sort_by == "start_date":
                return sorted(projects, key=lambda p: p.start_date or date.min, reverse=reverse)
            elif sort_by == "end_date":
                return sorted(projects, key=lambda p: p.end_date or date.max, reverse=reverse)
            elif sort_by == "status":
                return sorted(projects, key=lambda p: p.status.value if p.status else "", reverse=reverse)
            elif sort_by == "priority":
                return sorted(projects, key=lambda p: p.priority.value if p.priority else "", reverse=reverse)
            else:
                # Campo no reconocido, devolver sin ordenar
                return projects
                
        except Exception as e:
            self._logger.warning(f"Error al ordenar proyectos por {sort_by}: {e}")
            return projects

    async def _apply_pagination(
        self, 
        projects: List[Project], 
        page: int = 1, 
        page_size: int = 50
    ) -> List[Project]:
        """
        Aplica paginación a la lista de proyectos.
        
        Args:
            projects: Lista de proyectos
            page: Número de página (1-based)
            page_size: Tamaño de página
            
        Returns:
            List[Project]: Lista paginada
        """
        if page < 1:
            page = 1
        
        if page_size < 1:
            page_size = 50
        
        start_index = (page - 1) * page_size
        end_index = start_index + page_size
        
        return projects[start_index:end_index]