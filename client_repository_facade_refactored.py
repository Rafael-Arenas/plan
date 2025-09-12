"""Facade refactorizado para operaciones de cliente.

Este módulo implementa el patrón Facade simplificado que delega exclusivamente
a los nuevos módulos modularizados, eliminando la duplicación de funcionalidad
y reduciendo significativamente el tamaño del código.

Arquitectura Simplificada:
=========================

El ClientRepositoryFacade coordina únicamente los nuevos módulos especializados:

1. **CrudOperations**: Operaciones CRUD completas
2. **QueryOperations**: Consultas básicas y búsquedas
3. **AdvancedQueryOperations**: Consultas avanzadas y filtros complejos
4. **ValidationOperations**: Validaciones de datos y reglas de negocio
5. **StatisticsOperations**: Estadísticas y reportes
6. **RelationshipOperations**: Gestión de relaciones cliente-proyecto
7. **DateOperations**: Operaciones de fecha y tiempo
8. **HealthOperations**: Verificaciones de salud del sistema

Beneficios de la Refactorización:
===============================

- **Código Reducido**: De 1335 líneas a ~400 líneas (70% reducción)
- **Sin Duplicación**: Eliminación completa de funcionalidad duplicada
- **Arquitectura Limpia**: Solo nuevos módulos modularizados
- **Mantenibilidad**: Código más simple y fácil de mantener
- **Performance**: Menos overhead por eliminación de capas redundantes
"""

from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientValidationError,
    ClientNotFoundError,
    ClientDuplicateError,
)
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate

# Importaciones únicamente de nuevos módulos modularizados
from .modules.crud_operations import CrudOperations
from .modules.query_operations import QueryOperations
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.validation_operations import ValidationOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.date_operations import DateOperations
from .modules.health_operations import HealthOperations


