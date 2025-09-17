# src/planificador/repositories/team/interfaces/statistics_interface.py

"""
Interfaz para operaciones de estadísticas del repositorio Team.

Este módulo define la interfaz abstracta para las operaciones de
cálculo de estadísticas, métricas y análisis de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para estadísticas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de análisis y estadísticas

Uso:
    ```python
    class TeamStatisticsModule(ITeamStatisticsOperations):
        async def get_team_count_stats(self) -> Dict[str, int]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List
from datetime import date

from planificador.exceptions.repository import TeamRepositoryError


class ITeamStatisticsOperations(ABC):
    """
    Interfaz abstracta para operaciones de estadísticas de equipos.
    
    Define los métodos para generar estadísticas, métricas y análisis
    relacionados con equipos, membresías y rendimiento.
    
    Métodos:
        - Estadísticas básicas de equipos
        - Análisis de distribución y tamaños
        - Métricas de membresías y participación
        - Reportes y tendencias
    """
    
    @abstractmethod
    async def get_team_count_stats(self) -> Dict[str, int]:
        """
        Obtiene conteo de equipos (totales, activos, con/sin líder).
        
        Returns:
            Dict[str, int]: Estadísticas de conteo
                - total_teams: Total de equipos
                - active_teams: Equipos activos
                - inactive_teams: Equipos inactivos
                - teams_with_leader: Equipos con líder asignado
                - teams_without_leader: Equipos sin líder
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_team_size_distribution(self) -> Dict[str, Any]:
        """
        Obtiene distribución de tamaños por equipo.
        
        Returns:
            Dict[str, Any]: Distribución de tamaños
                - size_ranges: Dict con rangos de tamaño y conteos
                - average_size: Tamaño promedio de equipos
                - median_size: Tamaño mediano
                - largest_team: Información del equipo más grande
                - smallest_team: Información del equipo más pequeño
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_department_stats(self) -> Dict[str, Any]:
        """
        Obtiene estadísticas por departamento.
        
        Returns:
            Dict[str, Any]: Estadísticas departamentales
                - departments: Lista de departamentos únicos
                - teams_per_department: Dict con conteo por departamento
                - largest_department: Departamento con más equipos
                - average_teams_per_department: Promedio de equipos por departamento
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_membership_stats(self) -> Dict[str, Any]:
        """
        Obtiene conteo de membresías (totales, activas, distribución por rol).
        
        Returns:
            Dict[str, Any]: Estadísticas de membresías
                - total_memberships: Total de membresías
                - active_memberships: Membresías activas
                - inactive_memberships: Membresías inactivas
                - memberships_by_role: Dict con conteo por rol
                - average_members_per_team: Promedio de miembros por equipo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_employee_team_participation(
        self, 
        employee_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene participación de empleados en equipos.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            Dict[str, Any]: Estadísticas de participación
                - current_teams: Número de equipos actuales
                - total_teams_history: Total de equipos en historial
                - leadership_roles: Número de roles de liderazgo
                - membership_duration_avg: Duración promedio de membresías
                - most_recent_team: Información del equipo más reciente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_membership_trends(
        self, 
        start_date: date, 
        end_date: date
    ) -> Dict[str, Any]:
        """
        Obtiene tendencias de membresías en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
        
        Returns:
            Dict[str, Any]: Tendencias de membresías
                - new_memberships: Nuevas membresías en el período
                - ended_memberships: Membresías terminadas
                - net_change: Cambio neto de membresías
                - monthly_breakdown: Desglose mensual de cambios
                - most_active_teams: Equipos con más cambios
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_team_efficiency_metrics(self, team_id: int) -> Dict[str, Any]:
        """
        Obtiene métricas de eficiencia de equipos.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Métricas de eficiencia
                - member_retention_rate: Tasa de retención de miembros
                - average_membership_duration: Duración promedio de membresías
                - leadership_stability: Estabilidad del liderazgo
                - team_growth_rate: Tasa de crecimiento del equipo
                - role_distribution: Distribución de roles
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_summary_report(self) -> Dict[str, Any]:
        """
        Obtiene reporte resumen completo de estadísticas de equipos.
        
        Returns:
            Dict[str, Any]: Reporte completo
                - team_overview: Resumen general de equipos
                - membership_overview: Resumen de membresías
                - department_analysis: Análisis departamental
                - size_analysis: Análisis de tamaños
                - leadership_analysis: Análisis de liderazgo
                - trends_summary: Resumen de tendencias
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la generación
        """
        pass
    
    @abstractmethod
    async def get_team_activity_stats(self, team_id: int) -> Dict[str, Any]:
        """
        Calcula estadísticas de actividad de un equipo usando Pendulum.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Estadísticas de actividad
                - creation_date: Fecha de creación formateada
                - days_since_creation: Días desde la creación
                - last_membership_change: Último cambio de membresía
                - activity_level: Nivel de actividad (alto/medio/bajo)
                - membership_changes_last_month: Cambios en el último mes
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_teams_by_department_summary(self) -> Dict[str, int]:
        """
        Obtiene un resumen de equipos agrupados por departamento.
        
        Returns:
            Dict[str, int]: Conteo de equipos por departamento
                - Clave: Nombre del departamento
                - Valor: Número de equipos en ese departamento
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass
    
    @abstractmethod
    async def get_team_stats(self, team_id: int) -> Dict[str, Any]:
        """
        Obtiene estadísticas de un equipo específico.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Estadísticas del equipo
                - basic_info: Información básica del equipo
                - member_count: Número de miembros
                - role_distribution: Distribución de roles
                - membership_duration_stats: Estadísticas de duración
                - activity_metrics: Métricas de actividad
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante el cálculo
        """
        pass