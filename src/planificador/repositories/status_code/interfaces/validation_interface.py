# src/planificador/repositories/status_code/interfaces/validation_interface.py

"""
Interfaz para operaciones de validación de códigos de estado.

Define los métodos de validación y verificación de integridad para la entidad
StatusCode, incluyendo validaciones de unicidad y reglas de negocio.
"""

from abc import ABC, abstractmethod
from typing import Optional

from planificador.models.status_code import StatusCode


class IStatusCodeValidationOperations(ABC):
    """
    Interfaz abstracta para operaciones de validación de códigos de estado.
    
    Define los métodos de validación que debe implementar cualquier módulo
    que maneje verificaciones de integridad, unicidad y reglas de negocio
    para códigos de estado.
    
    Métodos incluyen validación de unicidad de códigos y verificaciones
    de reglas de negocio específicas del dominio.
    """

    # ==========================================
    # VALIDACIONES DE UNICIDAD
    # ==========================================

    @abstractmethod
    async def validate_code_uniqueness(
        self, 
        code: str, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que un código sea único en el sistema.
        
        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el código es único, False si ya existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # VALIDACIONES DE REGLAS DE NEGOCIO
    # ==========================================

    @abstractmethod
    async def validate_status_code_can_be_deleted(self, entity_id: int) -> bool:
        """
        Valida si un código de estado puede ser eliminado.
        
        Verifica que el código no esté siendo utilizado en horarios,
        cargas de trabajo u otras entidades relacionadas.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            bool: True si puede ser eliminado, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def validate_status_code_can_be_deactivated(self, entity_id: int) -> bool:
        """
        Valida si un código de estado puede ser desactivado.
        
        Verifica que la desactivación no afecte registros activos
        o procesos en curso.
        
        Args:
            entity_id: ID del código de estado
            
        Returns:
            bool: True si puede ser desactivado, False en caso contrario
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def validate_sort_order_uniqueness(
        self, 
        sort_order: int, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """
        Valida que un orden de clasificación sea único.
        
        Args:
            sort_order: Orden de clasificación a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)
            
        Returns:
            bool: True si el orden es único, False si ya existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass