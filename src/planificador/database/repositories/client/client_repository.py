# src/planificador/database/repositories/client/client_repository.py

from datetime import date
from typing import Any

from loguru import logger
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession

from ....exceptions import (
    NotFoundError,
    ValidationError,
)
from ....exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
)
from ....exceptions.repository import (
    RepositoryError,
    convert_sqlalchemy_error,
    create_client_bulk_operation_error,
    create_client_date_range_error,
    create_client_relationship_error,
    create_client_validation_repository_error,
)
from ....models.client import Client
from ....models.project import Project
from ....utils.date_utils import (
    format_datetime,
    get_current_time,
    is_business_day,
)
from ..base_repository import BaseRepository

# Importar clases especializadas
from .client_query_builder import ClientQueryBuilder
from .client_relationship_manager import ClientRelationshipManager
from .client_statistics import ClientStatistics
from .client_validator import ClientValidator


class ClientRepository(BaseRepository[Client]):
    """
    Repositorio principal para la gestión de clientes.

    Actúa como orquestador de las clases especializadas:
    - ClientQueryBuilder: Constructor de consultas complejas
    - ClientValidator: Validador de datos y reglas de negocio
    - ClientStatistics: Generador de estadísticas y métricas
    - ClientRelationshipManager: Gestor de relaciones con proyectos

    Proporciona una interfaz unificada para todas las operaciones
    relacionadas con clientes, manteniendo la compatibilidad con
    la API existente mientras mejora la organización del código.
    """

    def __init__(self, session: AsyncSession):
        super().__init__(Client, session)

        # Inicializar componentes especializados
        self.query_builder = ClientQueryBuilder(session)
        self.validator = ClientValidator(session)
        self.statistics = ClientStatistics(session)
        self.relationship_manager = ClientRelationshipManager(session)

        self._logger = logger.bind(component="ClientRepository")

    # ==========================================
    # OPERACIONES CRUD BÁSICAS (4 funciones)
    # ==========================================

    async def create_client(self, client_data: dict[str, Any]) -> Client:
        """
        Crea un nuevo cliente con validaciones.

        Args:
            client_data: Datos del cliente

        Returns:
            Cliente creado

        Raises:
            ValidationError: Si hay errores de validación
            ClientValidationRepositoryError: Si hay errores específicos del repositorio
        """
        try:
            # Validar datos del cliente
            await self.validator.validate_client_data(client_data)

            # Crear cliente usando el método base
            client = await self.create(client_data)

            self._logger.info(
                f"Cliente creado exitosamente: {client.name} (ID: {client.id})"
            )
            return client

        except ValidationError:
            # Re-lanzar errores de validación de dominio directamente
            raise
        except ValidationError as e:
            # Convertir ValidationError en ClientValidationRepositoryError específico
            self._logger.error(f"Error de validación creando cliente: {e}")
            raise create_client_validation_repository_error(
                field="validation",
                value=client_data,
                reason=str(e),
                operation="create_client",
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(f"Error de base de datos creando cliente: {e}")
            raise convert_sqlalchemy_error(
                error=e, operation="create_client", entity_type="Client"
            )
        except Exception as e:
            # Manejar otros errores como errores generales del repositorio
            await self.session.rollback()
            self._logger.error(f"Error inesperado creando cliente: {e}")
            raise create_client_validation_repository_error(
                field="general",
                value=client_data,
                reason=f"Error inesperado: {e!s}",
                operation="create_client",
            )

    async def update_client(
        self, client_id: int, update_data: dict[str, Any]
    ) -> Client | None:
        """
        Actualiza un cliente con validaciones.

        Args:
            client_id: ID del cliente
            update_data: Datos a actualizar

        Returns:
            Cliente actualizado o None si no existe

        Raises:
            NotFoundError: Si el cliente no existe
            ValidationError: Si hay errores de validación
            ClientValidationRepositoryError: Si hay errores específicos del repositorio
        """
        try:
            # Primero verificar si el cliente existe
            existing_client = await self.get_by_id(client_id)
            if not existing_client:
                raise NotFoundError(f"Cliente con ID {client_id} no encontrado")

            # Validar datos de actualización
            await self.validator.validate_client_update_data(
                update_data, client_id
            )

            # Actualizar cliente usando el método base
            client = await self.update(client_id, update_data)

            if client:
                self._logger.info(
                    f"Cliente actualizado exitosamente: {client.name} (ID: {client.id})"
                )

            return client

        except NotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except ValidationError:
            # Re-lanzar errores de validación de dominio directamente
            raise
        except ValidationError as e:
            # Convertir ValidationError en ClientValidationRepositoryError específico
            self._logger.error(
                f"Error de validación actualizando cliente {client_id}: {e}"
            )
            raise create_client_validation_repository_error(
                field="validation",
                value={"client_id": client_id, **update_data},
                reason=str(e),
                operation="update_client",
                client_id=client_id,
            )

    async def create_client_with_date_validation(
        self, client_data: dict[str, Any], validate_business_day: bool = False
    ) -> Client:
        """
        Crea un cliente con validaciones avanzadas de fecha.

        Args:
            client_data: Datos del cliente
            validate_business_day: Si validar que la creación sea en día laborable

        Returns:
            Cliente creado

        Raises:
            ClientValidationError: Si hay validaciones fallidas
        """
        try:
            # Obtener timestamp actual con Pendulum
            current_time = get_current_time()

            # Validar día laborable si se requiere
            if validate_business_day and not is_business_day(
                current_time.date()
            ):
                raise ValidationError(
                f"Los clientes solo pueden crearse en días laborables. "
                f"Hoy es {current_time.format('dddd')}"
            )

            # Agregar timestamp de creación con Pendulum
            client_data_with_timestamp = {
                **client_data,
                "created_at": current_time.to_datetime_string(),
                "timezone_created": str(current_time.timezone),
            }

            # Crear usando el método existente con validaciones
            client = await self.create_client(client_data_with_timestamp)

            self._logger.info(
                f"Cliente creado con validación Pendulum: {format_datetime(current_time)} "
                f"(Zona: {current_time.timezone})"
            )

            return client

        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(
                f"Error de base de datos creando cliente con validación Pendulum: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="create_client_with_date_validation",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error creando cliente con validación Pendulum: {e}"
            )
            if isinstance(e, ValidationError):
                raise
            await self.session.rollback()
            raise ValidationError(
                f"Error creando cliente con validación Pendulum: {e}"
            )

    # ==========================================
    # CONSULTAS POR IDENTIFICADORES ÚNICOS (2 funciones)
    # ==========================================

    async def get_by_name(self, name: str) -> Client | None:
        """
        Busca un cliente por nombre.

        Args:
            name: Nombre del cliente

        Returns:
            Cliente encontrado o None
        """
        return await self.query_builder.get_by_name(name)

    async def get_by_code(self, code: str) -> Client | None:
        """
        Busca un cliente por código.

        Args:
            code: Código del cliente

        Returns:
            Cliente encontrado o None
        """
        return await self.query_builder.get_by_code(code)

    # ==========================================
    # CONSULTAS POR ATRIBUTOS (7 funciones)
    # ==========================================

    async def search_by_name(self, search_term: str) -> list[Client]:
        """
        Busca clientes por término de búsqueda en el nombre.

        Args:
            search_term: Término de búsqueda

        Returns:
            Lista de clientes que coinciden
        """
        return await self.query_builder.search_by_name(search_term)

    async def get_active_clients(self) -> list[Client]:
        """
        Obtiene todos los clientes activos.

        Returns:
            Lista de clientes activos
        """
        return await self.query_builder.get_active_clients()

    async def get_with_projects(self, client_id: int) -> Client | None:
        """
        Obtiene un cliente con todos sus proyectos cargados.

        Args:
            client_id: ID del cliente

        Returns:
            Cliente con proyectos cargados o None

        Raises:
            ClientRelationshipError: Si hay errores cargando las relaciones
        """
        try:
            return await self.query_builder.get_with_projects(client_id)
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos cargando cliente {client_id} con proyectos: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_projects",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado cargando cliente {client_id} con proyectos: {e}"
            )
            raise create_client_relationship_error(
                relationship_type="projects",
                client_id=client_id,
                related_entity_type="Project",
                reason=str(e),
            )

    async def get_client_relationship_duration(
        self, client_id: int
    ) -> dict[str, Any]:
        """
        Calcula la duración de la relación con un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con estadísticas de duración de relación
        """
        try:
            client = await self.get_by_id(client_id)
            if not client or not client.created_at:
                return {
                    "client_found": False,
                    "has_creation_date": False,
                    "relationship_days": 0,
                    "relationship_business_days": 0,
                    "relationship_years": 0.0,
                    "created_at": None,
                }

            # Convertir fecha de creación a date si es necesario
            created_date = (
                client.created_at.date()
                if hasattr(client.created_at, "date")
                else client.created_at
            )
            current_date = get_current_time().date()

            # Calcular duración de relación
            relationship_days = (current_date - created_date).days
            relationship_business_days = get_business_days(
                created_date, current_date
            )
            relationship_years = relationship_days / 365.25

            # Determinar si fue creado en día laborable
            created_on_business_day = is_business_day(created_date)

            stats = {
                "client_found": True,
                "has_creation_date": True,
                "client_name": client.name,
                "client_code": client.code,
                "created_at": created_date.isoformat(),
                "current_date": current_date.isoformat(),
                "relationship_days": relationship_days,
                "relationship_business_days": relationship_business_days,
                "relationship_years": round(relationship_years, 2),
                "relationship_months": round(relationship_years * 12, 1),
                "created_on_business_day": created_on_business_day,
                "is_active": client.is_active,
            }

            self._logger.debug(
                f"Estadísticas de relación calculadas para cliente {client_id}"
            )
            return stats

        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(
                f"Error de base de datos calculando duración de relación - Cliente {client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="calculate_relationship_duration",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(
                f"Error inesperado calculando duración de relación - Cliente {client_id}: {e}"
            )
            raise

    async def get_clients_with_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Obtiene clientes que tienen información de contacto.
        Utiliza la propiedad has_contact_info del modelo.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes con información de contacto
        """
        try:
            return await self.query_builder.find_clients_with_contact_info(
                include_inactive
            )
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error obteniendo clientes con información de contacto: {e}"
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_with_contact_info",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes con información de contacto: {e}"
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes con información de contacto: {e}",
                operation="get_clients_with_contact_info",
                entity_type="Client",
                original_error=e,
            )

    async def get_clients_without_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Obtiene clientes que NO tienen información de contacto.
        Útil para identificar clientes que necesitan actualización de datos.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes sin información de contacto
        """
        try:
            return await self.query_builder.find_clients_without_contact_info(
                include_inactive
            )
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error obteniendo clientes sin información de contacto: {e}"
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_without_contact_info",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes sin información de contacto: {e}"
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo clientes sin información de contacto: {e}",
                operation="get_clients_without_contact_info",
                entity_type="Client",
                original_error=e,
            )

    async def get_clients_display_summary(
        self, include_inactive: bool = False
    ) -> list[dict[str, Any]]:
        """
        Obtiene un resumen de clientes con información formateada para mostrar.
        Utiliza las propiedades display_name, status_display y contact_summary del modelo.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de diccionarios con información formateada de clientes
        """
        try:
            clients = await self.get_all()
            if not include_inactive:
                clients = [client for client in clients if client.is_active]

            summary_data = []
            for client in clients:
                client_summary = {
                    "id": client.id,
                    "display_name": client.display_name,
                    "status_display": client.status_display,
                    "has_contact_info": client.has_contact_info,
                    "contact_summary": client.contact_summary,
                    "created_at": client.created_at,
                    "updated_at": client.updated_at,
                }
                summary_data.append(client_summary)

            self._logger.debug(
                f"Generado resumen para {len(summary_data)} clientes"
            )
            return summary_data

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error obteniendo resumen de clientes: {e}"
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_display_summary",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo resumen de clientes: {e}"
            )
            await self.session.rollback()
            raise RepositoryError(
                message=f"Error inesperado obteniendo resumen de clientes: {e}",
                operation="get_clients_display_summary",
                entity_type="Client",
                original_error=e,
            )

    # ==========================================
    # CONSULTAS TEMPORALES (3 funciones)
    # ==========================================

    async def get_clients_created_current_week(self, **kwargs) -> list[Client]:
        """
        Obtiene clientes creados en la semana actual.

        Args:
            **kwargs: Criterios adicionales de filtrado

        Returns:
            Lista de clientes creados esta semana
        """
        return await self.query_builder.find_clients_created_current_week(
            **kwargs
        )

    async def get_clients_created_current_month(
        self, **kwargs
    ) -> list[Client]:
        """
        Obtiene clientes creados en el mes actual.

        Args:
            **kwargs: Criterios adicionales de filtrado

        Returns:
            Lista de clientes creados este mes
        """
        return await self.query_builder.find_clients_created_current_month(
            **kwargs
        )

    async def get_clients_created_business_days_only(
        self,
        start_date: date | str | None = None,
        end_date: date | str | None = None,
        **kwargs,
    ) -> list[Client]:
        """
        Obtiene clientes creados solo en días laborables.

        Args:
            start_date: Fecha de inicio (opcional)
            end_date: Fecha de fin (opcional)
            **kwargs: Criterios adicionales

        Returns:
            Lista de clientes creados en días laborables

        Raises:
            ClientDateRangeError: Si hay errores con el rango de fechas
        """
        try:
            return await self.query_builder.find_clients_created_business_days_only(
                start_date, end_date, **kwargs
            )
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(
                f"Error de base de datos obteniendo clientes por días laborables: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_clients_created_business_days_only",
                entity_type="Client",
            )
        except Exception as e:
            # Manejar errores inesperados
            self._logger.error(
                f"Error inesperado obteniendo clientes por días laborables: {e}"
            )
            # Convertir fechas a datetime para la excepción
            from datetime import datetime

            default_start = datetime.now().replace(
                day=1
            )  # Primer día del mes actual
            default_end = datetime.now()  # Fecha actual

            raise create_client_date_range_error(
                start_date=start_date
                if isinstance(start_date, datetime)
                else default_start,
                end_date=end_date
                if isinstance(end_date, datetime)
                else default_end,
                operation="get_clients_created_business_days_only",
                reason=str(e),
            )

    # ==========================================
    # VALIDACIONES DE UNICIDAD (2 funciones)
    # ==========================================

    async def name_exists(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """
        Verifica si existe un cliente con el nombre dado.

        Args:
            name: Nombre a verificar
            exclude_id: ID de cliente a excluir de la verificación

        Returns:
            True si el nombre existe, False en caso contrario
        """
        return await self.query_builder.name_exists(name, exclude_id)

    async def code_exists(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """
        Verifica si existe un cliente con el código dado.

        Args:
            code: Código a verificar
            exclude_id: ID de cliente a excluir de la verificación

        Returns:
            True si el código existe, False en caso contrario
        """
        return await self.query_builder.code_exists(code, exclude_id)

    # ==========================================
    # ESTADÍSTICAS Y MÉTRICAS (8 funciones)
    # ==========================================

    async def get_client_stats(self, client_id: int) -> dict[str, Any]:
        """
        Obtiene estadísticas de un cliente específico.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con estadísticas del cliente
        """
        return await self.statistics.get_client_stats(client_id)

    async def get_clients_by_relationship_duration(
        self,
        min_years: float = 0.0,
        max_years: float | None = None,
        is_active: bool | None = None,
    ) -> list[dict[str, Any]]:
        """
        Obtiene clientes por duración de relación.

        Args:
            min_years: Duración mínima de relación en años
            max_years: Duración máxima de relación en años (opcional)
            is_active: Estado del cliente (opcional)

        Returns:
            Lista de clientes con información de duración de relación
        """
        return await self.statistics.get_clients_by_relationship_duration(
            min_years, max_years, is_active
        )

    async def get_client_counts_by_status(self) -> dict[str, int]:
        """
        Obtiene el conteo de clientes por estado.

        Returns:
            Diccionario con el conteo por estado
        """
        return await self.statistics.get_client_counts_by_status()

    async def get_client_creation_trends(
        self, days: int = 30, group_by: str = "day"
    ) -> list[dict[str, Any]]:
        """
        Obtiene tendencias de creación de clientes.

        Args:
            days: Número de días hacia atrás
            group_by: Agrupación ('day', 'week', 'month')

        Returns:
            Lista con tendencias de creación
        """
        return await self.statistics.get_client_creation_trends(days, group_by)

    async def get_clients_by_project_count(
        self, limit: int = 10
    ) -> list[dict[str, Any]]:
        """
        Obtiene clientes ordenados por número de proyectos.

        Args:
            limit: Número máximo de clientes a retornar

        Returns:
            Lista de clientes con conteo de proyectos
        """
        return await self.statistics.get_clients_by_project_count(limit)

    async def get_client_activity_summary(self) -> dict[str, Any]:
        """
        Obtiene un resumen de actividad de clientes.

        Returns:
            Diccionario con resumen de actividad
        """
        return await self.statistics.get_client_activity_summary()

    async def get_performance_metrics(self) -> dict[str, Any]:
        """
        Obtiene métricas de rendimiento del sistema de clientes.

        Returns:
            Diccionario con métricas de rendimiento
        """
        return await self.statistics.get_performance_metrics()

    async def get_contact_info_statistics(self) -> dict[str, Any]:
        """
        Obtiene estadísticas sobre información de contacto de clientes.
        Utiliza las propiedades del modelo Client para generar métricas detalladas.

        Returns:
            Diccionario con estadísticas de información de contacto
        """
        return await self.statistics.get_contact_info_statistics()

    # ==========================================
    # GESTIÓN DE RELACIONES CON PROYECTOS (4 funciones)
    # ==========================================

    async def get_client_projects(
        self,
        client_id: int,
        status_filter: list[str] | None = None,
        include_inactive: bool = False,
        load_details: bool = False,
    ) -> list[Project]:
        """
        Obtiene todos los proyectos de un cliente.

        Args:
            client_id: ID del cliente
            status_filter: Lista de estados de proyecto a filtrar (opcional)
            include_inactive: Si incluir proyectos inactivos
            load_details: Si cargar detalles completos del proyecto

        Returns:
            Lista de proyectos del cliente
        """
        return await self.relationship_manager.get_client_projects(
            client_id, status_filter, include_inactive, load_details
        )

    async def get_client_project_summary(
        self, client_id: int
    ) -> dict[str, Any]:
        """
        Obtiene un resumen de proyectos de un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con resumen de proyectos
        """
        return await self.relationship_manager.get_client_project_summary(
            client_id
        )

    async def transfer_projects_to_client(
        self,
        source_client_id: int,
        target_client_id: int,
        project_ids: list[int] | None = None,
        validate_transfer: bool = True,
    ) -> dict[str, Any]:
        """
        Transfiere proyectos de un cliente a otro.

        Args:
            source_client_id: ID del cliente origen
            target_client_id: ID del cliente destino
            project_ids: IDs específicos de proyectos a transferir (opcional)
            validate_transfer: Si validar la transferencia

        Returns:
            Diccionario con resultado de la transferencia

        Raises:
            NotFoundError: Si alguno de los clientes no existe
            ClientRepositoryError: Si hay errores en la operación bulk
        """
        try:
            return await self.relationship_manager.transfer_projects_to_client(
                source_client_id,
                target_client_id,
                project_ids,
                validate_transfer,
            )
        except NotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            await self.session.rollback()
            self._logger.error(
                f"Error de base de datos transfiriendo proyectos de cliente {source_client_id} a {target_client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="transfer_projects_to_client",
                entity_type="Client",
                entity_id=f"{source_client_id}->{target_client_id}",
            )
        except Exception as e:
            # Convertir otros errores en ClientBulkOperationError específico
            await self.session.rollback()
            self._logger.error(
                f"Error transfiriendo proyectos de cliente {source_client_id} a {target_client_id}: {e}"
            )
            raise create_client_bulk_operation_error(
                operation_type="transfer_projects_to_client",
                total_items=len(project_ids) if project_ids else 1,
                failed_items=[
                    {
                        "source_client_id": source_client_id,
                        "target_client_id": target_client_id,
                        "project_ids": project_ids,
                        "error": str(e),
                    }
                ],
                reason=f"Error transfiriendo proyectos: {e!s}",
            )

    async def validate_client_project_integrity(
        self, client_id: int
    ) -> dict[str, Any]:
        """
        Valida la integridad de las relaciones cliente-proyecto.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con resultado de la validación

        Raises:
            NotFoundError: Si el cliente no existe
            ClientRepositoryError: Si hay errores en la validación
        """
        try:
            return await self.relationship_manager.validate_client_project_integrity(
                client_id
            )
        except NotFoundError:
            # Re-lanzar errores de cliente no encontrado directamente
            raise
        except SQLAlchemyError as e:
            # Convertir errores de SQLAlchemy
            self._logger.error(
                f"Error de base de datos validando integridad del cliente {client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_client_project_integrity",
                entity_type="Client",
                entity_id=str(client_id),
            )
        except Exception as e:
            # Convertir otros errores en ClientValidationRepositoryError específico
            self._logger.error(
                f"Error validando integridad del cliente {client_id}: {e}"
            )
            raise create_client_validation_repository_error(
                field="project_integrity",
                value={"client_id": client_id},
                reason=str(e),
                operation="validate_client_project_integrity",
                client_id=client_id,
            )
