# src/planificador/services/domain/client/client_domain_service.py

"""
Servicio de Dominio Cliente - Facade Principal

Este módulo implementa el facade principal para todas las operaciones del dominio cliente,
unificando el acceso a los diferentes módulos especializados y proporcionando una interfaz
cohesiva para la lógica de negocio relacionada con clientes.

Características principales:
- Facade unificado para todas las operaciones de cliente
- Integración con ClientRepositoryFacade para persistencia
- Gestión centralizada de sesiones de base de datos
- Logging estructurado con Loguru
- Manejo robusto de errores y excepciones
- Patrón de inyección de dependencias
- Operaciones asíncronas optimizadas
"""

from typing import Optional, List, Dict, Any, Union
from uuid import UUID

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from ....config.config import settings
from ....repositories.client.client_repository_facade import ClientRepositoryFacade
from ....schemas.client import (
    ClientCreate,
    ClientUpdate,
    Client,
    ClientStatsResponse,
    ClientFilter,
    ClientSort
)
from ....exceptions import (
    RepositoryError,
    ValidationError,
    BusinessLogicError
)

# Importar la interfaz principal
from .interfaces.client_domain_interface import IClientDomainService

# Importar todos los módulos especializados
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.date_operations import DateOperations
from .modules.validation_operations import ValidationOperations
from .modules.health_operations import HealthOperations


