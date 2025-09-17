# src/planificador/repositories/team/interfaces/validation_interface.py

"""
Interfaz para operaciones de validación del repositorio Team.

Este módulo define la interfaz abstracta para las operaciones de
validación de datos, reglas de negocio y consistencia de equipos.

Principios de Diseño:
    - Interface Segregation: Interfaz específica para validaciones
    - Dependency Inversion: Abstracción para implementaciones concretas
    - Single Responsibility: Solo operaciones de validación

Uso:
    ```python
    class TeamValidationModule(ITeamValidationOperations):
        async def validate_team_data(self, team_data: Dict[str, Any]) -> bool:
            # Implementación específica
            pass
    ```
"""

from abc import ABC, abstractmethod
from typing import Dict, Any, List, Optional
from datetime import date

from planificador.exceptions.repository import TeamRepositoryError


class ITeamValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de equipos.
    
    Define los métodos para validar datos de equipos, reglas de negocio,
    consistencia de datos y restricciones del dominio.
    
    Métodos:
        - Validación de datos de equipos
        - Validación de membresías y roles
        - Validación de reglas de negocio
        - Validación de consistencia
    """
    
    @abstractmethod
    async def validate_team_data(self, team_data: Dict[str, Any]) -> bool:
        """
        Valida datos básicos de un equipo.
        
        Args:
            team_data: Diccionario con datos del equipo
                - name: Nombre del equipo (requerido)
                - description: Descripción (opcional)
                - department: Departamento (requerido)
                - is_active: Estado activo (opcional, default True)
        
        Returns:
            bool: True si los datos son válidos
        
        Raises:
            TeamRepositoryError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    async def validate_team_id(self, team_id: int) -> bool:
        """
        Valida que un ID de equipo sea válido y exista.
        
        Args:
            team_id: ID del equipo a validar
        
        Returns:
            bool: True si el ID es válido y existe
        
        Raises:
            TeamRepositoryError: Si el ID no es válido o no existe
        """
        pass
    
    @abstractmethod
    async def validate_team_name_uniqueness(
        self, 
        name: str, 
        exclude_team_id: Optional[int] = None
    ) -> bool:
        """
        Valida que el nombre del equipo sea único.
        
        Args:
            name: Nombre del equipo a validar
            exclude_team_id: ID de equipo a excluir de la validación (para updates)
        
        Returns:
            bool: True si el nombre es único
        
        Raises:
            TeamRepositoryError: Si el nombre ya existe
        """
        pass
    
    @abstractmethod
    async def validate_membership_data(self, membership_data: Dict[str, Any]) -> bool:
        """
        Valida datos de membresía de equipo.
        
        Args:
            membership_data: Diccionario con datos de membresía
                - team_id: ID del equipo (requerido)
                - employee_id: ID del empleado (requerido)
                - role: Rol en el equipo (requerido)
                - start_date: Fecha de inicio (requerido)
                - end_date: Fecha de fin (opcional)
                - is_leader: Es líder (opcional, default False)
        
        Returns:
            bool: True si los datos son válidos
        
        Raises:
            TeamRepositoryError: Si los datos no son válidos
        """
        pass
    
    @abstractmethod
    async def validate_employee_id(self, employee_id: int) -> bool:
        """
        Valida que un ID de empleado sea válido y exista.
        
        Args:
            employee_id: ID del empleado a validar
        
        Returns:
            bool: True si el ID es válido y existe
        
        Raises:
            TeamRepositoryError: Si el ID no es válido o no existe
        """
        pass
    
    @abstractmethod
    async def validate_date_range(
        self, 
        start_date: date, 
        end_date: Optional[date] = None
    ) -> bool:
        """
        Valida que un rango de fechas sea lógico.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin (opcional)
        
        Returns:
            bool: True si el rango es válido
        
        Raises:
            TeamRepositoryError: Si el rango no es válido
        """
        pass
    
    @abstractmethod
    async def validate_membership_overlap(
        self, 
        employee_id: int, 
        team_id: int, 
        start_date: date, 
        end_date: Optional[date] = None
    ) -> bool:
        """
        Valida que no haya solapamiento de membresías.
        
        Args:
            employee_id: ID del empleado
            team_id: ID del equipo
            start_date: Fecha de inicio de la nueva membresía
            end_date: Fecha de fin de la nueva membresía (opcional)
        
        Returns:
            bool: True si no hay solapamiento
        
        Raises:
            TeamRepositoryError: Si hay solapamiento de membresías
        """
        pass
    
    @abstractmethod
    async def validate_leadership_assignment(
        self, 
        team_id: int, 
        employee_id: int, 
        start_date: date
    ) -> bool:
        """
        Valida asignación de liderazgo (solo un líder activo por equipo).
        
        Args:
            team_id: ID del equipo
            employee_id: ID del empleado que será líder
            start_date: Fecha de inicio del liderazgo
        
        Returns:
            bool: True si la asignación es válida
        
        Raises:
            TeamRepositoryError: Si ya existe un líder activo
        """
        pass
    
    @abstractmethod
    async def validate_team_capacity(
        self, 
        team_id: int, 
        new_members_count: int = 1
    ) -> bool:
        """
        Valida que el equipo no exceda su capacidad máxima.
        
        Args:
            team_id: ID del equipo
            new_members_count: Número de nuevos miembros a agregar
        
        Returns:
            bool: True si no se excede la capacidad
        
        Raises:
            TeamRepositoryError: Si se excede la capacidad máxima
        """
        pass
    
    @abstractmethod
    async def validate_role_permissions(
        self, 
        role: str, 
        operation: str
    ) -> bool:
        """
        Valida permisos de rol para operaciones específicas.
        
        Args:
            role: Rol del usuario
            operation: Operación a validar
        
        Returns:
            bool: True si el rol tiene permisos
        
        Raises:
            TeamRepositoryError: Si el rol no tiene permisos
        """
        pass
    
    @abstractmethod
    async def validate_department_exists(self, department: str) -> bool:
        """
        Valida que un departamento exista en el sistema.
        
        Args:
            department: Nombre del departamento
        
        Returns:
            bool: True si el departamento existe
        
        Raises:
            TeamRepositoryError: Si el departamento no existe
        """
        pass
    
    @abstractmethod
    async def validate_team_deletion(self, team_id: int) -> bool:
        """
        Valida que un equipo pueda ser eliminado (sin membresías activas).
        
        Args:
            team_id: ID del equipo
        
        Returns:
            bool: True si el equipo puede ser eliminado
        
        Raises:
            TeamRepositoryError: Si el equipo tiene membresías activas
        """
        pass
    
    @abstractmethod
    async def validate_membership_end_date(
        self, 
        membership_id: int, 
        end_date: date
    ) -> bool:
        """
        Valida fecha de fin de membresía (debe ser posterior al inicio).
        
        Args:
            membership_id: ID de la membresía
            end_date: Fecha de fin propuesta
        
        Returns:
            bool: True si la fecha es válida
        
        Raises:
            TeamRepositoryError: Si la fecha no es válida
        """
        pass
    
    @abstractmethod
    async def validate_business_rules(
        self, 
        operation: str, 
        data: Dict[str, Any]
    ) -> bool:
        """
        Valida reglas de negocio específicas según la operación.
        
        Args:
            operation: Tipo de operación (create, update, delete, etc.)
            data: Datos a validar
        
        Returns:
            bool: True si cumple las reglas de negocio
        
        Raises:
            TeamRepositoryError: Si no cumple las reglas de negocio
        """
        pass
    
    @abstractmethod
    async def validate_data_consistency(
        self, 
        team_id: int
    ) -> Dict[str, Any]:
        """
        Valida consistencia de datos de un equipo.
        
        Args:
            team_id: ID del equipo
        
        Returns:
            Dict[str, Any]: Reporte de consistencia
                - is_consistent: bool
                - issues: List[str] con problemas encontrados
                - warnings: List[str] con advertencias
        
        Raises:
            TeamRepositoryError: Si ocurre un error durante la validación
        """
        pass
    
    @abstractmethod
    async def validate_search_criteria(self, criteria: Dict[str, Any]) -> bool:
        """
        Valida criterios de búsqueda para equipos.
        
        Args:
            criteria: Diccionario con criterios de búsqueda
        
        Returns:
            bool: True si los criterios son válidos
        
        Raises:
            TeamRepositoryError: Si los criterios no son válidos
        """
        pass