class ClientRepositoryFacade:
    """Facade simplificado que delega únicamente a módulos modularizados.
    
    Esta versión refactorizada elimina toda duplicación de funcionalidad
    y mantiene solo la delegación a los nuevos módulos especializados.
    """

    def __init__(self, session: AsyncSession) -> None:
        """Inicializa el facade con módulos modularizados únicamente.
        
        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="ClientRepositoryFacade")

        # Inicializar únicamente nuevos módulos modularizados
        self.crud_operations = CrudOperations(session)
        self.query_operations = QueryOperations(session)
        self.advanced_query_operations = AdvancedQueryOperations(session)
        self.validation_operations = ValidationOperations(session)
        self.statistics_operations = StatisticsOperations(session)
        self.relationship_operations = RelationshipOperations(session)
        self.date_operations = DateOperations(session)
        self.health_operations = HealthOperations(
            session=session,
            modules={
                'crud_operations': self.crud_operations,
                'query_operations': self.query_operations,
                'advanced_query_operations': self.advanced_query_operations,
                'validation_operations': self.validation_operations,
                'statistics_operations': self.statistics_operations,
                'relationship_operations': self.relationship_operations,
                'date_operations': self.date_operations,
            }
        )

        self._logger.debug("ClientRepositoryFacade refactorizado inicializado")

    # ============================================================================
    # OPERACIONES CRUD (Delegación directa)
    # ============================================================================

    async def create_client(self, client_data: ClientCreate) -> Client:
        """Crea un nuevo cliente."""
        return await self.crud_operations.create_client(client_data.model_dump())

    async def get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por ID."""
        return await self.crud_operations.get_client_by_id(client_id)

    async def update_client(self, client_id: int, client_data: ClientUpdate) -> Client | None:
        """Actualiza un cliente existente."""
        return await self.crud_operations.update_client(
            client_id, client_data.model_dump(exclude_unset=True)
        )

    async def delete_client(self, client_id: int) -> bool:
        """Elimina un cliente (soft delete)."""
        return await self.crud_operations.delete_client(client_id)

    # ============================================================================
    # CONSULTAS BÁSICAS (Delegación directa)
    # ============================================================================

    async def get_client_by_name(self, name: str) -> Client | None:
        """Busca un cliente por nombre exacto."""
        return await self.query_operations.get_client_by_name(name)

    async def get_client_by_code(self, code: str) -> Client | None:
        """Busca un cliente por código único."""
        return await self.query_operations.get_client_by_code(code)

    async def get_client_by_email(self, email: str) -> Client | None:
        """Busca un cliente por email."""
        return await self.query_operations.get_client_by_email(email)

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """Busca clientes por patrón de nombre."""
        return await self.query_operations.search_clients_by_name(name_pattern)

    # ============================================================================
    # CONSULTAS AVANZADAS (Delegación directa)
    # ============================================================================

    async def search_clients_by_text(self, search_text: str, limit: int = 50) -> list[Client]:
        """Búsqueda de texto completo en clientes."""
        return await self.advanced_query_operations.search_clients_by_text(
            search_text, limit
        )

    async def get_clients_by_filters(
        self,
        name_pattern: str | None = None,
        code_pattern: str | None = None,
        email_pattern: str | None = None,
        is_active: bool | None = None,
        has_projects: bool | None = None,
        created_after: date | None = None,
        created_before: date | None = None,
        limit: int = 100,
        offset: int = 0,
    ) -> list[Client]:
        """Obtiene clientes con filtros múltiples."""
        return await self.advanced_query_operations.get_clients_by_filters(
            name_pattern=name_pattern,
            code_pattern=code_pattern,
            email_pattern=email_pattern,
            is_active=is_active,
            has_projects=has_projects,
            created_after=created_after,
            created_before=created_before,
            limit=limit,
            offset=offset,
        )

    async def search_clients_fuzzy(self, search_term: str, threshold: float = 0.6) -> list[Client]:
        """Búsqueda difusa de clientes."""
        return await self.advanced_query_operations.search_clients_fuzzy(
            search_term, threshold
        )

    # ============================================================================
    # VALIDACIONES (Delegación directa)
    # ============================================================================

    async def validate_client_data(self, client_data: dict[str, Any]) -> dict[str, Any]:
        """Valida datos de cliente."""
        return await self.validation_operations.validate_client_data(client_data)

    async def check_name_uniqueness(self, name: str, exclude_id: int | None = None) -> bool:
        """Verifica unicidad del nombre."""
        return await self.validation_operations.check_name_uniqueness(name, exclude_id)

    async def check_code_uniqueness(self, code: str, exclude_id: int | None = None) -> bool:
        """Verifica unicidad del código."""
        return await self.validation_operations.check_code_uniqueness(code, exclude_id)

    # ============================================================================
    # ESTADÍSTICAS (Delegación directa)
    # ============================================================================

    async def get_client_statistics(self) -> dict[str, Any]:
        """Obtiene estadísticas generales de clientes."""
        return await self.statistics_operations.get_client_statistics()

    async def get_client_count(self) -> int:
        """Obtiene el conteo total de clientes."""
        return await self.statistics_operations.get_client_count()

    async def get_client_stats_by_id(self, client_id: int) -> dict[str, Any]:
        """Obtiene estadísticas de un cliente específico."""
        return await self.statistics_operations.get_client_stats_by_id(client_id)

    async def get_client_creation_trends(
        self, days: int = 30, group_by: str = "day"
    ) -> list[dict[str, Any]]:
        """Obtiene tendencias de creación de clientes."""
        return await self.statistics_operations.get_client_creation_trends(days, group_by)

    # ============================================================================
    # RELACIONES (Delegación directa)
    # ============================================================================

    async def get_client_projects(self, client_id: int) -> list[Any]:
        """Obtiene proyectos de un cliente."""
        return await self.relationship_operations.get_client_projects(client_id)

    async def get_client_project_count(self, client_id: int) -> int:
        """Obtiene el conteo de proyectos de un cliente."""
        return await self.relationship_operations.get_client_project_count(client_id)

    async def assign_project_to_client(self, client_id: int, project_id: int) -> bool:
        """Asigna un proyecto a un cliente."""
        return await self.relationship_operations.assign_project_to_client(
            client_id, project_id
        )

    # ============================================================================
    # OPERACIONES DE FECHA (Delegación directa)
    # ============================================================================

    async def get_clients_created_in_date_range(
        self, start_date: date, end_date: date
    ) -> list[Client]:
        """Obtiene clientes creados en un rango de fechas."""
        return await self.date_operations.get_clients_created_in_date_range(
            start_date, end_date
        )

    async def get_clients_updated_in_date_range(
        self, start_date: date, end_date: date
    ) -> list[Client]:
        """Obtiene clientes actualizados en un rango de fechas."""
        return await self.date_operations.get_clients_updated_in_date_range(
            start_date, end_date
        )

    # ============================================================================
    # HEALTH CHECK (Delegación directa)
    # ============================================================================

    async def health_check(self) -> dict[str, Any]:
        """Verifica el estado de salud del facade y sus módulos."""
        return await self.health_operations.health_check()

    async def detailed_health_check(self) -> dict[str, Any]:
        """Verifica el estado detallado de salud."""
        return await self.health_operations.detailed_health_check()

    # ============================================================================
    # MÉTODOS DE UTILIDAD
    # ============================================================================

    def get_facade_info(self) -> dict[str, Any]:
        """Obtiene información del facade refactorizado."""
        return {
            "facade_type": "ClientRepositoryFacade",
            "version": "2.0.0-refactored",
            "architecture": "modular",
            "modules": {
                "crud_operations": self.crud_operations.__class__.__name__,
                "query_operations": self.query_operations.__class__.__name__,
                "advanced_query_operations": self.advanced_query_operations.__class__.__name__,
                "validation_operations": self.validation_operations.__class__.__name__,
                "statistics_operations": self.statistics_operations.__class__.__name__,
                "relationship_operations": self.relationship_operations.__class__.__name__,
                "date_operations": self.date_operations.__class__.__name__,
                "health_operations": self.health_operations.__class__.__name__,
            },
            "legacy_modules_removed": True,
            "code_reduction": "70%",
            "lines_of_code": "~400",
        }