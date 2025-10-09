# src/planificador/services/domain/team/interfaces/membership_operations.py

"""
Interfaz para operaciones de gestión de membresías del servicio de dominio de Team.

Define los métodos para administrar miembros de equipos, incluyendo roles,
capacidad organizacional y transferencia de responsabilidades.
"""

from abc import ABC, abstractmethod
from typing import List, Optional
from datetime import datetime

from .....schemas.team.team import TeamMembership, TeamMembershipCreate
from .....schemas.team.team_advanced_schemas import TeamMembershipSchema
from .....models.team_membership import MembershipRole


class ITeamDomainMembershipOperations(ABC):
    """
    Interfaz para operaciones de gestión de membresías del servicio de dominio de Team.
    
    Define los métodos para la administración completa de miembros del equipo,
    incluyendo validación de roles, capacidad y transferencia de responsabilidades.
    """

    @abstractmethod
    async def add_team_member(
        self,
        team_id: int,
        member_id: int,
        role: str,
        start_date: Optional[datetime] = None
    ) -> bool:
        """
        Agrega un nuevo miembro a un equipo con rol específico.
        
        Args:
            team_id: Identificador único del equipo
            member_id: Identificador único del miembro
            role: Rol del miembro en el equipo
            start_date: Fecha de inicio opcional (por defecto fecha actual)
            
        Returns:
            bool: True si se agregó exitosamente
            
        Raises:
            NotFoundError: Si el equipo o miembro no existe
            BusinessRuleViolationError: Si viola reglas de membresía
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def remove_team_member(
        self,
        team_id: int,
        member_id: int
    ) -> bool:
        """
        Remueve un miembro específico de un equipo.
        
        Args:
            team_id: Identificador único del equipo
            member_id: Identificador único del miembro
            
        Returns:
            bool: True si se removió exitosamente
            
        Raises:
            NotFoundError: Si el equipo, miembro o membresía no existe
            BusinessRuleViolationError: Si viola reglas de negocio
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def update_member_role(
        self,
        team_id: int,
        member_id: int,
        new_role: str
    ) -> bool:
        """
        Actualiza el rol de un miembro existente en el equipo.
        
        Args:
            team_id: Identificador único del equipo
            member_id: Identificador único del miembro
            new_role: Nuevo rol para el miembro
            
        Returns:
            bool: True si se actualizó exitosamente
            
        Raises:
            NotFoundError: Si el equipo, miembro o membresía no existe
            ValidationError: Si el nuevo rol no es válido
            RepositoryError: Si hay error en la persistencia
        """
        pass

    @abstractmethod
    async def get_team_members(
        self,
        team_id: int,
        include_inactive: bool = False
    ) -> List[TeamMembershipSchema]:
        """
        Obtiene todos los miembros de un equipo específico.
        
        Args:
            team_id: Identificador único del equipo
            include_inactive: Si incluir miembros inactivos
            
        Returns:
            List[TeamMemberSchema]: Lista de miembros del equipo
            
        Raises:
            NotFoundError: Si el equipo no existe
            RepositoryError: Si hay error en la consulta
        """
        pass