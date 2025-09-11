"""Facade principal para operaciones de cliente.

Este módulo implementa el patrón Facade para unificar todas las operaciones
relacionadas con clientes, proporcionando una interfaz simplificada que
encapsula la complejidad de múltiples módulos especializados.

Arquitectura del Patrón Facade:
===============================

El ClientRepositoryFacade coordina los siguientes módulos especializados:

1. **ClientCRUDOperations**: Operaciones CRUD básicas y avanzadas
   - Creación, lectura, actualización y eliminación de clientes
   - Validaciones de integridad de datos
   - Transacciones seguras

2. **ClientQueryBuilder**: Consultas especializadas y búsquedas
   - Búsquedas por nombre, código, estado
   - Filtros avanzados y combinados
   - Optimización de consultas SQL

3. **ClientValidator**: Validaciones de datos y reglas de negocio
   - Validación de unicidad de nombres y códigos
   - Reglas de negocio específicas del dominio
   - Validaciones de formato y estructura

4. **ClientStatistics**: Estadísticas y reportes
   - Conteos por estado y categoría
   - Métricas de rendimiento
   - Reportes agregados

5. **ClientDateOperations**: Operaciones de fecha y tiempo
   - Manejo de zonas horarias con Pendulum
   - Cálculos de períodos y duraciones
   - Formateo y conversión de fechas

6. **ClientExceptionHandler**: Manejo centralizado de excepciones
   - Conversión de errores SQLAlchemy
   - Logging estructurado de errores
   - Contexto enriquecido para debugging

7. **ClientRelationshipManager**: Gestión de relaciones cliente-proyecto
   - Asignación y transferencia de proyectos
   - Consultas de relaciones
   - Mantenimiento de integridad referencial

Características del Patrón:
===========================

- **Interfaz Unificada**: Un solo punto de entrada para todas las operaciones
- **Encapsulación**: Oculta la complejidad de múltiples subsistemas
- **Desacoplamiento**: Los clientes no dependen de módulos específicos
- **Manejo Consistente**: Excepciones y logging uniformes
- **Extensibilidad**: Fácil adición de nuevos módulos especializados
- **Testabilidad**: Cada módulo puede ser probado independientemente

Beneficios de la Implementación:
===============================

1. **Simplicidad**: Interfaz clara y fácil de usar
2. **Mantenibilidad**: Cambios internos no afectan a los clientes
3. **Reutilización**: Módulos especializados reutilizables
4. **Robustez**: Manejo centralizado de errores
5. **Performance**: Operaciones optimizadas y asíncronas
6. **Monitoreo**: Health checks integrados para todos los módulos

Ejemplo de uso:
    ```python
    facade = ClientRepositoryFacade(session)
    
    # Crear cliente con validaciones completas
    client = await facade.create_client(client_data)
    
    # Búsquedas especializadas
    active_clients = await facade.get_active_clients()
    
    # Gestión de relaciones
    projects = await facade.get_client_projects(client_id)
    
    # Estadísticas
    stats = await facade.get_client_statistics()
    
    # Verificación de salud
    health = await facade.health_check()
    ```

Autor: Sistema de Repositorios
Versión: 2.0.0
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
    create_client_repository_error,
)

# Importaciones de modelos y esquemas
from planificador.models.client import Client
from planificador.schemas.client import ClientCreate, ClientUpdate

# Importaciones de utilidades
from planificador.utils.date_utils import get_current_time

# Importaciones de módulos especializados
from .client_crud_operations import ClientCRUDOperations
from .client_date_operations import ClientDateOperations
from .client_exception_handler import ClientExceptionHandler
from .client_query_builder import ClientQueryBuilder
from .client_relationship_manager import ClientRelationshipManager
from .client_statistics import ClientStatistics
from .client_validator import ClientValidator


class ClientRepositoryFacade:
    """
    Facade que unifica todas las operaciones de clientes a través de
    módulos especializados.

    Esta clase actúa como punto de entrada único para todas las operaciones
    relacionadas con clientes, delegando a los módulos especializados
    apropiados y coordinando
    operaciones complejas que requieren múltiples módulos.

    Attributes:
        session: Sesión asíncrona de SQLAlchemy
        crud_ops: Operaciones CRUD especializadas
        date_ops: Operaciones relacionadas con fechas
        exception_handler: Manejador centralizado de excepciones
        query_builder: Constructor de consultas especializadas
        relationship_manager: Gestor de relaciones cliente-proyecto
        statistics: Generador de estadísticas y métricas
        validator: Validador de datos de clientes
    """

    def __init__(self, session: AsyncSession):
        """
        Inicializa el facade con todos los módulos especializados.

        Args:
            session: Sesión asíncrona de SQLAlchemy
        """
        self.session = session
        self._logger = logger.bind(component="ClientRepositoryFacade")

        # Inicializar componentes especializados
        self.query_builder = ClientQueryBuilder(session)
        self.validator = ClientValidator(session)
        self.crud_ops = ClientCRUDOperations(session, self.validator)
        self.date_ops = ClientDateOperations(session, self.query_builder)
        self.exception_handler = ClientExceptionHandler()
        self.relationship_manager = ClientRelationshipManager(session)
        self.statistics = ClientStatistics(session)

        self._logger.debug(
            "ClientRepositoryFacade inicializado con todos los módulos"
        " especializados"
        )

    # ============================================================================
    # OPERACIONES CRUD UNIFICADAS
    # ============================================================================

    async def create_client(self, client_data: ClientCreate) -> Client:
        """
        Crea un nuevo cliente con validaciones completas.

        Args:
            client_data: Datos del cliente a crear

        Returns:
            Cliente creado

        Raises:
            ClientRepositoryError: Si ocurre un error en la creación
        """
        try:
            return await self.crud_ops.create_client(client_data)
        except (ClientValidationError, ClientNotFoundError, ClientDuplicateError) as e:
            # Re-lanzar excepciones de negocio sin modificar
            raise e
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client",
                additional_context={
                    "client_data": client_data.model_dump()
                    if hasattr(client_data, "model_dump")
                    else str(client_data)
                },
            )

    async def create_client_with_date_validation(
        self, client_data: ClientCreate
    ) -> Client:
        """
        Crea un cliente con validaciones avanzadas de fecha.

        Args:
            client_data: Datos del cliente a crear

        Returns:
            Cliente creado con validaciones de fecha

        Raises:
            ClientRepositoryError: Si ocurre un error en la creación
        """
        try:
            return await self.crud_ops.create_client_with_date_validation(
                client_data
            )
        except (ClientValidationError, ClientNotFoundError, ClientDuplicateError) as e:
            # Re-lanzar excepciones de negocio sin modificar
            raise e
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client_with_date_validation",
                additional_context={
                    "client_data": client_data.model_dump()
                    if hasattr(client_data, "model_dump")
                    else str(client_data)
                },
            )

    async def get_client_by_id(self, client_id: int) -> Client | None:
        """
        Obtiene un cliente por su ID.

        Args:
            client_id: ID del cliente

        Returns:
            Cliente encontrado o None

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.crud_ops.get_client_by_id(client_id)
        except ClientNotFoundError:
            # Cliente no encontrado es un caso válido, retornar None
            return None
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_id",
                additional_context={"client_id": client_id},
            )

    async def update_client(
        self, client_id: int, client_data: ClientUpdate
    ) -> Client | None:
        """
        Actualiza un cliente existente.

        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos de actualización

        Returns:
            Cliente actualizado o None si no existe

        Raises:
            ClientRepositoryError: Si ocurre un error en la actualización
        """
        try:
            return await self.crud_ops.update_client(client_id, client_data)
        except (ClientValidationError, ClientNotFoundError, ClientDuplicateError) as e:
            # Re-lanzar excepciones de negocio sin modificar
            raise e
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="update_client",
                additional_context={
                    "client_id": client_id,
                    "client_data": client_data.model_dump()
                    if hasattr(client_data, "model_dump")
                    else str(client_data),
                },
            )

    async def delete_client(self, client_id: int) -> bool:
        """
        Elimina un cliente (soft delete).

        Args:
            client_id: ID del cliente a eliminar

        Returns:
            True si se eliminó correctamente

        Raises:
            ClientRepositoryError: Si ocurre un error en la eliminación
        """
        try:
            return await self.crud_ops.delete_client(client_id)
        except (ClientValidationError, ClientNotFoundError) as e:
            # Re-lanzar excepciones de negocio sin modificar
            raise e
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="delete_client",
                additional_context={"client_id": client_id},
            )

    # ============================================================================
    # CONSULTAS ESPECIALIZADAS
    # ============================================================================

    async def get_client_by_name(self, name: str) -> Client | None:
        """
        Busca un cliente por nombre exacto.

        Args:
            name: Nombre del cliente

        Returns:
            Cliente encontrado o None
        """
        try:
            return await self.query_builder.get_by_name(name)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_client_by_name", additional_context={"name": name}
            )

    async def get_client_by_code(self, code: str) -> Client | None:
        """
        Busca un cliente por código único.

        Args:
            code: Código del cliente

        Returns:
            Cliente encontrado o None
        """
        try:
            return await self.query_builder.get_by_code(code)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_client_by_code", additional_context={"code": code}
            )

    async def search_clients_by_name(self, name_pattern: str) -> list[Client]:
        """
        Busca clientes por patrón de nombre.

        Args:
            name_pattern: Patrón de búsqueda

        Returns:
            Lista de clientes que coinciden

        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        try:
            return await self.query_builder.search_by_name(name_pattern)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_clients_by_name",
                additional_context={"name_pattern": name_pattern},
            )

    async def get_active_clients(self) -> list[Client]:
        """
        Obtiene todos los clientes activos.

        Returns:
            Lista de clientes activos

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.get_active_clients()
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_active_clients", additional_context={}
            )

    async def search_with_advanced_filters(
        self,
        name_pattern: str | None = None,
        code_pattern: str | None = None,
        has_email: bool | None = None,
        has_phone: bool | None = None,
        has_contact_person: bool | None = None,
        is_active: bool | None = None,
        min_projects: int | None = None,
        max_projects: int | None = None,
        created_after: date | None = None,
        created_before: date | None = None,
        order_by: str = "name",
        order_direction: str = "asc",
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Client]:
        """
        Búsqueda avanzada de clientes con múltiples filtros.

        Args:
            name_pattern: Patrón de búsqueda en nombre
            code_pattern: Patrón de búsqueda en código
            has_email: Filtrar por presencia de email
            has_phone: Filtrar por presencia de teléfono
            has_contact_person: Filtrar por presencia de persona de contacto
            is_active: Filtrar por estado activo
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos
            created_after: Fecha de creación posterior a
            created_before: Fecha de creación anterior a
            order_by: Campo de ordenamiento
            order_direction: Dirección de ordenamiento
            limit: Límite de resultados
            offset: Desplazamiento de resultados

        Returns:
            Lista de clientes que coinciden con los filtros
        """
        try:
            return await self.query_builder.search_with_advanced_filters(
                name_pattern=name_pattern,
                code_pattern=code_pattern,
                has_email=has_email,
                has_phone=has_phone,
                has_contact_person=has_contact_person,
                is_active=is_active,
                min_projects=min_projects,
                max_projects=max_projects,
                created_after=created_after,
                created_before=created_before,
                order_by=order_by,
                order_direction=order_direction,
                limit=limit,
                offset=offset,
            )
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_with_advanced_filters",
                additional_context={
                    "filters": {
                        "name_pattern": name_pattern,
                        "code_pattern": code_pattern,
                        "has_email": has_email,
                        "has_phone": has_phone,
                        "has_contact_person": has_contact_person,
                        "is_active": is_active,
                        "min_projects": min_projects,
                        "max_projects": max_projects,
                        "created_after": created_after.isoformat()
                        if created_after
                        else None,
                        "created_before": created_before.isoformat()
                        if created_before
                        else None,
                        "order_by": order_by,
                        "order_direction": order_direction,
                        "limit": limit,
                        "offset": offset,
                    }
                },
            )
            return []

    # ============================================================================
    # OPERACIONES TEMPORALES
    # ============================================================================

    async def get_clients_created_current_week(self) -> list[Client]:
        """
        Obtiene clientes creados en la semana actual.

        Returns:
            Lista de clientes creados esta semana
        """
        try:
            return await self.date_ops.get_clients_created_current_week()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_created_current_week",
                additional_context={},
            )
            return []

    async def get_clients_created_current_month(self) -> list[Client]:
        """
        Obtiene clientes creados en el mes actual.

        Returns:
            Lista de clientes creados este mes
        """
        try:
            return await self.date_ops.get_clients_created_current_month()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_created_current_month",
                additional_context={},
            )
            return []

    async def get_clients_by_date_range(
        self, start_date: date, end_date: date
    ) -> list[Client]:
        """
        Obtiene clientes creados en un rango de fechas.

        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin

        Returns:
            Lista de clientes en el rango de fechas
        """
        try:
            return await self.date_ops.get_clients_by_date_range(
                start_date, end_date
            )
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_date_range",
                additional_context={
                    "start_date": start_date.isoformat(),
                    "end_date": end_date.isoformat(),
                },
            )
            return []

    async def get_clients_by_age_range(
        self, min_age_days: int, max_age_days: int
    ) -> list[Client]:
        """
        Obtiene clientes por rango de antigüedad.

        Args:
            min_age_days: Edad mínima en días
            max_age_days: Edad máxima en días

        Returns:
            Lista de clientes en el rango de antigüedad
        """
        try:
            return await self.date_ops.get_clients_by_age_range(
                min_age_days, max_age_days
            )
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_age_range",
                additional_context={
                    "min_age_days": min_age_days,
                    "max_age_days": max_age_days,
                },
            )
            return []

    # ============================================================================
    # ESTADÍSTICAS Y MÉTRICAS
    # ============================================================================

    async def get_client_statistics(self) -> dict[str, Any]:
        """
        Obtiene estadísticas básicas de clientes.

        Returns:
            Diccionario con estadísticas básicas
        """
        try:
            return await self.statistics.get_client_counts_by_status()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_client_statistics", additional_context={}
            )
            return {}

    async def get_comprehensive_dashboard_metrics(self) -> dict[str, Any]:
        """
        Obtiene métricas comprehensivas para dashboard ejecutivo.

        Returns:
            Diccionario con todas las métricas para dashboard
        """
        try:
            return await self.statistics.get_comprehensive_dashboard_metrics()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_comprehensive_dashboard_metrics",
                additional_context={},
            )
            return {}

    async def get_client_segmentation_analysis(self) -> dict[str, Any]:
        """
        Obtiene análisis de segmentación de clientes.

        Returns:
            Diccionario con análisis de segmentación
        """
        try:
            return await self.statistics.get_client_segmentation_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_segmentation_analysis",
                additional_context={},
            )
            return {}

    async def get_client_value_analysis(self) -> dict[str, Any]:
        """
        Obtiene análisis de valor de clientes.

        Returns:
            Diccionario con análisis de valor
        """
        try:
            return await self.statistics.get_client_value_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_client_value_analysis", additional_context={}
            )
            return {}

    async def get_client_retention_analysis(self) -> dict[str, Any]:
        """
        Obtiene análisis de retención de clientes.

        Returns:
            Diccionario con análisis de retención
        """
        try:
            return await self.statistics.get_client_retention_analysis()
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e, operation="get_client_retention_analysis", additional_context={}
            )
            return {}

    # ============================================================================
    # VALIDACIONES
    # ============================================================================

    async def validate_client_name_unique(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """
        Valida que el nombre del cliente sea único.

        Args:
            name: Nombre a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)

        Returns:
            True si el nombre es único
        """
        try:
            return await self.validator.validate_name_unique(name, exclude_id)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_name_unique",
                additional_context={"name": name, "exclude_id": exclude_id},
            )
            return False

    async def validate_client_code_unique(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """
        Valida que el código del cliente sea único.

        Args:
            code: Código a validar
            exclude_id: ID a excluir de la validación (para actualizaciones)

        Returns:
            True si el código es único
        """
        try:
            return await self.validator.validate_code_unique(code, exclude_id)
        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_code_unique",
                additional_context={"code": code, "exclude_id": exclude_id},
            )
            return False

    # ============================================================================
    # OPERACIONES COMPLEJAS COORDINADAS
    # ============================================================================

    async def create_client_with_full_validation(
        self, client_data: ClientCreate, validate_business_rules: bool = True
    ) -> Client:
        """
        Crea un cliente con validaciones completas y reglas de negocio.

        Esta operación coordina múltiples módulos para realizar una creación
        completa con todas las validaciones necesarias.

        Args:
            client_data: Datos del cliente a crear
            validate_business_rules: Si aplicar reglas de negocio adicionales

        Returns:
            Cliente creado

        Raises:
            ClientRepositoryError: Si falla alguna validación o la creación
        """
        try:
            self._logger.debug(
                f"Iniciando creación completa de cliente: {client_data.name}"
            )

            # Validar unicidad de nombre y código
            if not await self.validator.validate_name_unique(client_data.name):
                raise create_client_repository_error(
                    message=f"El nombre '{client_data.name}' ya existe",
                    operation="create_client_with_full_validation",
                    entity_id=None,
                )

            if not await self.validator.validate_code_unique(client_data.code):
                raise create_client_repository_error(
                    message=f"El código '{client_data.code}' ya existe",
                    operation="create_client_with_full_validation",
                    entity_id=None,
                )

            # Aplicar reglas de negocio adicionales si se solicita
            if validate_business_rules:
                # Validar formato de email si se proporciona
                if hasattr(client_data, "email") and client_data.email:
                    if not await self.validator.validate_email_format(
                        client_data.email
                    ):
                        raise create_client_repository_error(
                            message=(
                                f"Formato de email inválido: {client_data.email}"
                            ),
                            operation="create_client_with_full_validation",
                            entity_id=None,
                        )

                # Validar formato de teléfono si se proporciona
                if hasattr(client_data, "phone") and client_data.phone:
                    if not await self.validator.validate_phone_format(
                        client_data.phone
                    ):
                        raise create_client_repository_error(
                            message=(
                                f"Formato de teléfono inválido: {client_data.phone}"
                            ),
                            operation="create_client_with_full_validation",
                            entity_id=None,
                        )

            # Crear el cliente usando validaciones de Pendulum
            client = (
                await self.crud_ops.create_client_with_date_validation(
                    client_data
                )
            )

            # Registrar éxito de la operación
            await self.exception_handler.log_operation_success(
                operation="create_client_with_full_validation",
                entity_type="Client",
                entity_id=client.id,
                details=(
                    f"Cliente '{client.name}' creado exitosamente con "
                    "validaciones completas"
                ),
            )

            self._logger.info(
                f"Cliente creado exitosamente con validaciones completas: "
                f"{client.name} (ID: {client.id})"
            )
            return client

        except ClientRepositoryError:
            # Re-lanzar errores de repositorio sin modificar
            raise
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="create_client_with_full_validation",
                additional_context={
                    "client_data": client_data.model_dump()
                    if hasattr(client_data, "model_dump")
                    else str(client_data),
                    "validate_business_rules": validate_business_rules,
                },
            )

    async def get_client_complete_profile(
        self, client_id: int
    ) -> dict[str, Any] | None:
        """
        Obtiene el perfil completo de un cliente incluyendo estadísticas.

        Esta operación coordina múltiples módulos para obtener información
        comprehensiva sobre un cliente específico.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con perfil completo del cliente o None si no existe
        """
        try:
            self._logger.debug(
                f"Obteniendo perfil completo para cliente ID: {client_id}"
            )

            # Obtener datos básicos del cliente
            client = await self.crud_ops.get_client_by_id(client_id)
            if not client:
                self._logger.warning(f"Cliente no encontrado: {client_id}")
                return None

            # Obtener estadísticas específicas del cliente
            client_stats = await self.statistics.get_client_stats(client_id)

            # Calcular edad del cliente
            client_age = await self.date_ops.calculate_client_age(client_id)

            # Construir perfil completo
            complete_profile = {
                "basic_info": {
                    "id": client.id,
                    "name": client.name,
                    "code": client.code,
                    "email": client.email,
                    "phone": client.phone,
                    "contact_person": client.contact_person,
                    "is_active": client.is_active,
                    "created_at": client.created_at.isoformat()
                    if client.created_at
                    else None,
                    "updated_at": client.updated_at.isoformat()
                    if client.updated_at
                    else None,
                },
                "statistics": client_stats,
                "age_info": {
                    "age_days": client_age,
                    "age_months": round(client_age / 30.44, 1)
                    if client_age
                    else 0,
                    "age_years": round(client_age / 365.25, 1)
                    if client_age
                    else 0,
                },
                "profile_generated_at": get_current_time().isoformat(),
            }

            self._logger.debug(
                f"Perfil completo generado para cliente: {client.name}"
            )
            return complete_profile

        except Exception as e:
            await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_complete_profile",
                additional_context={"client_id": client_id},
            )
            return None

    # ============================================================================
    # CONSULTAS AVANZADAS Y FILTROS
    # ============================================================================

    async def get_clients_by_filters(
        self, filters: dict[str, Any]
    ) -> list[Client]:
        """
        Obtiene clientes aplicando múltiples filtros.

        Args:
            filters: Diccionario con criterios de filtrado

        Returns:
            Lista de clientes que cumplen los filtros

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_by_criteria(**filters)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_by_filters",
                additional_context={"filters": filters},
            )

    async def search_clients_by_text(self, search_text: str) -> list[Client]:
        """
        Busca clientes por texto en múltiples campos.

        Args:
            search_text: Texto a buscar

        Returns:
            Lista de clientes que coinciden con el texto

        Raises:
            ClientRepositoryError: Si ocurre un error en la búsqueda
        """
        try:
            return await self.query_builder.search_clients_by_text(search_text)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="search_clients_by_text",
                additional_context={"search_text": search_text},
            )

    async def get_clients_with_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Obtiene clientes que tienen información de contacto.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes con información de contacto

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_clients_with_contact_info(
                include_inactive
            )
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_with_contact_info",
                additional_context={"include_inactive": include_inactive},
            )

    async def get_clients_without_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Obtiene clientes que no tienen información de contacto.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes sin información de contacto

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_clients_without_contact_info(
                include_inactive
            )
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_without_contact_info",
                additional_context={"include_inactive": include_inactive},
            )

    # ============================================================================
    # VALIDACIONES ADICIONALES
    # ============================================================================

    async def validate_client_deletion(self, client_id: int) -> bool:
        """
        Valida si un cliente puede ser eliminado.

        Args:
            client_id: ID del cliente a validar

        Returns:
            True si puede ser eliminado, False en caso contrario

        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            return await self.validator.validate_client_deletion(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_client_deletion",
                additional_context={"client_id": client_id},
            )

    async def validate_email_format(self, email: str) -> bool:
        """
        Valida el formato de un email.

        Args:
            email: Email a validar

        Returns:
            True si el formato es válido, False en caso contrario

        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            return self.validator.validate_email_format(email)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_email_format",
                additional_context={"email": email},
            )

    async def validate_phone_format(self, phone: str) -> bool:
        """
        Valida el formato de un teléfono.

        Args:
            phone: Teléfono a validar

        Returns:
            True si el formato es válido, False en caso contrario

        Raises:
            ClientRepositoryError: Si ocurre un error en la validación
        """
        try:
            return self.validator.validate_phone_format(phone)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="validate_phone_format",
                additional_context={"phone": phone},
            )

    # ============================================================================
    # ESTADÍSTICAS ADICIONALES
    # ============================================================================

    async def get_client_distribution_by_status(self) -> dict[str, int]:
        """
        Obtiene la distribución de clientes por estado.

        Returns:
            Diccionario con conteo por estado

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.statistics.get_client_counts_by_status()
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_distribution_by_status",
                additional_context={},
            )

    async def get_top_clients_by_projects(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Obtiene los clientes con más proyectos.

        Args:
            limit: Número máximo de clientes a retornar

        Returns:
            Lista de clientes ordenados por cantidad de proyectos

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.statistics.get_clients_by_project_count(limit)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_top_clients_by_projects",
                additional_context={"limit": limit},
            )

    async def get_monthly_client_growth(
        self, months: int = 12
    ) -> dict[str, Any]:
        """
        Obtiene el crecimiento mensual de clientes.

        Args:
            months: Número de meses a analizar

        Returns:
            Diccionario con datos de crecimiento mensual

        Raises:
            ClientRepositoryError: Si ocurre un error en el análisis
        """
        try:
            return await self.statistics.get_client_creation_trends(months * 30)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_monthly_client_growth",
                additional_context={"months": months},
            )

    # ============================================================================
    # OPERACIONES CRUD ADICIONALES
    # ============================================================================

    async def update_client_advanced(
        self, client_id: int, client_data: dict[str, Any]
    ) -> Client:
        """
        Actualiza un cliente existente con validaciones avanzadas.

        Args:
            client_id: ID del cliente a actualizar
            client_data: Datos del cliente a actualizar

        Returns:
            Cliente actualizado

        Raises:
            ClientRepositoryError: Si ocurre un error en la actualización
        """
        try:
            return await self.crud_ops.update_client(
                client_id, client_data
            )
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="update_client_advanced",
                additional_context={"client_id": client_id, "data": client_data},
            )

    async def delete_client_advanced(self, client_id: int) -> bool:
        """
        Elimina un cliente con validaciones avanzadas.

        Args:
            client_id: ID del cliente a eliminar

        Returns:
            True si se eliminó correctamente

        Raises:
            ClientRepositoryError: Si ocurre un error en la eliminación
        """
        try:
            return await self.crud_ops.delete_client(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="delete_client_advanced",
                additional_context={"client_id": client_id},
            )

    async def get_client_by_id_advanced(
        self, client_id: int
    ) -> Client | None:
        """
        Obtiene un cliente por su ID con validaciones avanzadas.

        Args:
            client_id: ID del cliente

        Returns:
            Cliente encontrado o None si no existe

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_by_id(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_id_advanced",
                additional_context={"client_id": client_id},
            )

    async def get_client_by_name_advanced(
        self, name: str
    ) -> Client | None:
        """
        Obtiene un cliente por su nombre con validaciones avanzadas.

        Args:
            name: Nombre del cliente

        Returns:
            Cliente encontrado o None si no existe

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_by_name(name)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_name_advanced",
                additional_context={"name": name},
            )

    async def get_client_by_email(self, email: str) -> Client | None:
        """
        Obtiene un cliente por su email.

        Args:
            email: Email del cliente

        Returns:
            Cliente encontrado o None si no existe

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.query_builder.find_by_email(email)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_by_email",
                additional_context={"email": email},
            )

    # ============================================================================
    # GESTIÓN DE RELACIONES
    # ============================================================================

    async def transfer_projects_to_client(
        self, source_client_id: int, target_client_id: int
    ) -> bool:
        """
        Transfiere proyectos de un cliente a otro.

        Args:
            source_client_id: ID del cliente origen
            target_client_id: ID del cliente destino

        Returns:
            True si la transferencia fue exitosa

        Raises:
            ClientRepositoryError: Si ocurre un error en la transferencia
        """
        try:
            return await self.relationship_manager.\
                transfer_projects_to_client(
                    source_client_id, target_client_id
                )
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="transfer_projects_to_client",
                additional_context={
                    "source_client_id": source_client_id,
                    "target_client_id": target_client_id,
                },
            )

    async def get_client_projects(self, client_id: int) -> list[dict[str, Any]]:
        """
        Obtiene los proyectos de un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Lista de proyectos del cliente

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.relationship_manager.\
                get_client_projects(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_projects",
                additional_context={"client_id": client_id},
            )

    async def get_client_project_count(self, client_id: int) -> int:
        """
        Obtiene el número de proyectos de un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Número de proyectos del cliente

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.relationship_manager.\
                get_client_project_count(client_id)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_client_project_count",
                additional_context={"client_id": client_id},
            )

    # ============================================================================
    # OPERACIONES DE FECHA
    # ============================================================================

    async def get_clients_created_in_date_range(
        self, start_date: str, end_date: str
    ) -> list[Client]:
        """
        Obtiene clientes creados en un rango de fechas.

        Args:
            start_date: Fecha de inicio (formato ISO)
            end_date: Fecha de fin (formato ISO)

        Returns:
            Lista de clientes creados en el rango

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.date_operations.\
                get_clients_created_in_range(start_date, end_date)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_created_in_date_range",
                additional_context={"start_date": start_date, "end_date": end_date},
            )

    async def get_clients_updated_in_date_range(
        self, start_date: str, end_date: str
    ) -> list[Client]:
        """
        Obtiene clientes actualizados en un rango de fechas.

        Args:
            start_date: Fecha de inicio (formato ISO)
            end_date: Fecha de fin (formato ISO)

        Returns:
            Lista de clientes actualizados en el rango

        Raises:
            ClientRepositoryError: Si ocurre un error en la consulta
        """
        try:
            return await self.date_operations.\
                get_clients_updated_in_range(start_date, end_date)
        except Exception as e:
            return await self.exception_handler.handle_unexpected_error(
                error=e,
                operation="get_clients_updated_in_date_range",
                additional_context={"start_date": start_date, "end_date": end_date},
            )

    # ============================================================================
    # MÉTODOS DE UTILIDAD Y ESTADO
    # ============================================================================

    async def health_check(self) -> dict[str, Any]:
        """
        Verifica el estado de salud de todos los módulos del facade.

        Returns:
            Diccionario con estado de salud de cada módulo
        """
        try:
            health_status = {
                "facade_status": "healthy",
                "modules": {},
                "timestamp": get_current_time().isoformat(),
            }

            # Verificar cada módulo realizando una operación simple
            try:
                await self.statistics.get_client_counts_by_status()
                health_status["modules"]["statistics"] = "healthy"
            except Exception as e:
                health_status["modules"]["statistics"] = f"error: {e!s}"

            try:
                await self.query_builder.get_active_clients()
                health_status["modules"]["query_builder"] = "healthy"
            except Exception as e:
                health_status["modules"]["query_builder"] = f"error: {e!s}"

            # Verificar validador
            try:
                await self.validator.validate_name_exists(
                    "__health_check_test__"
                )
                health_status["modules"]["validator"] = "healthy"
            except Exception as e:
                health_status["modules"]["validator"] = f"error: {e!s}"

            # Verificar relationship_manager
            try:
                await self.relationship_manager.get_client_projects(1)
                health_status["modules"]["relationship_manager"] = "healthy"
            except Exception as e:
                health_status["modules"]["relationship_manager"] = f"error: {e!s}"

            # Verificar crud_ops
            try:
                # Verificar que el módulo esté disponible
                if hasattr(self.crud_ops, 'get_client_by_id'):
                    health_status["modules"]["crud_ops"] = "healthy"
                else:
                    health_status["modules"]["crud_ops"] = "error: missing methods"
            except Exception as e:
                health_status["modules"]["crud_ops"] = f"error: {e!s}"

            # Verificar date_ops
            try:
                # Verificar que el módulo esté disponible
                if hasattr(self.date_ops, 'get_clients_created_current_week'):
                    health_status["modules"]["date_ops"] = "healthy"
                else:
                    health_status["modules"]["date_ops"] = "error: missing methods"
            except Exception as e:
                health_status["modules"]["date_ops"] = f"error: {e!s}"

            # Verificar exception_handler
            try:
                # Verificar que el módulo esté disponible
                if hasattr(self.exception_handler, 'handle_unexpected_error'):
                    health_status["modules"]["exception_handler"] = "healthy"
                else:
                    health_status["modules"]["exception_handler"] = "error: missing methods"
            except Exception as e:
                health_status["modules"]["exception_handler"] = f"error: {e!s}"

            # Determinar estado general
            unhealthy_modules = [
                k
                for k, v in health_status["modules"].items()
                if v != "healthy"
            ]
            if unhealthy_modules:
                health_status["facade_status"] = (
                    f"degraded - modules with issues: "
                    f"{', '.join(unhealthy_modules)}"
                )

            self._logger.debug(
                f"Health check completado - Estado: "
                f"{health_status['facade_status']}"
            )
            return health_status

        except Exception as e:
            self._logger.error(f"Error en health check: {e}")
            return {
                "facade_status": f"error: {e!s}",
                "modules": {},
                "timestamp": get_current_time().isoformat(),
            }

    def get_module_info(self) -> dict[str, str]:
        """
        Obtiene información sobre los módulos cargados.

        Returns:
            Diccionario con información de módulos
        """
        return {
            "crud_operations": self.crud_ops.__class__.__name__,
            "date_operations": self.date_ops.__class__.__name__,
            "exception_handler": self.exception_handler.__class__.__name__,
            "query_builder": self.query_builder.__class__.__name__,
            "statistics": self.statistics.__class__.__name__,
            "validator": self.validator.__class__.__name__,
            "facade_version": "1.0.0",
            "initialized_at": get_current_time().isoformat(),
        }
