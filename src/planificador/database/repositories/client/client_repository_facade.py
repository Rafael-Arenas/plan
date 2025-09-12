"""
Facade del repositorio de clientes, ahora compatible con la nueva arquitectura modular.

Este facade actúa como un punto de entrada único para todas las operaciones
relacionadas con la entidad `Client`. Su propósito es abstraer la complejidad
interna de los diferentes módulos de repositorio y proporcionar una interfaz
coherente y simplificada.

Arquitectura y Principios:
- **Compatibilidad hacia atrás**: Mantiene los atributos y métodos legacy
  (`crud_ops`, `date_ops`, etc.) para no romper los tests existentes que
  dependen de la implementación anterior. Estos atributos ahora apuntan a los
  nuevos módulos optimizados.
- **Delegación de responsabilidades**: En lugar de contener la lógica de
  negocio, este facade delega las llamadas a los módulos especializados
  correspondientes (CRUD, consultas, validaciones, etc.).
- **Nuevos módulos con prefijo `_`**: Los nuevos módulos optimizados se
  inicializan con un prefijo `_` (ej: `_crud_operations`) para indicar que
  son la implementación principal y moderna.
- **Manejo de errores centralizado**: Aunque los módulos internos manejan sus
  propias excepciones, el facade puede actuar como una capa adicional de
- **Interfaz pública estable**: Los métodos públicos del facade mantienen su
  firma para garantizar que los servicios que lo consumen no necesiten
  modificaciones.

Módulos Delegados:
- `_crud_operations`: Operaciones básicas de Crear, Leer, Actualizar, Eliminar.
- `_query_operations`: Consultas comunes y optimizadas.
- `_advanced_query_operations`: Búsquedas complejas y con múltiples filtros.
- `_validation_operations`: Validaciones de negocio (ej: unicidad de campos).
- `_statistics_operations`: Cálculos de métricas y estadísticas.
- `_relationship_operations`: Gestión de relaciones (ej: proyectos de un cliente).
- `_date_operations`: Consultas y manipulaciones basadas en fechas.
- `_health_operations`: Verificación del estado de salud de los módulos.
"""

from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models import Client
from planificador.schemas.client import ClientCreate, ClientUpdate

# Nuevos módulos refactorizados
from .modules.advanced_query_operations import AdvancedQueryOperations
from .modules.crud_operations import CrudOperations 
from .modules.date_operations import DateOperations
from .modules.health_operations import HealthOperations
from .modules.query_operations import QueryOperations
from .modules.relationship_operations import RelationshipOperations
from .modules.statistics_operations import StatisticsOperations
from .modules.validation_operations import ValidationOperations


