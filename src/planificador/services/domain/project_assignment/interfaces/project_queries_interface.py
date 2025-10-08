# src/planificador/services/domain/project_assignment/interfaces/project_queries_interface.py

"""
Interfaz para Consultas por Proyecto de Asignaciones de Proyecto

Define el contrato para operaciones de consulta centradas en proyectos,
incluyendo equipos, recursos y líneas de tiempo de asignaciones.
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any
from datetime import date

from planificador.schemas import ProjectAssignment


class IProjectQueries(ABC):
    """
    Interfaz para consultas de asignaciones centradas en proyectos.
    
    Proporciona métodos para obtener información detallada sobre
    las asignaciones de proyectos específicos, incluyendo análisis
    de equipos y distribución de recursos.
    """
    
    # ============================================================================
    # OPERACIONES DE CONSULTA POR PROYECTO (4 métodos)
    # ============================================================================
    
    @abstractmethod
    async def get_assignments_by_project(self, project_id: int) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            List[ProjectAssignment]: Lista de todas las asignaciones del proyecto
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_project_team_summary(self, project_id: int) -> Dict[str, Any]:
        """
        Obtiene un resumen completo del equipo asignado al proyecto.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con resumen del equipo incluyendo:
            - project_id: ID del proyecto
            - total_team_members: Número total de miembros del equipo
            - active_members: Número de miembros activos
            - roles_distribution: Distribución de roles en el equipo
            - team_members: Lista detallada de miembros con sus roles
            - total_allocated_hours: Horas totales asignadas al proyecto
            - average_allocation: Asignación promedio por miembro
            - team_capacity: Capacidad total del equipo
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_project_resource_allocation(self, project_id: int) -> Dict[str, Any]:
        """
        Calcula la distribución de recursos del proyecto por roles y tiempo.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Dict con distribución de recursos:
            - project_id: ID del proyecto
            - total_resources: Número total de recursos asignados
            - allocation_by_role: Distribución de horas por rol
            - allocation_by_period: Distribución temporal de recursos
            - resource_utilization: Utilización de recursos por empleado
            - peak_allocation_periods: Períodos de mayor asignación
            - resource_gaps: Períodos con baja asignación de recursos
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass
    
    @abstractmethod
    async def get_project_assignment_timeline(
        self, 
        project_id: int,
        include_milestones: bool = True
    ) -> Dict[str, Any]:
        """
        Genera una línea de tiempo visual de las asignaciones del proyecto.
        
        Args:
            project_id: ID del proyecto
            include_milestones: Si incluir hitos en la línea de tiempo
            
        Returns:
            Dict con línea de tiempo:
            - project_id: ID del proyecto
            - project_start_date: Fecha de inicio del proyecto
            - project_end_date: Fecha de fin del proyecto
            - timeline_events: Lista de eventos de asignación ordenados
            - concurrent_assignments: Asignaciones concurrentes por período
            - resource_peaks: Picos de recursos en la línea de tiempo
            - milestone_assignments: Asignaciones asociadas a hitos
            - timeline_visualization_data: Datos para visualización gráfica
            
        Raises:
            RepositoryError: Si hay errores en la consulta
        """
        pass