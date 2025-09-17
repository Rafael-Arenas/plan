# src/planificador/repositories/team/interfaces/relationship_interface.py

"""
Interfaz para operaciones de relaciones del repositorio Team.

Este módulo define la interfaz abstracta para las operaciones de
gestión de relaciones entre equipos, empleados y otras entidades.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para relaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de relaciones

Uso:
    ```python
    class TeamRelationshipModule(ITeamRelationshipOperations):
        async def get_team_with_members(self, team_id: int) -> Optional[Team]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from planificador.models.team import Team
from planificador.models.employee import Employee
from planificador.models.team_membership import TeamMembership
from planificador.enums.membership_role import MembershipRole
from planificador.exceptions.repository import TeamRepositoryError


class ITeamRelationshipOperations(ABC):
    """
    Interfaz abstracta para operaciones de relaciones de equipos.
    
    Define los métodos para gestionar las relaciones entre equipos,
    empleados, membresías y otras entidades del sistema.
    
    Métodos:
        - Gestión de membresías (agregar, remover, actualizar)
        - Gestión de liderazgo
        - Consultas con relaciones cargadas
        - Operaciones de membresía avanzadas
    """
    
    @abstractmethod
    async def get_team_with_leader(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo con información del líder cargada.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Optional[Team]: Equipo con líder cargado o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_with_members(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo con información de miembros cargada.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Optional[Team]: Equipo con miembros cargados o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_with_all_relations(self, team_id: int) -> Optional[Team]:
        """
        Obtiene un equipo con todas las relaciones cargadas.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Optional[Team]: Equipo con todas las relaciones o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_members(
        self, 
        team_id: int, 
        active_only: bool = True
    ) -> List[Employee]:
        """
        Obtiene los miembros de un equipo.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[Employee]: Lista de empleados miembros del equipo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_teams_by_member(self, employee_id: int) -> List[Team]:
        """
        Obtiene equipos donde el empleado es miembro.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[Team]: Lista de equipos donde es miembro
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_members_by_role(
        self, 
        team_id: int, 
        role: MembershipRole
    ) -> List[Employee]:
        """
        Obtiene miembros de un equipo por rol específico.
        
        Args:
            team_id: ID del equipo
            role: Rol de membresía a filtrar
        
        Returns:
            List[Employee]: Lista de empleados con el rol especificado
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def add_member(
        self,
        team_id: int,
        employee_id: int,
        role: Optional[MembershipRole] = None,
        start_date: Optional[date] = None
    ) -> TeamMembership:
        """
        Añade un miembro a un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            role: Rol del miembro (por defecto MEMBER)
            start_date: Fecha de inicio de la membresía
        
        Returns:
            TeamMembership: Membresía creada
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la operación
            ValidationError: Si la membresía ya existe o datos inválidos
        """
        pass
    
    @abstractmethod
    async def remove_member(
        self,
        team_id: int,
        employee_id: int,
        end_date: Optional[date] = None
    ) -> bool:
        """
        Remueve un miembro de un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            end_date: Fecha de fin de la membresía
        
        Returns:
            bool: True si se removió exitosamente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la operación
            NotFoundError: Si la membresía no existe
        """
        pass
    
    @abstractmethod
    async def update_member_role(
        self,
        team_id: int,
        employee_id: int,
        new_role: MembershipRole
    ) -> bool:
        """
        Actualiza el rol de un miembro en el equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            new_role: Nuevo rol del miembro
        
        Returns:
            bool: True si se actualizó exitosamente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la operación
            NotFoundError: Si la membresía no existe
            ValidationError: Si el cambio de rol no es válido
        """
        pass
    
    @abstractmethod
    async def is_member(
        self, 
        team_id: int, 
        employee_id: int, 
        active_only: bool = True
    ) -> bool:
        """
        Verifica si un empleado es miembro de un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
            active_only: Si solo considerar membresías activas
        
        Returns:
            bool: True si es miembro del equipo
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la verificación
        """
        pass
    
    @abstractmethod
    async def get_active_membership(
        self, 
        team_id: int, 
        employee_id: int
    ) -> Optional[TeamMembership]:
        """
        Obtiene la membresía activa de un empleado en un equipo.
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado
        
        Returns:
            Optional[TeamMembership]: Membresía activa o None si no existe
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def assign_leader(self, team_id: int, leader_id: int) -> bool:
        """
        Asigna un líder al equipo.
        
        Args:
            team_id: ID del equipo
            leader_id: ID del empleado que será líder
        
        Returns:
            bool: True si se asignó exitosamente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la asignación
            ValidationError: Si el empleado no puede ser líder
        """
        pass
    
    @abstractmethod
    async def remove_leader(self, team_id: int) -> bool:
        """
        Remueve el líder del equipo.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            bool: True si se removió exitosamente
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la operación
        """
        pass
    
    @abstractmethod
    async def get_team_membership_history(
        self, 
        team_id: int
    ) -> List[TeamMembership]:
        """
        Obtiene el historial completo de membresías de un equipo.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            List[TeamMembership]: Lista de todas las membresías (activas e inactivas)
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass
    
    @abstractmethod
    async def get_employee_team_history(
        self, 
        employee_id: int
    ) -> List[TeamMembership]:
        """
        Obtiene el historial de equipos de un empleado.
        
        Args:
            employee_id: ID del empleado
        
        Returns:
            List[TeamMembership]: Lista de membresías del empleado
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la consulta
        """
        pass