# src/planificador/repositories/team_membership/interfaces/query_interface.py

"""
Interfaz para operaciones de consulta del repositorio TeamMembership.

Este módulo define la interfaz abstracta para las operaciones de
búsqueda y consulta de membresías de equipos en el sistema.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para consultas
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de consulta

Uso:
    ```python
    class TeamMembershipQueryModule(ITeamMembershipQueryOperations):
        async def get_membership_by_id(self, membership_id: int) -> Optional[TeamMembership]:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any
from datetime import date

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.models.employee import Employee
from planificador.models.team import Team
from planificador.exceptions.repository import TeamMembershipRepositoryError


class ITeamMembershipQueryOperations(ABC):
    """
    Interfaz abstracta para operaciones de consulta de membresías de equipos.
    
    Define los métodos de búsqueda y consulta que debe implementar
    cualquier módulo que maneje la recuperación de datos de membresías.
    
    Métodos:
        - Consultas básicas por ID, empleado, equipo
        - Búsquedas por criterios específicos (rol, fechas, estado)
        - Consultas con filtros avanzados
        - Consultas de historial y tendencias
    """
    
    @abstractmethod
    async def get_membership_by_id(self, membership_id: int) -> Optional[TeamMembership]:
        """
        Obtiene una membresía por su ID.
        
        Args:
            membership_id: ID de la membresía
        
        Returns:
            Optional[TeamMembership]: La membresía encontrada o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_memberships_by_employee(
        self, 
        employee_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un empleado.
        
        Args:
            employee_id: ID del empleado
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías del empleado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_memberships_by_team(
        self, 
        team_id: int,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías de un equipo.
        
        Args:
            team_id: ID del equipo
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías del equipo
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_membership_by_employee_and_team(
        self,
        employee_id: int,
        team_id: int,
        active_only: bool = True
    ) -> Optional[TeamMembership]:
        """
        Obtiene la membresía específica de un empleado en un equipo.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            active_only: Si solo buscar membresías activas
        
        Returns:
            Optional[TeamMembership]: La membresía encontrada o None
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_memberships_by_role(
        self, 
        role: MembershipRole,
        active_only: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías con un rol específico.
        
        Args:
            role: Rol a buscar
            active_only: Si solo incluir membresías activas
        
        Returns:
            List[TeamMembership]: Lista de membresías con el rol especificado
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_active_memberships(self) -> List[TeamMembership]:
        """
        Obtiene todas las membresías activas del sistema.
        
        Returns:
            List[TeamMembership]: Lista de membresías activas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_memberships_by_date_range(
        self,
        start_date: date,
        end_date: date,
        include_overlapping: bool = True
    ) -> List[TeamMembership]:
        """
        Obtiene membresías en un rango de fechas.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            include_overlapping: Si incluir membresías que se solapan parcialmente
        
        Returns:
            List[TeamMembership]: Lista de membresías en el rango
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_current_memberships(self, as_of_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías vigentes en una fecha específica.
        
        Args:
            as_of_date: Fecha de referencia (opcional, default hoy)
        
        Returns:
            List[TeamMembership]: Lista de membresías vigentes
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_future_memberships(self, from_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías futuras desde una fecha.
        
        Args:
            from_date: Fecha desde la cual buscar (opcional, default hoy)
        
        Returns:
            List[TeamMembership]: Lista de membresías futuras
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_past_memberships(self, until_date: Optional[date] = None) -> List[TeamMembership]:
        """
        Obtiene membresías pasadas hasta una fecha.
        
        Args:
            until_date: Fecha hasta la cual buscar (opcional, default hoy)
        
        Returns:
            List[TeamMembership]: Lista de membresías pasadas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def search_memberships(
        self,
        filters: Dict[str, Any],
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Busca membresías con filtros avanzados.
        
        Args:
            filters: Diccionario con criterios de búsqueda
                - employee_id: ID del empleado (opcional)
                - team_id: ID del equipo (opcional)
                - role: Rol específico (opcional)
                - is_active: Estado activo (opcional)
                - start_date_from: Fecha de inicio desde (opcional)
                - start_date_to: Fecha de inicio hasta (opcional)
                - end_date_from: Fecha de fin desde (opcional)
                - end_date_to: Fecha de fin hasta (opcional)
            limit: Límite de resultados (opcional)
            offset: Desplazamiento para paginación (opcional)
        
        Returns:
            List[TeamMembership]: Lista de membresías que cumplen los criterios
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def count_memberships(self, filters: Optional[Dict[str, Any]] = None) -> int:
        """
        Cuenta el número de membresías que cumplen los criterios.
        
        Args:
            filters: Criterios de filtrado (opcional)
        
        Returns:
            int: Número de membresías encontradas
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass
    
    @abstractmethod
    async def get_all_memberships(
        self,
        limit: Optional[int] = None,
        offset: Optional[int] = None
    ) -> List[TeamMembership]:
        """
        Obtiene todas las membresías del sistema.
        
        Args:
            limit: Límite de resultados (opcional)
            offset: Desplazamiento para paginación (opcional)
        
        Returns:
            List[TeamMembership]: Lista de todas las membresías
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la consulta
        """
        pass