class ClientDomainService(IClientDomainService):
    """
    Servicio de Dominio Cliente - Facade Principal
    
    Proporciona una interfaz unificada para todas las operaciones del dominio cliente,
    delegando responsabilidades a módulos especializados mientras mantiene la cohesión
    de la lógica de negocio.
    
    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        repository_facade: Facade del repositorio cliente para persistencia
        crud: Operaciones CRUD básicas
        query: Operaciones de consulta básicas
        advanced_query: Operaciones de consulta avanzadas
        statistics: Operaciones de estadísticas y métricas
        relationships: Operaciones de relaciones entre entidades
        dates: Operaciones relacionadas con fechas y tiempo
        validation: Operaciones de validación de datos
        health: Operaciones de salud y diagnóstico
    """
    
    def __init__(self, session: AsyncSession):
        """
        Inicializa el servicio de dominio cliente.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy para operaciones de base de datos
        """
        self.session = session
        self._logger = logger.bind(service="ClientDomainService")
        
        # Inicializar el facade del repositorio
        self.repository_facade = ClientRepositoryFacade(session)
        
        # Inicializar todos los módulos especializados
        self.crud = CrudOperations(session, self.repository_facade)
        self.query = QueryOperations(session, self.repository_facade)
        self.advanced_query = AdvancedQueryOperations(session, self.repository_facade)
        self.statistics = StatisticsOperations(session, self.repository_facade)
        self.relationships = RelationshipOperations(session, self.repository_facade)
        self.dates = DateOperations(session, self.repository_facade)
        self.validation = ValidationOperations(session, self.repository_facade)
        self.health = HealthOperations(session, self.repository_facade)
        
        self._logger.info("ClientDomainService inicializado correctamente")
    
    # ==================== OPERACIONES CRUD ====================
    
    async def create_client(self, client_data: ClientCreate) -> Client:
        """Crea un nuevo cliente con validaciones de negocio."""
        return await self.crud.create_client(client_data)
    
    async def get_client_by_id(self, client_id: UUID) -> Optional[Client]:
        """Obtiene un cliente por su ID."""
        return await self.crud.get_client_by_id(client_id)
    
    async def update_client(self, client_id: UUID, client_data: ClientUpdate) -> Optional[Client]:
        """Actualiza un cliente existente con validaciones de negocio."""
        return await self.crud.update_client(client_id, client_data)
    
    async def delete_client(self, client_id: UUID) -> bool:
        """Elimina un cliente con validaciones de integridad."""
        return await self.crud.delete_client(client_id)
    
    async def bulk_create_clients(self, clients_data: List[ClientCreate]) -> List[Client]:
        """Crea múltiples clientes en una operación optimizada."""
        return await self.crud.bulk_create_clients(clients_data)
    
    # ==================== OPERACIONES DE CONSULTA ====================
    
    async def get_client_by_name(self, name: str) -> Optional[Client]:
        """Obtiene un cliente por su nombre."""
        return await self.query.get_client_by_name(name)
    
    async def get_client_by_email(self, email: str) -> Optional[Client]:
        """Obtiene un cliente por su email."""
        return await self.query.get_client_by_email(email)
    
    async def get_client_by_code(self, code: str) -> Optional[Client]:
        """Obtiene un cliente por su código."""
        return await self.query.get_client_by_code(code)
    
    async def get_clients_by_status(self, is_active: bool) -> List[Client]:
        """Obtiene clientes por su estado activo/inactivo."""
        return await self.query.get_clients_by_status(is_active)
    
    async def get_active_clients(self) -> List[Client]:
        """Obtiene todos los clientes activos."""
        return await self.query.get_active_clients()
    
    async def get_inactive_clients(self) -> List[Client]:
        """Obtiene todos los clientes inactivos."""
        return await self.query.get_inactive_clients()
    
    async def search_clients_basic(self, search_term: str) -> List[Client]:
        """Búsqueda básica de clientes por término."""
        return await self.query.search_clients_basic(search_term)
    
    async def client_exists(self, client_id: UUID) -> bool:
        """Verifica si un cliente existe."""
        return await self.query.client_exists(client_id)
    
    # ==================== OPERACIONES AVANZADAS ====================
    
    async def search_clients_advanced(
        self,
        filters: Optional[Dict[str, Any]] = None,
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        page: int = 1,
        page_size: int = 10
    ) -> Dict[str, Any]:
        """Búsqueda avanzada de clientes con filtros, ordenamiento y paginación."""
        return await self.advanced_query.search_clients_advanced(
            filters, sort_by, sort_order, page, page_size
        )
    
    async def get_clients_paginated(
        self,
        page: int = 1,
        page_size: int = 10,
        sort_by: Optional[str] = None
    ) -> Dict[str, Any]:
        """Obtiene clientes con paginación."""
        return await self.advanced_query.get_clients_paginated(page, page_size, sort_by)
    
    async def search_clients_fuzzy(self, search_term: str, threshold: float = 0.6) -> List[Client]:
        """Búsqueda difusa de clientes."""
        return await self.advanced_query.search_clients_fuzzy(search_term, threshold)
    
    # ==================== OPERACIONES DE ESTADÍSTICAS ====================
    
    async def get_client_statistics(self) -> ClientStatsResponse:
        """Obtiene estadísticas generales de clientes."""
        return await self.statistics.get_client_statistics()
    
    async def count_clients_by_status(self) -> Dict[str, int]:
        """Cuenta clientes por estado."""
        return await self.statistics.count_clients_by_status()
    
    async def get_client_growth_statistics(self, days: int = 30) -> Dict[str, Any]:
        """Obtiene estadísticas de crecimiento de clientes."""
        return await self.statistics.get_client_growth_statistics(days)
    
    async def get_client_activity_metrics(self) -> Dict[str, Any]:
        """Obtiene métricas de actividad de clientes."""
        return await self.statistics.get_client_activity_metrics()
    
    # ==================== OPERACIONES DE VALIDACIÓN ====================
    
    async def validate_client_creation(self, client_data: ClientCreate) -> Dict[str, Any]:
        """Valida datos para creación de cliente."""
        return await self.validation.validate_client_creation(client_data)
    
    async def validate_client_update(self, client_id: UUID, client_data: ClientUpdate) -> Dict[str, Any]:
        """Valida datos para actualización de cliente."""
        return await self.validation.validate_client_update(client_id, client_data)
    
    async def validate_business_rules(self, client_data: Union[ClientCreate, ClientUpdate]) -> Dict[str, Any]:
        """Valida reglas de negocio para cliente."""
        return await self.validation.validate_business_rules(client_data)
    
    async def validate_email_uniqueness(self, email: str, exclude_client_id: Optional[UUID] = None) -> bool:
        """Valida unicidad de email."""
        return await self.validation.validate_email_uniqueness(email, exclude_client_id)
    
    # ==================== OPERACIONES DE SALUD ====================
    
    async def check_service_health(self) -> Dict[str, Any]:
        """Verifica la salud del servicio de dominio."""
        return await self.health.check_service_health()
    
    async def check_database_connectivity(self) -> Dict[str, Any]:
        """Verifica la conectividad con la base de datos."""
        return await self.health.check_database_connectivity()
    
    async def generate_health_report(self) -> Dict[str, Any]:
        """Genera un reporte completo de salud del servicio."""
        return await self.health.generate_health_report()
    
    # ==================== MÉTODOS DE UTILIDAD ====================
    
    async def get_service_info(self) -> Dict[str, Any]:
        """Obtiene información general del servicio de dominio."""
        try:
            self._logger.info("Obteniendo información del servicio")
            
            return {
                "service_name": "ClientDomainService",
                "version": "1.0.0",
                "description": "Servicio de dominio para gestión integral de clientes",
                "modules": {
                    "crud": "Operaciones CRUD básicas",
                    "query": "Operaciones de consulta básicas",
                    "advanced_query": "Operaciones de consulta avanzadas",
                    "statistics": "Estadísticas y métricas",
                    "relationships": "Gestión de relaciones",
                    "dates": "Operaciones de fechas",
                    "validation": "Validaciones de negocio",
                    "health": "Monitoreo y diagnóstico"
                },
                "capabilities": [
                    "CRUD completo de clientes",
                    "Búsquedas básicas y avanzadas",
                    "Estadísticas y métricas",
                    "Validaciones de negocio",
                    "Monitoreo de salud",
                    "Operaciones en lote",
                    "Paginación optimizada"
                ],
                "status": "active"
            }
            
        except Exception as e:
            self._logger.error(f"Error obteniendo información del servicio: {e}")
            raise RepositoryError(
                message=f"Error obteniendo información del servicio: {e}",
                operation="get_service_info",
                entity_type="ClientDomainService",
                original_error=e
            )
    
    async def close(self):
        """Cierra recursos del servicio de dominio."""
        try:
            self._logger.info("Cerrando ClientDomainService")
            # Aquí se podrían cerrar recursos adicionales si fuera necesario
            # La sesión se gestiona externamente
            
        except Exception as e:
            self._logger.error(f"Error cerrando ClientDomainService: {e}")
            raise RepositoryError(
                message=f"Error cerrando servicio: {e}",
                operation="close",
                entity_type="ClientDomainService",
                original_error=e
            )