# src/planificador/repositories/team_membership/interfaces/crud_interface.py

"""
Interfaz para operaciones CRUD del repositorio TeamMembership.

Este módulo define la interfaz abstracta para las operaciones básicas
de creación, lectura, actualización y eliminación de membresías de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para operaciones CRUD
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones CRUD básicas

Uso:
    ```python
    class TeamMembershipCrudModule(ITeamMembershipCrudOperations):
        async def create_membership(self, membership_data: Dict[str, Any]) -> TeamMembership:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, Optional
from datetime import date

from planificador.models.team_membership import TeamMembership, MembershipRole
from planificador.exceptions.repository import TeamMembershipRepositoryError


class ITeamMembershipCrudOperations(ABC):
    """
    Interfaz abstracta para operaciones CRUD de membresías de equipos.
    
    Define los métodos básicos que debe implementar cualquier módulo
    que maneje operaciones de creación, lectura, actualización y
    eliminación de membresías de equipos.
    
    Métodos:
        create_membership: Crea una nueva membresía
        update_membership: Actualiza una membresía existente
        delete_membership: Elimina una membresía
        activate_membership: Activa una membresía
        deactivate_membership: Desactiva una membresía
    """
    
    @abstractmethod
    async def create_membership(self, membership_data: Dict[str, Any]) -> TeamMembership:
        """
        Crea una nueva membresía de equipo con validaciones.
        
        Args:
            membership_data: Diccionario con los datos de la membresía
                - employee_id: ID del empleado (requerido)
                - team_id: ID del equipo (requerido)
                - role: Rol en el equipo (opcional, default MEMBER)
                - start_date: Fecha de inicio (requerido)
                - end_date: Fecha de fin (opcional)
                - is_active: Estado activo (opcional, default True)
        
        Returns:
            TeamMembership: La membresía creada con todos sus datos
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la creación
            ValidationError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    async def update_membership(
        self,
        membership_id: int,
        update_data: Dict[str, Any]
    ) -> Optional[TeamMembership]:
        """
        Actualiza una membresía existente.
        
        Args:
            membership_id: ID de la membresía a actualizar
            update_data: Diccionario con los datos a actualizar
                - role: Nuevo rol (opcional)
                - start_date: Nueva fecha de inicio (opcional)
                - end_date: Nueva fecha de fin (opcional)
                - is_active: Nuevo estado activo (opcional)
        
        Returns:
            Optional[TeamMembership]: La membresía actualizada o None si no existe
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la actualización
            ValidationError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    async def delete_membership(self, membership_id: int) -> bool:
        """
        Elimina una membresía de equipo.
        
        Args:
            membership_id: ID de la membresía a eliminar
        
        Returns:
            bool: True si se eliminó correctamente, False si no existía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la eliminación
        """
        pass
    
    @abstractmethod
    async def activate_membership(self, membership_id: int) -> bool:
        """
        Activa una membresía de equipo.
        
        Args:
            membership_id: ID de la membresía a activar
        
        Returns:
            bool: True si se activó correctamente, False si no existía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la activación
        """
        pass
    
    @abstractmethod
    async def deactivate_membership(
        self, 
        membership_id: int,
        end_date: Optional[date] = None
    ) -> bool:
        """
        Desactiva una membresía de equipo.
        
        Args:
            membership_id: ID de la membresía a desactivar
            end_date: Fecha de fin de la membresía (opcional, default hoy)
        
        Returns:
            bool: True si se desactivó correctamente, False si no existía
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la desactivación
        """
        pass
    
    @abstractmethod
    async def update_membership_role(
        self,
        membership_id: int,
        new_role: MembershipRole
    ) -> Optional[TeamMembership]:
        """
        Actualiza el rol de una membresía específica.
        
        Args:
            membership_id: ID de la membresía
            new_role: Nuevo rol para la membresía
        
        Returns:
            Optional[TeamMembership]: La membresía actualizada o None si no existe
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la actualización
        """
        pass
    
    @abstractmethod
    async def end_membership(
        self,
        membership_id: int,
        end_date: date
    ) -> Optional[TeamMembership]:
        """
        Finaliza una membresía estableciendo fecha de fin.
        
        Args:
            membership_id: ID de la membresía
            end_date: Fecha de finalización
        
        Returns:
            Optional[TeamMembership]: La membresía actualizada o None si no existe
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error durante la actualización
        """
        pass