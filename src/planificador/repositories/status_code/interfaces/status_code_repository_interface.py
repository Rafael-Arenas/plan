# src/planificador/repositories/status_code/interfaces/status_code_repository_interface.py

"""
Interfaz principal para el repositorio de códigos de estado.

Define el contrato completo para todas las operaciones disponibles
en el repositorio de códigos de estado, incluyendo CRUD básico,
búsquedas especializadas, validaciones y estadísticas.
"""

from abc import ABC, abstractmethod
from typing import List, Optional, Dict, Any

from planificador.models.status_code import StatusCode


class IStatusCodeRepository(ABC):
    """
    Interfaz principal para el repositorio de códigos de estado.
    
    Define todos los métodos disponibles para gestionar códigos de estado,
    incluyendo operaciones CRUD, búsquedas especializadas, validaciones,
    gestión de ordenamiento y análisis estadístico.
    """

    # ==========================================
    # OPERACIONES CRUD BÁSICAS
    # ==========================================

    @abstractmethod
    async def create(self, entity_data: Dict[str, Any]) -> StatusCode:
        """Crea un nuevo código de estado."""
        pass

    @abstractmethod
    async def update(self, entity_id: int, **update_data) -> StatusCode:
        """Actualiza un código de estado existente."""
        pass

    @abstractmethod
    async def get_by_id(self, entity_id: int) -> Optional[StatusCode]:
        """Obtiene código de estado por ID."""
        pass

    @abstractmethod
    async def delete(self, entity_id: int) -> bool:
        """Elimina un código de estado."""
        pass

    @abstractmethod
    async def get_all(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado."""
        pass

    @abstractmethod
    async def exists(self, entity_id: int) -> bool:
        """Verifica si existe un código de estado por ID."""
        pass

    # ==========================================
    # MÉTODOS DE BÚSQUEDA ESPECÍFICOS
    # ==========================================

    @abstractmethod
    async def get_by_code(self, code: str) -> Optional[StatusCode]:
        """Busca un código de estado por su código único."""
        pass

    @abstractmethod
    async def search_by_name(self, search_term: str) -> List[StatusCode]:
        """Busca códigos de estado cuyo nombre contenga el término de búsqueda."""
        pass

    @abstractmethod
    async def get_active_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado activos ordenados por sort_order."""
        pass

    @abstractmethod
    async def get_billable_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado facturables y activos."""
        pass

    @abstractmethod
    async def get_productive_status_codes(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado productivos y activos."""
        pass

    # ==========================================
    # MÉTODOS DE BÚSQUEDA POR CARACTERÍSTICAS
    # ==========================================

    @abstractmethod
    async def get_status_codes_requiring_approval(self) -> List[StatusCode]:
        """Obtiene todos los códigos de estado que requieren aprobación y están activos."""
        pass

    # ==========================================
    # MÉTODOS DE FILTRADO AVANZADO
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
        """Filtra códigos de estado por múltiples criterios."""
        pass

    # ==========================================
    # MÉTODOS DE GESTIÓN DE ORDENAMIENTO
    # ==========================================

    @abstractmethod
    async def get_max_sort_order(self) -> int:
        """Obtiene el valor máximo de sort_order para asignar a nuevos códigos."""
        pass

    @abstractmethod
    async def reorder_status_codes(self, code_order_mapping: Dict[str, int]) -> bool:
        """Reordena múltiples códigos de estado según un mapeo código -> orden."""
        pass

    # ==========================================
    # MÉTODOS DE ESTADÍSTICAS Y ANÁLISIS
    # ==========================================

    @abstractmethod
    async def get_usage_statistics(self) -> Dict[str, Any]:
        """Obtiene estadísticas de uso de los códigos de estado."""
        pass

    # ==========================================
    # MÉTODOS DE VALIDACIÓN
    # ==========================================

    @abstractmethod
    async def validate_code_uniqueness(
        self, 
        code: str, 
        exclude_id: Optional[int] = None
    ) -> bool:
        """Valida que un código sea único en el sistema."""
        pass