class ClientRepositoryFacade:
    """
    Facade que unifica el acceso a las operaciones del repositorio de clientes.

    Este facade implementa una arquitectura modular, delegando la ejecución de
    operaciones a módulos especializados. Para mantener la compatibilidad con
    los tests existentes, también expone los nombres de los módulos legacy,
    que ahora apuntan a las nuevas implementaciones.
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade y todos los módulos de operaciones.

        Args:
            session: La sesión de base de datos asíncrona.
        """
        self._session = session
        self._logger = logger

        # Inicialización de los nuevos módulos optimizados
        self._crud_operations = CrudOperations(session)
        self._query_operations = QueryOperations(session)
        self._advanced_query_operations = AdvancedQueryOperations(session)
        self._validation_operations = ValidationOperations(session)
        self._statistics_operations = StatisticsOperations(session)
        self._relationship_operations = RelationshipOperations(session)
        self._date_operations = DateOperations(session)
        self._health_operations = HealthOperations(
            session=session,
            modules={
                "crud": self._crud_operations,
                "query": self._query_operations,
                "advanced_query": self._advanced_query_operations,
                "validation": self._validation_operations,
                "statistics": self._statistics_operations,
                "relationship": self._relationship_operations,
                "date": self._date_operations,
            },
        )

        # --- Módulos Legacy (para compatibilidad con tests) ---
        # Estos atributos apuntan a los nuevos módulos para que los tests
        # que acceden a `facade.crud_ops` sigan funcionando sin cambios.
        self.crud_ops = self._crud_operations
        self.query_builder = self._query_operations
        self.validator = self._validation_operations
        self.statistics = self._statistics_operations
        self.relationship_manager = self._relationship_operations
        self.date_ops = self._date_operations
        # El exception_handler se elimina, ya que ahora está integrado
        # en cada módulo.

    # ==========================================================================
    # MÉTODOS DELEGADOS A LOS NUEVOS MÓDULOS
    # ==========================================================================

    # --- CRUD Operations ---
    async def create_client(self, client_data: ClientCreate) -> Client:
        return await self._crud_operations.create_client(client_data.model_dump())

    async def get_client_by_id(self, client_id: int) -> Client | None:
        return await self._query_operations.get_client_by_id(client_id)

    async def update_client(
        self, client_id: int, client_data: ClientUpdate
    ) -> Client | None:
        return await self._crud_operations.update_client(client_id, client_data)

    async def delete_client(self, client_id: int) -> bool:
        return await self._crud_operations.delete_client(client_id)

    # --- Query Operations ---
    async def get_client_by_name(self, name: str) -> Client | None:
        return await self._query_operations.get_client_by_name(name)

    async def get_client_by_code(self, code: str) -> Client | None:
        return await self._query_operations.get_client_by_code(code)

    async def get_active_clients(self) -> list[Client]:
        return await self._advanced_query_operations.get_clients_by_filters(
            filters={"is_active": True}, limit=1000
        )

    async def get_client_by_email(self, email: str) -> Client | None:
        return await self._query_operations.get_client_by_email(email)

    # --- Advanced Query Operations ---
    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        return await self._advanced_query_operations.search_clients_by_name(
            name_pattern
        )

    async def search_with_advanced_filters(
        self, **filters: Any
    ) -> list[Client]:
        return await self._advanced_query_operations.search_with_advanced_filters(
            **filters
        )

    # --- Validation Operations ---
    async def validate_client_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        return await self._validation_operations.validate_name_unique(
            name, exclude_id
        )

    async def validate_client_code_unique(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        return await self._validation_operations.validate_code_unique(
            code, exclude_id
        )

    # --- Statistics Operations ---
    async def get_client_statistics(self) -> dict[str, Any]:
        return await self._statistics_operations.get_client_statistics()

    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        return (
            await self._statistics_operations.get_comprehensive_dashboard_metrics()
        )

    async def get_client_segmentation_analysis(self) -> dict[str, Any]:
        return (
            await self._statistics_operations.get_client_segmentation_analysis()
        )

    async def get_client_value_analysis(self) -> dict[str, Any]:
        return await self._statistics_operations.get_client_value_analysis()

    async def get_client_retention_analysis(self) -> dict[str, Any]:
        return await self._statistics_operations.get_client_retention_analysis()

    # --- Relationship Operations ---
    async def transfer_projects_to_client(
        self, source_client_id: int, target_client_id: int
    ) -> bool:
        return (
            await self._relationship_operations.transfer_projects_to_client(
                source_client_id, target_client_id
            )
        )

    async def get_client_projects(self, client_id: int) -> list[dict[str, Any]]:
        return await self._relationship_operations.get_client_projects(client_id)

    async def get_client_project_count(self, client_id: int) -> int:
        return await self._relationship_operations.get_client_project_count(
            client_id
        )

    # --- Date Operations ---
    async def get_clients_created_current_week(self) -> list[Client]:
        return await self._date_operations.get_clients_created_current_week()

    async def get_clients_created_current_month(self) -> list[Client]:
        return await self._date_operations.get_clients_created_current_month()

    async def get_clients_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[Client]:
        return await self._date_operations.get_clients_by_date_range(
            start_date, end_date
        )

    async def get_clients_by_age_range(
        self, min_age_days: int, max_age_days: int
    ) -> list[Client]:
        return await self._date_operations.get_clients_by_age_range(
            min_age_days, max_age_days
        )

    # --- Health Operations ---
    async def health_check(self) -> dict[str, Any]:
        return await self._health_operations.health_check()

    # ==========================================================================
    # MÉTODOS LEGACY (MANTENIDOS PARA COMPATIBILIDAD)
    # ==========================================================================
    # Estos métodos se mantienen por si alguna parte del código los llama
    # directamente, aunque la funcionalidad ya está cubierta por los métodos
    # delegados. En una futura refactorización, podrían ser eliminados.

    async def create_client_with_date_validation(
        self, client_data: ClientCreate
    ) -> Client:
        """Alias de create_client para compatibilidad."""
        return await self.create_client(client_data)

    async def get_clients_created_in_date_range(
        self, start_date: str, end_date: str
    ) -> list[Client]:
        """Alias de get_clients_by_date_range para compatibilidad."""
        start = date.fromisoformat(start_date)
        end = date.fromisoformat(end_date)
        return await self.get_clients_by_date_range(start, end)
