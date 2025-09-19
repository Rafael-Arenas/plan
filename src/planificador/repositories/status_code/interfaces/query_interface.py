# src/planificador/repositories/status_code/interfaces/query_interface.py

"""
Interfaz para operaciones de consulta de códigos de estado.

Define los métodos de búsqueda y consulta especializados para la entidad
StatusCode, incluyendo filtros por características y búsquedas avanzadas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from planificador.models.status_code import StatusCode


class IStatusCodeQueryOperations(ABC):
    """
    Interfaz abstracta para operaciones de consulta de códigos de estado.
    
    Define los métodos de búsqueda y consulta que debe implementar cualquier
    módulo que maneje operaciones de recuperación y filtrado de códigos de estado.
    
    Métodos incluyen búsquedas por código único, nombre, características
    booleanas (activo, facturable, productivo) y filtros combinados.
    """

    # ==========================================
    # BÚSQUEDAS POR IDENTIFICADORES ÚNICOS
    # ==========================================

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[StatusCode]:
        """
        Busca un código de estado por su código único.
        
        Args:
            code: Código único del status code
            
        Returns:
            Optional[StatusCode]: El código de estado o None si no existe
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # BÚSQUEDAS POR TEXTO
    # ==========================================

    @abstractmethod
    async def search_by_name(self, search_term: str) -> List[StatusCode]:
        """
        Busca códigos de estado cuyo nombre contenga el término de búsqueda.
        
        Args:
            search_term: Término a buscar en el nombre
            
        Returns:
            List[StatusCode]: Lista de códigos de estado que coinciden
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # BÚSQUEDAS POR CARACTERÍSTICAS BOOLEANAS
    # ==========================================

    @abstractmethod
    async def get_active_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado activos ordenados por sort_order.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado activos
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_billable_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado facturables y activos.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado facturables
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_productive_status_codes(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado productivos y activos.
        
        Returns:
            List[StatusCode]: Lista de códigos de estado productivos
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    @abstractmethod
    async def get_status_codes_requiring_approval(self) -> List[StatusCode]:
        """
        Obtiene todos los códigos de estado que requieren aprobación y están activos.
        
        Returns:
            List[StatusCode]: Lista de códigos que requieren aprobación
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass

    # ==========================================
    # FILTRADO AVANZADO Y COMBINADO
    # ==========================================

    @abstractmethod
    async def filter_by_criteria(
        self,
        is_active: Optional[bool] = None,
        is_billable: Optional[bool] = None,
        is_productive: Optional[bool] = None,
        requires_approval: Optional[bool] = None,
        search_term: Optional[str] = None
    ) -> List[StatusCode]:
        """
        Filtra códigos de estado por múltiples criterios.
        
        Args:
            is_active: Filtrar por estado activo/inactivo
            is_billable: Filtrar por códigos facturables
            is_productive: Filtrar por códigos productivos
            requires_approval: Filtrar por códigos que requieren aprobación
            search_term: Término de búsqueda en nombre o descripción
            
        Returns:
            List[StatusCode]: Lista de códigos que cumplen los criterios
            
        Raises:
            RepositoryError: Si ocurre un error en la base de datos
        """
        pass