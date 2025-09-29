# src/planificador/repositories/team_membership/interfaces/validation_interface.py

"""
Interfaz para operaciones de validación del repositorio TeamMembership.

Este módulo define la interfaz abstracta para las operaciones de
validación de datos, reglas de negocio y consistencia de membresías.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para validaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de validación

Uso:
    ```python
    class TeamMembershipValidationModule(ITeamMembershipValidationOperations):
        async def validate_membership_data(self, data: Dict[str, Any]) -> bool:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import List, Dict, Any, Optional, Tuple
from datetime import date

from planificador.models.team_membership import MembershipRole
from planificador.schemas import MembershipStatus
from planificador.exceptions.repository import TeamMembershipRepositoryError
from planificador.exceptions.validation import ValidationError


class ITeamMembershipValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de membresías.
    
    Define los métodos para validar datos de membresías, reglas de negocio,
    consistencia de datos y restricciones del sistema.
    
    Métodos:
        - Validación de datos de entrada
        - Validación de reglas de negocio
        - Verificación de consistencia
        - Validación de restricciones temporales
    """
    
    @abstractmethod
    async def validate_membership_data(self, data: Dict[str, Any]) -> bool:
        """
        Valida los datos básicos de una membresía.
        
        Args:
            data: Diccionario con datos de la membresía
        
        Returns:
            bool: True si los datos son válidos
        
        Raises:
            ValidationError: Si los datos no son válidos
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_id(self, membership_id: int) -> bool:
        """
        Valida que un ID de membresía existe y es válido.
        
        Args:
            membership_id: ID de la membresía a validar
        
        Returns:
            bool: True si el ID es válido
        
        Raises:
            ValidationError: Si el ID no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_employee_id(self, employee_id: int) -> bool:
        """
        Valida que un ID de empleado existe y es válido.
        
        Args:
            employee_id: ID del empleado a validar
        
        Returns:
            bool: True si el ID es válido
        
        Raises:
            ValidationError: Si el ID no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_team_id(self, team_id: int) -> bool:
        """
        Valida que un ID de equipo existe y es válido.
        
        Args:
            team_id: ID del equipo a validar
        
        Returns:
            bool: True si el ID es válido
        
        Raises:
            ValidationError: Si el ID no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_role(self, role: MembershipRole) -> bool:
        """
        Valida que un rol de membresía es válido.
        
        Args:
            role: Rol a validar
        
        Returns:
            bool: True si el rol es válido
        
        Raises:
            ValidationError: Si el rol no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_status(self, status: MembershipStatus) -> bool:
        """
        Valida que un estado de membresía es válido.
        
        Args:
            status: Estado a validar
        
        Returns:
            bool: True si el estado es válido
        
        Raises:
            ValidationError: Si el estado no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_date_range(
        self, 
        start_date: date, 
        end_date: Optional[date] = None
    ) -> bool:
        """
        Valida que un rango de fechas es válido.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
        
        Returns:
            bool: True si el rango es válido
        
        Raises:
            ValidationError: Si el rango no es válido
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_overlap(
        self,
        employee_id: int,
        team_id: int,
        start_date: date,
        end_date: Optional[date] = None,
        exclude_membership_id: Optional[int] = None
    ) -> bool:
        """
        Valida que no hay solapamiento de membresías.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
            exclude_membership_id: ID de membresía a excluir (opcional)
        
        Returns:
            bool: True si no hay solapamiento
        
        Raises:
            ValidationError: Si hay solapamiento
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_leadership_assignment(
        self,
        employee_id: int,
        team_id: int,
        role: MembershipRole,
        start_date: date,
        end_date: Optional[date] = None
    ) -> bool:
        """
        Valida la asignación de roles de liderazgo.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            role: Rol propuesto
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
        
        Returns:
            bool: True si la asignación es válida
        
        Raises:
            ValidationError: Si la asignación no es válida
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_team_capacity(
        self,
        team_id: int,
        as_of_date: Optional[date] = None
    ) -> bool:
        """
        Valida que un equipo no excede su capacidad máxima.
        
        Args:
            team_id: ID del equipo
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            bool: True si no excede la capacidad
        
        Raises:
            ValidationError: Si excede la capacidad
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_role_permissions(
        self,
        employee_id: int,
        role: MembershipRole,
        team_id: int
    ) -> bool:
        """
        Valida que un empleado tiene permisos para un rol.
        
        Args:
            employee_id: ID del empleado
            role: Rol propuesto
            team_id: ID del equipo
        
        Returns:
            bool: True si tiene permisos
        
        Raises:
            ValidationError: Si no tiene permisos
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_transition(
        self,
        membership_id: int,
        new_status: MembershipStatus,
        transition_date: Optional[date] = None
    ) -> bool:
        """
        Valida una transición de estado de membresía.
        
        Args:
            membership_id: ID de la membresía
            new_status: Nuevo estado propuesto
            transition_date: Fecha de transición (opcional)
        
        Returns:
            bool: True si la transición es válida
        
        Raises:
            ValidationError: Si la transición no es válida
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_membership_end_date(
        self,
        membership_id: int,
        end_date: date
    ) -> bool:
        """
        Valida una fecha de fin de membresía.
        
        Args:
            membership_id: ID de la membresía
            end_date: Fecha de fin propuesta
        
        Returns:
            bool: True si la fecha es válida
        
        Raises:
            ValidationError: Si la fecha no es válida
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(
        self,
        employee_id: int,
        team_id: int,
        role: MembershipRole,
        start_date: date,
        end_date: Optional[date] = None
    ) -> Tuple[bool, List[str]]:
        """
        Valida todas las reglas de negocio para una membresía.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            role: Rol propuesto
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
        
        Returns:
            Tuple[bool, List[str]]: (Es válido, Lista de errores)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_data_consistency(
        self,
        membership_id: Optional[int] = None
    ) -> Tuple[bool, List[str]]:
        """
        Valida la consistencia de datos de membresías.
        
        Args:
            membership_id: ID de membresía específica (opcional)
        
        Returns:
            Tuple[bool, List[str]]: (Es consistente, Lista de inconsistencias)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_search_criteria(self, criteria: Dict[str, Any]) -> bool:
        """
        Valida criterios de búsqueda de membresías.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
        
        Returns:
            bool: True si los criterios son válidos
        
        Raises:
            ValidationError: Si los criterios no son válidos
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_bulk_operation_data(
        self, 
        operations_data: List[Dict[str, Any]]
    ) -> Tuple[bool, List[str]]:
        """
        Valida datos para operaciones en lote.
        
        Args:
            operations_data: Lista de datos de operaciones
        
        Returns:
            Tuple[bool, List[str]]: (Son válidos, Lista de errores)
        
        Raises:
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass
    
    @abstractmethod
    async def validate_concurrent_membership_limit(
        self,
        employee_id: int,
        as_of_date: Optional[date] = None
    ) -> bool:
        """
        Valida el límite de membresías concurrentes de un empleado.
        
        Args:
            employee_id: ID del empleado
            as_of_date: Fecha de referencia (opcional)
        
        Returns:
            bool: True si no excede el límite
        
        Raises:
            ValidationError: Si excede el límite
            TeamMembershipRepositoryError: Si ocurre un error en la validación
        """
        pass