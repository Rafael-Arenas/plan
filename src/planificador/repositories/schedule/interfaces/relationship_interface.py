# src/planificador/repositories/schedule/interfaces/relationship_interface.py

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import date

from ....models.schedule import Schedule
from ....models.employee import Employee
from ....models.project import Project
from ....models.team import Team


class IScheduleRelationshipOperations(ABC):
    """
    Interface para operaciones de relaciones del repositorio Schedule.
    
    Define los métodos para gestionar las relaciones entre horarios
    y otras entidades como empleados, proyectos y equipos.
    """
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON EMPLEADOS
    # ==========================================
    
    @abstractmethod
    async def get_employee_schedules_with_details(
        self,
        employee_id: int,
        include_projects: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado con detalles de relaciones.
        
        Args:
            employee_id: ID del empleado
            include_projects: Incluir detalles de proyectos
            include_teams: Incluir detalles de equipos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        pass
    
    @abstractmethod
    async def get_employees_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Employee, List[Schedule]]]:
        """
        Obtiene empleados con sus horarios en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de tuplas (empleado, lista de horarios)
        """
        pass
    
    @abstractmethod
    async def get_employee_schedules_in_period(
        self,
        employee_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Obtiene horarios de un empleado en un período específico.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de horarios del empleado
        """
        pass
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON PROYECTOS
    # ==========================================
    
    @abstractmethod
    async def get_project_schedules_with_details(
        self,
        project_id: int,
        include_employees: bool = True,
        include_teams: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un proyecto con detalles de relaciones.
        
        Args:
            project_id: ID del proyecto
            include_employees: Incluir detalles de empleados
            include_teams: Incluir detalles de equipos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        pass
    
    @abstractmethod
    async def get_projects_with_schedules_in_period(
        self,
        start_date: date,
        end_date: date
    ) -> List[Tuple[Project, List[Schedule]]]:
        """
        Obtiene proyectos con sus horarios en un período.
        
        Args:
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de tuplas (proyecto, lista de horarios)
        """
        pass
    
    @abstractmethod
    async def get_project_schedules_in_period(
        self,
        project_id: int,
        start_date: date,
        end_date: date
    ) -> List[Schedule]:
        """
        Obtiene horarios de un proyecto en un período específico.
        
        Args:
            project_id: ID del proyecto
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período
            
        Returns:
            Lista de horarios del proyecto
        """
        pass
    
    # ==========================================
    # GESTIÓN DE RELACIONES CON EQUIPOS
    # ==========================================
    
    @abstractmethod
    async def get_team_schedules_with_details(
        self,
        team_id: int,
        include_employees: bool = True,
        include_projects: bool = True,
        include_status_codes: bool = True
    ) -> List[Schedule]:
        """
        Obtiene horarios de un equipo con detalles de relaciones.
        
        Args:
            team_id: ID del equipo
            include_employees: Incluir detalles de empleados
            include_projects: Incluir detalles de proyectos
            include_status_codes: Incluir detalles de códigos de estado
            
        Returns:
            Lista de horarios con relaciones cargadas
        """
        pass
    
    # ==========================================
    # OPERACIONES DE ASIGNACIÓN
    # ==========================================
    
    @abstractmethod
    async def assign_schedule_to_project(
        self,
        schedule_id: int,
        project_id: int
    ) -> Schedule:
        """
        Asigna un horario a un proyecto.
        
        Args:
            schedule_id: ID del horario
            project_id: ID del proyecto
            
        Returns:
            Horario actualizado
        """
        pass
    
    @abstractmethod
    async def assign_schedule_to_team(
        self,
        schedule_id: int,
        team_id: int
    ) -> Schedule:
        """
        Asigna un horario a un equipo.
        
        Args:
            schedule_id: ID del horario
            team_id: ID del equipo
            
        Returns:
            Horario actualizado
        """
        pass
    
    @abstractmethod
    async def remove_schedule_from_project(
        self,
        schedule_id: int
    ) -> Schedule:
        """
        Remueve un horario de su proyecto asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
        """
        pass
    
    @abstractmethod
    async def remove_schedule_from_team(
        self,
        schedule_id: int
    ) -> Schedule:
        """
        Remueve un horario de su equipo asignado.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Horario actualizado
        """
        pass
    
    # ==========================================
    # OPERACIONES DE CONSULTA AUXILIARES
    # ==========================================
    
    @abstractmethod
    async def get_schedule_relationships_summary(
        self,
        schedule_id: int
    ) -> Dict[str, Any]:
        """
        Obtiene resumen de relaciones de un horario.
        
        Args:
            schedule_id: ID del horario
            
        Returns:
            Dict con resumen de relaciones
        """
        pass
    
    @abstractmethod
    async def validate_project_assignment(
        self,
        schedule_id: int,
        project_id: int
    ) -> bool:
        """
        Valida si un horario puede ser asignado a un proyecto.
        
        Args:
            schedule_id: ID del horario
            project_id: ID del proyecto
            
        Returns:
            True si la asignación es válida
        """
        pass
    
    @abstractmethod
    async def validate_team_assignment(
        self,
        schedule_id: int,
        team_id: int
    ) -> bool:
        """
        Valida si un horario puede ser asignado a un equipo.
        
        Args:
            schedule_id: ID del horario
            team_id: ID del equipo
            
        Returns:
            True si la asignación es válida
        """
        pass