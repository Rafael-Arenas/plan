# src/planificador/repositories/team_membership/interfaces/relationship_interface.py

"""
Interfaz para operaciones de relaciones del repositorio TeamMembership.

Este módulo define la interfaz abstracta para las operaciones de
gestión de relaciones entre membresías, empleados, equipos y otras entidades.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para relaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de relaciones

Uso:
    ```python
    class TeamMembershipRelationshipModule(ITeamMembershipRelationshipOperations):
        async def get_membership_with_employee(self, membership_id: int) -> Optional[TeamMembership]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any, Tuple
from datetime import date

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.employee import Employee
from planificador.models.team import Team
from planificador.exceptions.repository import TeamMembershipRepositoryError


class ITeamMembershipRelationshipOperations(ABC):
    """
    Interfaz abstracta para operaciones de relaciones de membresías.
    
    Define los métodos para gestionar las relaciones entre membresías,
    empleados, equipos y otras entidades del sistema.
    
    Métodos:
        - Consultas con relaciones cargadas (eager loading)
        - Operaciones de transferencia entre equipos
        - Gestión de conflictos de membresías
        - Análisis de solapamientos y dependencias
    """
    
    @abstractmethod
    async def get_membership_with_employee(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía con información del empleado cargada.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            Optional[TeamMembership]: Membresía con empleado cargado o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_membership_with_team(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía con información del equipo cargada.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            Optional[TeamMembership]: Membresía con equipo cargado o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_membership_with_all_relations(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía con todas las relaciones cargadas.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            Optional[TeamMembership]: Membresía con todas las relaciones o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_employee_teams_with_details(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene equipos de un empleado con detalles de membresía.
        
        Args:
            employee_id: ID del empleado
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[Dict[str, Any]]: Lista con detalles de equipos y membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_members_with_details(
        self, 
        team_id: int,
        active_only: bool = True
    ) -> List[Dict[str, Any]]:
        """
        Obtiene miembros de un equipo con detalles de membresía.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[Dict[str, Any]]: Lista con detalles de empleados y membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def transfer_employee_between_teams(
        self,
        employee_id: int,
        from_team_id: int,
        to_team_id: int,
        transfer_date: date,
        new_role: Optional[MembershipRole] = None
    ) -> Tuple[TeamMembership, TeamMembership]:
        """
        Transfiere un empleado de un equipo a otro.
        
        Args:
            employee_id: ID del empleado
            from_team_id: ID del equipo origen
            to_team_id: ID del equipo destino
            transfer_date: Fecha de transferencia
            new_role: Nuevo rol en el equipo destino (opcional)
        
        Returns:
            Tuple[TeamMembership, TeamMembership]: Membresía finalizada y nueva membresía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la transferencia
        """
        pass
    
    @abstractmethod
    async def get_overlapping_memberships(
        self,
        employee_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Obtiene membresías que se solapan con un período dado.
        
        Args:
            employee_id: ID del empleado
            start_date: Fecha de inicio del período
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías que se solapan
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_membership_conflicts(
        self,
        employee_id: int,
        team_id: int,
        start_date: date,
        end_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Identifica conflictos de membresía para un empleado.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            start_date: Fecha de inicio propuesta
            end_date: Fecha de fin propuesta (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías en conflicto
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_employee_membership_history(
        self, 
        employee_id: int,
        include_future: bool = False
    ) -> List[TeamMembership]:
        """
        Obtiene el historial completo de membresías de un empleado.
        
        Args:
            employee_id: ID del empleado
            include_future: Si incluir membresías futuras
        
        Returns:
            List[TeamMembership]: Historial ordenado por fecha de inicio
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_team_membership_timeline(
        self, 
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene la línea de tiempo de membresías de un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            List[Dict[str, Any]]: Timeline con eventos de membresía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_concurrent_memberships(
        self,
        employee_id: int,
        reference_date: Optional[date] = None
    ) -> List[TeamMembership]:
        """
        Obtiene membresías concurrentes de un empleado en una fecha.
        
        Args:
            employee_id: ID del empleado
            reference_date: Fecha de referencia (opcional, default hoy)
        
        Returns:
            List[TeamMembership]: Lista de membresías concurrentes
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_leadership_transitions(
        self,
        team_id: int,
        start_date: Optional[date] = None,
        end_date: Optional[date] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene transiciones de liderazgo en un equipo.
        
        Args:
            team_id: ID del equipo
            start_date: Fecha de inicio del período (opcional)
            end_date: Fecha de fin del período (opcional)
        
        Returns:
            List[Dict[str, Any]]: Lista de transiciones de liderazgo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_role_changes_history(
        self,
        employee_id: Optional[int] = None,
        team_id: Optional[int] = None
    ) -> List[Dict[str, Any]]:
        """
        Obtiene historial de cambios de roles.
        
        Args:
            employee_id: ID del empleado (opcional)
            team_id: ID del equipo (opcional)
        
        Returns:
            List[Dict[str, Any]]: Historial de cambios de roles
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass