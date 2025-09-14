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

from datetime import date, datetime
from typing import Any

from loguru import logger
from sqlalchemy.ext.asyncio import AsyncSession

from planificador.models import Client
from planificador.schemas.client import ClientCreate, ClientUpdate

# Módulos 
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

        # Inicialización de los módulos
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
        # Estos atributos apuntan a los módulos para que los tests
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
    # MÉTODOS DELEGADOS A LOS MÓDULOS
    # ==========================================================================

    # --- Advanced Query Operations ---
    async def search_clients_by_text(
        self, 
        search_text: str, 
        fields: list[str] | None = None,
        limit: int = 50,
        offset: int = 0
    ) -> list[Client]:
        return await self._advanced_query_operations.search_clients_by_text(
            search_text, fields, limit, offset
        )

    async def get_clients_by_filters(
        self, 
        filters: dict[str, Any],
        limit: int = 50,
        offset: int = 0,
        order_by: str | None = None
    ) -> list[Client]:
        return await self._advanced_query_operations.get_clients_by_filters(
            filters, limit, offset, order_by
        )

    async def get_clients_with_relationships(
        self, 
        include_projects: bool = False,
        include_contacts: bool = False,
        limit: int = 50,
        offset: int = 0
    ) -> list[Client]:
        return await self._advanced_query_operations.get_clients_with_relationships(
            include_projects, include_contacts, limit, offset
        )

    async def count_clients_by_filters(self, filters: dict[str, Any]) -> int:
        return await self._advanced_query_operations.count_clients_by_filters(filters)

    async def search_clients_fuzzy(
        self, 
        search_term: str, 
        similarity_threshold: float = 0.3
    ) -> list[Client]:
        return await self._advanced_query_operations.search_clients_fuzzy(
            search_term, similarity_threshold
        )


    # --- CRUD Operations ---
    async def create_client(self, client_data: ClientCreate) -> Client:
        return await self._crud_operations.create_client(client_data.model_dump())

    async def update_client(
        self, client_id: int, client_data: ClientUpdate
    ) -> Client | None:
        return await self._crud_operations.update_client(client_id, client_data)

    async def delete_client(self, client_id: int) -> bool:
        return await self._crud_operations.delete_client(client_id)


    # --- Date Operations ---
    async def get_clients_created_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Client]:
        return await self._date_operations.get_clients_created_in_date_range(
            start_date, end_date
        )

    async def get_clients_updated_in_date_range(
        self, start_date: datetime, end_date: datetime
    ) -> list[Client]:
        return await self._date_operations.get_clients_updated_in_date_range(
            start_date, end_date
        )


    # --- Health Operations ---
    async def health_check(self) -> dict[str, Any]:
        return await self._health_operations.health_check()

    async def get_module_info(self) -> dict[str, Any]:
        return await self._health_operations.get_module_info()

    # --- Query Operations ---
    async def get_client_by_id(self, client_id: int) -> Client | None:
        return await self._query_operations.get_client_by_id(client_id)

    async def get_client_by_name(self, name: str) -> Client | None:
        return await self._query_operations.get_client_by_name(name)

    async def get_client_by_code(self, code: str) -> Client | None:
        return await self._query_operations.get_client_by_code(code)

    async def get_client_by_email(self, email: str) -> Client | None:
        return await self._query_operations.get_client_by_email(email)

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        return await self._query_operations.search_clients_by_name(name_pattern)

    async def get_all_clients(self, limit: int | None = None, offset: int = 0) -> list[Client]:
        return await self._query_operations.get_all_clients(limit, offset)
    
    # --- Relationship Operations ---
    async def transfer_projects_to_client(self, from_client_id: int, to_client_id: int) -> bool:
        return await self._relationship_operations.transfer_projects_to_client(from_client_id, to_client_id)

    async def get_client_projects(self, client_id: int) -> list[Any]:
        return await self._relationship_operations.get_client_projects(client_id)

    async def get_client_project_count(self, client_id: int) -> int:
        return await self._relationship_operations.get_client_project_count(client_id)

    # --- Statistics Operations ---
    async def get_client_statistics(self) -> dict[str, Any]:
        return await self._statistics_operations.get_client_statistics()

    async def get_client_counts_by_status(self) -> dict[str, int]:
        return await self._statistics_operations.get_client_counts_by_status()

    async def get_client_count(self) -> int:
        return await self._statistics_operations.get_client_count()

    async def get_client_stats_by_id(self, client_id: int) -> dict[str, Any]:
        return await self._statistics_operations.get_client_stats_by_id(client_id)

    async def get_client_creation_trends(self, days: int = 30, group_by: str = "day") -> list[dict[str, Any]]:
        return await self._statistics_operations.get_client_creation_trends(days, group_by)

    async def get_clients_by_project_count(self, limit: int = 10) -> list[dict[str, Any]]:
        return await self._statistics_operations.get_clients_by_project_count(limit)

    def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        return self._statistics_operations.get_comprehensive_dashboard_metrics()

    # --- Validation Operations ---

    async def validate_unique_fields(
        self, 
        client_data: dict[str, Any], 
        exclude_id: int | None = None
    ) -> None:
        return await self._validation_operations.validate_unique_fields(
            client_data, exclude_id
        )

    def validate_email_format(self, email: str) -> None:
        return self._validation_operations.validate_email_format(email)

    def validate_phone_format(self, phone: str) -> None:
        return self._validation_operations.validate_phone_format(phone)

    def validate_required_fields(self, client_data: dict[str, Any]) -> None:
        return self._validation_operations.validate_required_fields(client_data)

    def validate_field_lengths(self, client_data: dict[str, Any]) -> None:
        return self._validation_operations.validate_field_lengths(client_data)

    async def validate_client_data(
        self, 
        client_data: dict[str, Any], 
        exclude_id: int | None = None,
        validate_uniqueness: bool = True
    ) -> None:
        return await self._validation_operations.validate_client_data(
            client_data, exclude_id, validate_uniqueness
        )

    def validate_code_format(self, code: str) -> None:
        return self._validation_operations.validate_code_format(code)

    async def validate_business_rules(
        self, 
        client_data: dict[str, Any], 
        exclude_id: int | None = None
    ) -> None:
        return await self._validation_operations.validate_business_rules(
            client_data, exclude_id
        )

    async def validate_client_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        return await self._validation_operations.validate_client_name_unique(
            name, exclude_id
        )

    async def validate_client_code_unique(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        return await self._validation_operations.validate_client_code_unique(
            code, exclude_id
        )

    async def validate_client_deletion(self, client_id: int) -> bool:
        return await self._validation_operations.validate_client_deletion(client_id)
        
