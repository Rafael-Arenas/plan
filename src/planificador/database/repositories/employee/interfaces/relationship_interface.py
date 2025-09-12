# src/planificador/database/repositories/employee/interfaces/relationship_interface.py

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from .....models.employee import Employee
from .....models.team import Team
from .....models.project import Project
from .....models.vacation import Vacation
from .....models.team_membership import TeamMembership
from .....models.project_assignment import ProjectAssignment


class IEmployeeRelationshipOperations(ABC):
    """
    Interfaz para operaciones de relaciones de empleados.
    
    Define métodos para gestionar las relaciones de empleados con equipos,
    proyectos, vacaciones y otros elementos relacionados.
    """
    
    @abstractmethod
    async def get_employee_teams(self, employee_id: int) -> List[Team]:
        """
        Obtiene todos los equipos a los que pertenece un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de equipos del empleado
        """
        pass
    
    @abstractmethod
    async def get_employee_projects(self, employee_id: int) -> List[Project]:
        """
        Obtiene todos los proyectos asignados a un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de proyectos del empleado
        """
        pass
    
    @abstractmethod
    async def get_employee_vacations(self, employee_id: int) -> List[Vacation]:
        """
        Obtiene todas las vacaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de vacaciones del empleado
        """
        pass
    
    @abstractmethod
    async def get_team_memberships(self, employee_id: int) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de equipo de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de membresías de equipo
        """
        pass
    
    @abstractmethod
    async def get_project_assignments(self, employee_id: int) -> List[ProjectAssignment]:
        """
        Obtiene todas las asignaciones de proyecto de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Lista de asignaciones de proyecto
        """
        pass
    
    @abstractmethod
    async def check_team_membership(self, employee_id: int, team_id: int) -> bool:
        """
        Verifica si un empleado pertenece a un equipo específico.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            
        Returns:
            True si pertenece al equipo, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def check_project_assignment(self, employee_id: int, project_id: int) -> bool:
        """
        Verifica si un empleado está asignado a un proyecto específico.
        
        Args:
            employee_id: ID del empleado
            project_id: ID del proyecto
            
        Returns:
            True si está asignado al proyecto, False en caso contrario
        """
        pass
    
    @abstractmethod
    async def get_employees_by_team(self, team_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados de un equipo específico.
        
        Args:
            team_id: ID del equipo
            
        Returns:
            Lista de empleados del equipo
        """
        pass
    
    @abstractmethod
    async def get_employees_by_project(self, project_id: int) -> List[Employee]:
        """
        Obtiene todos los empleados asignados a un proyecto específico.
        
        Args:
            project_id: ID del proyecto
            
        Returns:
            Lista de empleados del proyecto
        """
        pass
    
    @abstractmethod
    async def validate_employee_exists(self, employee_id: int) -> Employee:
        """
        Valida que un empleado existe y lo retorna.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado encontrado
            
        Raises:
            ValidationError: Si el empleado no existe
        """
        pass
    
    @abstractmethod
    async def get_employee_with_all_relations(self, employee_id: int) -> Optional[Employee]:
        """
        Obtiene un empleado con todas sus relaciones cargadas.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Empleado con todas las relaciones cargadas o None
        """
        pass
    
    @abstractmethod
    async def count_employee_relationships(self, employee_id: int) -> Dict[str, int]:
        """
        Cuenta las relaciones de un empleado.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            Diccionario con conteos de relaciones
        """
        pass
    
    @abstractmethod
    async def has_dependencies(self, employee_id: int) -> bool:
        """
        Verifica si un empleado tiene dependencias que impidan su eliminación.
        
        Args:
            employee_id: ID del empleado
            
        Returns:
            True si tiene dependencias, False en caso contrario
        """
        pass