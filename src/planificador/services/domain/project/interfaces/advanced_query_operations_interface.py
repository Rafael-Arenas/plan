"""
Interfaz para las operaciones avanzadas de consulta de proyectos.

Esta interfaz define el contrato para consultas complejas, agregaciones,
análisis de datos y búsquedas sofisticadas de proyectos.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Tuple
from datetime import date

from planificador.models.project import Project
from planificador.schemas.project.project import (
    ProjectWithAssignments,
    ProjectAdvancedFilters,
    EmployeeWorkloadSchema,
    ProjectTimelineSchema
)


class IProjectAdvancedQueryOperations(ABC):
    """
    Interfaz abstracta para las operaciones avanzadas de consulta de proyectos.
    
    Define el contrato para consultas complejas, agregaciones, análisis de datos
    y búsquedas sofisticadas que requieren procesamiento avanzado.
    """

    # ==========================================
    # CONSULTAS COMPLEJAS CON RELACIONES
    # ==========================================

    @abstractmethod
    async def get_projects_with_full_details(
        self,
        include_assignments: bool = True,
        include_client_info: bool = True,
        include_statistics: bool = False
    ) -> List[ProjectWithAssignments]:
        """
        Obtiene proyectos con información completa y relaciones.
        
        Args:
            include_assignments (bool): Incluir asignaciones de empleados
            include_client_info (bool): Incluir información del cliente
            include_statistics (bool): Incluir estadísticas del proyecto
            
        Returns:
            List[ProjectWithAssignments]: Proyectos con información completa
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_projects_with_assignments(self) -> List[ProjectWithAssignments]:
        """
        Obtiene proyectos con sus asignaciones de empleados.
        
        Returns:
            List[ProjectWithAssignments]: Proyectos con asignaciones
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_full_context(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene el contexto completo de un proyecto específico.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Contexto completo del proyecto
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # BÚSQUEDAS AVANZADAS CON FILTROS COMPLEJOS
    # ==========================================

    @abstractmethod
    async def advanced_search_projects(
        self, 
        filters: ProjectAdvancedFilters
    ) -> List[ProjectWithAssignments]:
        """
        Realiza búsquedas avanzadas con filtros complejos.
        
        Args:
            filters (ProjectAdvancedFilters): Filtros avanzados de búsqueda
            
        Returns:
            List[ProjectWithAssignments]: Proyectos que coinciden con los filtros
            
        Raises:
            ValidationError: Si los filtros no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def search_projects_with_complex_criteria(
        self,
        criteria: Dict[str, Any],
        sort_options: Optional[List[Dict[str, str]]] = None,
        limit: Optional[int] = None
    ) -> List[ProjectWithAssignments]:
        """
        Busca proyectos con criterios complejos y múltiples ordenamientos.
        
        Args:
            criteria (Dict[str, Any]): Criterios de búsqueda complejos
            sort_options (List[Dict[str, str]], optional): Opciones de ordenamiento
            limit (int, optional): Límite de resultados
            
        Returns:
            List[ProjectWithAssignments]: Proyectos encontrados
            
        Raises:
            ValidationError: Si los criterios no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE DATOS Y AGREGACIONES
    # ==========================================

    @abstractmethod
    async def get_projects_dashboard_data(
        self,
        date_range: Optional[Tuple[date, date]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene datos agregados para el dashboard de proyectos.
        
        Args:
            date_range (Tuple[date, date], optional): Rango de fechas para filtrar
            
        Returns:
            Dict[str, Any]: Datos del dashboard con métricas y estadísticas
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_project_trends(
        self,
        period_months: int = 12
    ) -> Dict[str, Any]:
        """
        Analiza tendencias de proyectos en un período específico.
        
        Args:
            period_months (int): Período en meses para el análisis
            
        Returns:
            Dict[str, Any]: Análisis de tendencias
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_project_performance_metrics(
        self,
        project_ids: Optional[List[int]] = None
    ) -> Dict[str, Any]:
        """
        Obtiene métricas de rendimiento de proyectos.
        
        Args:
            project_ids (List[int], optional): IDs específicos de proyectos
            
        Returns:
            Dict[str, Any]: Métricas de rendimiento
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS DE CARGA DE TRABAJO
    # ==========================================

    @abstractmethod
    async def analyze_project_workload_distribution(self) -> EmployeeWorkloadSchema:
        """
        Analiza la distribución de carga de trabajo en proyectos.
        
        Returns:
            EmployeeWorkloadSchema: Análisis de distribución de carga
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_resource_utilization_analysis(
        self,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> Dict[str, Any]:
        """
        Analiza la utilización de recursos en proyectos.
        
        Args:
            start_date (date, optional): Fecha de inicio del análisis
            end_date (date, optional): Fecha de fin del análisis
            
        Returns:
            Dict[str, Any]: Análisis de utilización de recursos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_team_capacity_vs_demand(self) -> Dict[str, Any]:
        """
        Analiza la capacidad del equipo versus la demanda de proyectos.
        
        Returns:
            Dict[str, Any]: Análisis de capacidad vs demanda
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS TEMPORAL Y CRONOGRAMAS
    # ==========================================

    @abstractmethod
    async def get_project_timeline_analysis(
        self,
        project_ids: Optional[List[int]] = None
    ) -> List[ProjectTimelineSchema]:
        """
        Analiza cronogramas y líneas de tiempo de proyectos.
        
        Args:
            project_ids (List[int], optional): IDs específicos de proyectos
            
        Returns:
            List[ProjectTimelineSchema]: Análisis de cronogramas
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def analyze_project_scheduling_conflicts(self) -> Dict[str, Any]:
        """
        Analiza conflictos de programación entre proyectos.
        
        Returns:
            Dict[str, Any]: Análisis de conflictos de programación
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def get_critical_path_analysis(self, project_id: int) -> Dict[str, Any]:
        """
        Realiza análisis de ruta crítica para un proyecto.
        
        Args:
            project_id (int): ID del proyecto
            
        Returns:
            Dict[str, Any]: Análisis de ruta crítica
            
        Raises:
            NotFoundError: Si el proyecto no existe
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS GEOESPACIALES Y UBICACIÓN
    # ==========================================

    @abstractmethod
    async def get_projects_by_geographic_region(
        self,
        region_criteria: Dict[str, Any]
    ) -> List[Project]:
        """
        Obtiene proyectos filtrados por región geográfica.
        
        Args:
            region_criteria (Dict[str, Any]): Criterios geográficos
            
        Returns:
            List[Project]: Proyectos en la región especificada
            
        Raises:
            ValidationError: Si los criterios geográficos no son válidos
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # ANÁLISIS PREDICTIVO Y FORECASTING
    # ==========================================

    @abstractmethod
    async def predict_project_completion_dates(
        self,
        project_ids: Optional[List[int]] = None
    ) -> Dict[int, Dict[str, Any]]:
        """
        Predice fechas de finalización de proyectos basado en tendencias.
        
        Args:
            project_ids (List[int], optional): IDs específicos de proyectos
            
        Returns:
            Dict[int, Dict[str, Any]]: Predicciones por proyecto
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def forecast_resource_needs(
        self,
        forecast_months: int = 6
    ) -> Dict[str, Any]:
        """
        Pronostica necesidades de recursos para proyectos futuros.
        
        Args:
            forecast_months (int): Meses hacia adelante para el pronóstico
            
        Returns:
            Dict[str, Any]: Pronóstico de necesidades de recursos
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    # ==========================================
    # CONSULTAS DE OPTIMIZACIÓN
    # ==========================================

    @abstractmethod
    async def optimize_project_scheduling(
        self,
        constraints: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Optimiza la programación de proyectos según restricciones.
        
        Args:
            constraints (Dict[str, Any]): Restricciones para la optimización
            
        Returns:
            Dict[str, Any]: Programación optimizada
            
        Raises:
            ValidationError: Si las restricciones no son válidas
            RepositoryError: Si hay errores en la base de datos
        """
        pass

    @abstractmethod
    async def suggest_project_rebalancing(self) -> Dict[str, Any]:
        """
        Sugiere rebalanceo de proyectos para optimizar recursos.
        
        Returns:
            Dict[str, Any]: Sugerencias de rebalanceo
            
        Raises:
            RepositoryError: Si hay errores en la base de datos
        """
        pass