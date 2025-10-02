# -*- coding: utf-8 -*-
"""
Interfaz del Servicio de Dominio Cliente

Define el contrato principal para el servicio de dominio de clientes,
especificando todas las operaciones disponibles para la gestión de clientes.
"""

from abc import ABC, abstractmethod
from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from planificador.schemas.client import (
    ClientCreate,
    ClientUpdate,
    Client,
    ClientStatsResponse,
    ClientFilter
)


class IClientDomainService(ABC):
    """
    Interfaz para el servicio de dominio de clientes.
    
    Define el contrato para todas las operaciones de negocio relacionadas
    con la gestión de clientes, incluyendo CRUD, consultas, validaciones,
    estadísticas y operaciones de salud del servicio.
    """

    # ========== Operaciones CRUD ==========
    
    @abstractmethod
    async def create_client(self, client_data: ClientCreate) -> Client:
        """Crea un nuevo cliente."""
        pass

    @abstractmethod
    async def get_client_by_id(self, client_id: UUID) -> Optional[Client]:
        """Obtiene un cliente por su ID."""
        pass

    @abstractmethod
    async def update_client(self, client_id: UUID, client_data: ClientUpdate) -> Optional[Client]:
        """Actualiza un cliente existente."""
        pass

    @abstractmethod
    async def delete_client(self, client_id: UUID) -> bool:
        """Elimina un cliente."""
        pass

    @abstractmethod
    async def bulk_create_clients(self, clients_data: List[ClientCreate]) -> List[Client]:
        """Crea múltiples clientes en lote."""
        pass

    # ========== Operaciones de Consulta ==========
    
    @abstractmethod
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """Obtiene un cliente por su nombre."""
        pass

    @abstractmethod
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """Obtiene un cliente por su email."""
        pass

    @abstractmethod
    async def get_client_by_code(self, code: str) -> Optional[Client]:
        """Obtiene un cliente por su código."""
        pass

    @abstractmethod
    async def get_clients_by_status(self, is_active: bool) -> List[Client]:
        """Obtiene clientes por su estado activo/inactivo."""
        pass

    @abstractmethod
    async def get_active_clients(self) -> List[Client]:
        """Obtiene todos los clientes activos."""
        pass

    @abstractmethod
    async def get_inactive_clients(self) -> List[Client]:
        """Obtiene todos los clientes inactivos."""
        pass

    @abstractmethod
    async def search_clients_basic(self, search_term: str) -> List[Client]:
        """Realiza una búsqueda básica de clientes."""
        pass

    @abstractmethod
    async def client_exists(self, client_id: UUID) -> bool:
        """Verifica si un cliente existe."""
        pass

    # ========== Operaciones de Consulta Avanzada ==========
    
    @abstractmethod
    async def search_clients_advanced(
        self,
        filters: Dict[str, Any],
        pagination: Dict[str, Any],
        sort_params: List[Dict[str, Any]]
    ) -> Dict[str, Any]:
        """Realiza una búsqueda avanzada de clientes con filtros, paginación y ordenamiento."""
        pass

    @abstractmethod
    async def get_clients_paginated(
        self,
        page: int,
        page_size: int,
        filters: Optional[Dict[str, Any]] = None
    ) -> Dict[str, Any]:
        """Obtiene clientes con paginación."""
        pass

    @abstractmethod
    async def search_clients_fuzzy(self, search_term: str, threshold: float = 0.6) -> List[Client]:
        """Realiza una búsqueda difusa de clientes."""
        pass

    # ========== Operaciones de Estadísticas ==========
    
    @abstractmethod
    async def get_client_statistics(self) -> ClientStatsResponse:
        """Obtiene estadísticas generales de clientes."""
        pass

    @abstractmethod
    async def count_clients_by_status(self) -> Dict[str, int]:
        """Cuenta clientes por estado."""
        pass

    @abstractmethod
    async def get_client_growth_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de crecimiento de clientes."""
        pass

    @abstractmethod
    async def get_client_activity_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de actividad de clientes."""
        pass

    # ========== Operaciones de Validación ==========
    
    @abstractmethod
    async def validate_client_creation(self, client_data: ClientCreate) -> Dict[str, Any]:
        """Valida datos para creación de cliente."""
        pass

    @abstractmethod
    async def validate_client_update(self, client_id: UUID, client_data: ClientUpdate) -> Dict[str, Any]:
        """Valida datos para actualización de cliente."""
        pass

    @abstractmethod
    async def validate_business_rules(self, client_data: Union[ClientCreate, ClientUpdate]) -> Dict[str, Any]:
        """Valida reglas de negocio para clientes."""
        pass

    @abstractmethod
    async def validate_email_uniqueness(self, email: str, exclude_client_id: Optional[UUID] = None) -> bool:
        """Valida que el email sea único."""
        pass

    # ========== Operaciones de Salud del Servicio ==========
    
    @abstractmethod
    async def check_service_health(self) -> Dict[str, Any]:
        """Verifica la salud del servicio."""
        pass

    @abstractmethod
    async def check_database_connectivity(self) -> Dict[str, Any]:
        """Verifica la conectividad con la base de datos."""
        pass

    @abstractmethod
    async def generate_health_report(self) -> Dict[str, Any]:
        """Genera un reporte completo de salud del servicio."""
        pass

    # ========== Operaciones de Información del Servicio ==========
    
    @abstractmethod
    async def get_service_info(self) -> Dict[str, Any]:
        """Obtiene información del servicio."""
        pass

    # ========== Gestión de Recursos ==========
    
    @abstractmethod
    async def close(self):
        """Cierra recursos del servicio."""
        pass