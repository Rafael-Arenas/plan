# src/planificador/database/repositories/client/client_query_builder.py

from datetime import date
from typing import Any

import pendulum
from loguru import logger
from sqlalchemy import and_, desc, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....exceptions.repository import (
    convert_sqlalchemy_error,
    create_client_query_error,
)
from ....models.client import Client
from ....models.project import Project
from ....utils.date_utils import get_current_time, is_business_day
from .interfaces.i_client_query_builder import IClientQueryBuilder


class ClientQueryBuilder(IClientQueryBuilder):
    """
    Constructor de consultas especializadas para clientes.

    Encapsula toda la lógica de construcción de queries SQLAlchemy
    para operaciones de búsqueda y filtrado de clientes.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(component="ClientQueryBuilder")

    # Consultas Base por Identificadores

    async def get_by_name(self, name: str) -> Client | None:
        """
        Busca un cliente por su nombre exacto.

        Args:
            name: Nombre del cliente

        Returns:
            Cliente encontrado o None
        """
        try:
            query = select(Client).where(Client.name == name)
            result = await self.session.execute(query)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(f"Cliente encontrado por nombre: {name}")
            else:
                self._logger.debug(f"Cliente no encontrado por nombre: {name}")

            return client

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos buscando cliente por nombre "
                f"'{name}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="get_by_name", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando cliente por nombre "
                f"'{name}': {e}"
            )
            raise create_client_query_error(
                query_type="get_by_name",
                parameters={"name": name},
                reason=f"Error inesperado: {e!s}",
            )

    async def get_by_code(self, code: str) -> Client | None:
        """
        Busca un cliente por su código.

        Args:
            code: Código del cliente

        Returns:
            Cliente encontrado o None
        """
        try:
            query = select(Client).where(Client.code == code)
            result = await self.session.execute(query)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(f"Cliente encontrado por código: {code}")
            else:
                self._logger.debug(f"Cliente no encontrado por código: {code}")

            return client

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos buscando cliente por código "
                f"'{code}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="get_by_code", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando cliente por código "
                f"'{code}': {e}"
            )
            raise create_client_query_error(
                query_type="get_by_code",
                parameters={"code": code},
                reason=f"Error inesperado: {e!s}",
            )

    # Consultas por Atributos

    async def search_by_name(self, search_term: str) -> list[Client]:
        """
        Busca clientes cuyo nombre contenga el término de búsqueda.

        Args:
            search_term: Término a buscar en el nombre

        Returns:
            Lista de clientes que coinciden
        """
        try:
            query = (
                select(Client)
                .where(Client.name.ilike(f"%{search_term}%"))
                .order_by(Client.name)
            )

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes con término: "
                f"{search_term}"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos buscando clientes con término "
                f"'{search_term}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="search_by_name", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando clientes con término "
                f"'{search_term}': {e}"
            )
            raise create_client_query_error(
                query_type="search_by_name",
                parameters={"search_term": search_term},
                reason=f"Error inesperado: {e!s}",
            )

    async def get_active_clients(self) -> list[Client]:
        """
        Obtiene todos los clientes activos.

        Returns:
            Lista de clientes activos
        """
        try:
            query = (
                select(Client)
                .where(Client.is_active)
                .order_by(Client.name)
            )

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(f"Obtenidos {len(clients)} clientes activos")
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes activos: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="get_active_clients", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes activos: {e}"
            )
            raise create_client_query_error(
                query_type="get_active_clients",
                parameters={},
                reason=f"Error inesperado: {e!s}",
            )

    async def get_with_projects(self, client_id: int) -> Client | None:
        """
        Obtiene un cliente con todos sus proyectos cargados.

        Args:
            client_id: ID del cliente

        Returns:
            Cliente con proyectos cargados o None
        """
        try:
            query = (
                select(Client)
                .options(selectinload(Client.projects))
                .where(Client.id == client_id)
            )

            result = await self.session.execute(query)
            client = result.scalar_one_or_none()

            if client:
                self._logger.debug(
                    f"Cliente con proyectos cargado: {client_id}"
                )
            else:
                self._logger.debug(f"Cliente no encontrado: {client_id}")

            return client

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo cliente con proyectos "
                f"{client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_with_projects",
                entity_type="Client",
                entity_id=str(client_id),
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo cliente con proyectos "
                f"{client_id}: {e}"
            )
            raise create_client_query_error(
                query_type="get_with_projects",
                parameters={"client_id": client_id},
                reason=f"Error inesperado: {e!s}",
            )

    async def find_clients_with_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Busca clientes que tienen información de contacto.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes con información de contacto
        """
        try:
            query = select(Client).where(
                or_(
                    Client.contact_person.isnot(None),
                    Client.email.isnot(None),
                    Client.phone.isnot(None),
                )
            )

            if not include_inactive:
                query = query.where(Client.is_active)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes con información de "
                f"contacto"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error buscando clientes con información de contacto: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_with_contact_info",
                entity_type="Client",
            )

    async def find_clients_without_contact_info(
        self, include_inactive: bool = False
    ) -> list[Client]:
        """
        Busca clientes que NO tienen información de contacto.

        Args:
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes sin información de contacto
        """
        try:
            query = select(Client).where(
                and_(
                    Client.contact_person.is_(None),
                    Client.email.is_(None),
                    Client.phone.is_(None),
                )
            )

            if not include_inactive:
                query = query.where(Client.is_active)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes sin información de "
                f"contacto"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error buscando clientes sin información de contacto: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_without_contact_info",
                entity_type="Client",
            )

    # Consultas Temporales

    async def find_clients_created_current_week(
        self, **kwargs
    ) -> list[Client]:
        """
        Obtiene clientes creados en la semana actual.

        Args:
            **kwargs: Criterios adicionales de filtrado

        Returns:
            Lista de clientes creados esta semana
        """
        try:
            current_time = get_current_time()
            start_of_week = current_time.start_of("week")
            end_of_week = current_time.end_of("week")

            query = select(Client).where(
                and_(
                    Client.created_at >= start_of_week,
                    Client.created_at <= end_of_week,
                )
            )

            # Aplicar filtros adicionales
            for key, value in kwargs.items():
                if hasattr(Client, key):
                    query = query.where(getattr(Client, key) == value)

            query = query.order_by(desc(Client.created_at))

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes creados esta semana"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes de la semana "
                f"actual: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_created_current_week",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes de la semana "
                f"actual: {e}"
            )
            raise create_client_query_error(
                query_type="find_clients_created_current_week",
                parameters=kwargs,
                reason=f"Error inesperado: {e!s}",
            )

    async def find_clients_created_current_month(
        self, **kwargs
    ) -> list[Client]:
        """
        Obtiene clientes creados en el mes actual.

        Args:
            **kwargs: Criterios adicionales de filtrado

        Returns:
            Lista de clientes creados este mes
        """
        try:
            current_time = get_current_time()
            start_of_month = current_time.start_of("month")
            end_of_month = current_time.end_of("month")

            query = select(Client).where(
                and_(
                    Client.created_at >= start_of_month,
                    Client.created_at <= end_of_month,
                )
            )

            # Aplicar filtros adicionales
            for key, value in kwargs.items():
                if hasattr(Client, key):
                    query = query.where(getattr(Client, key) == value)

            query = query.order_by(desc(Client.created_at))

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes creados este mes"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes del mes "
                f"actual: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_created_current_month",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes del mes "
                f"actual: {e}"
            )
            raise create_client_query_error(
                query_type="find_clients_created_current_month",
                parameters=kwargs,
                reason=f"Error inesperado: {e!s}",
            )

    async def find_clients_created_business_days_only(
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
        """
        try:
            # Obtener todos los clientes en el rango de fechas
            query = select(Client)

            if start_date:
                if isinstance(start_date, str):
                    start_date = pendulum.parse(start_date).date()
                query = query.where(Client.created_at >= start_date)

            if end_date:
                if isinstance(end_date, str):
                    end_date = pendulum.parse(end_date).date()
                query = query.where(Client.created_at <= end_date)

            # Aplicar filtros adicionales
            for key, value in kwargs.items():
                if hasattr(Client, key):
                    query = query.where(getattr(Client, key) == value)

            query = query.order_by(desc(Client.created_at))

            result = await self.session.execute(query)
            all_clients = result.scalars().all()

            # Filtrar solo días laborables
            business_day_clients = []
            for client in all_clients:
                if client.created_at and is_business_day(
                    client.created_at.date()
                ):
                    business_day_clients.append(client)

            self._logger.debug(
                f"Encontrados {len(business_day_clients)} clientes creados "
                f"en días laborables de {len(all_clients)} clientes totales"
            )

            return business_day_clients

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes de días "
                f"laborables: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_created_business_days_only",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes de días "
                f"laborables: {e}"
            )
            raise create_client_query_error(
                query_type="find_clients_created_business_days_only",
                parameters={
                    "start_date": start_date,
                    "end_date": end_date,
                    **kwargs,
                },
                reason=f"Error inesperado: {e!s}",
            )

    # Consultas por Criterios Múltiples

    async def find_by_criteria(self, **kwargs) -> list[Client]:
        """
        Busca clientes por múltiples criterios.

        Args:
            **kwargs: Criterios de búsqueda

        Returns:
            Lista de clientes que cumplen los criterios
        """
        try:
            query = select(Client)

            # Aplicar filtros dinámicamente
            if "name" in kwargs:
                query = query.where(Client.name.ilike(f"%{kwargs['name']}%"))
            if "code" in kwargs:
                query = query.where(Client.code == kwargs["code"])
            if "is_active" in kwargs:
                query = query.where(Client.is_active == kwargs["is_active"])

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes por criterios"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(f"Error buscando clientes por criterios: {e}")
            raise convert_sqlalchemy_error(
                error=e, operation="find_by_criteria", entity_type="Client"
            )

    # Consultas Avanzadas y Filtros Complejos

    async def find_by_date_range(
        self,
        start_date: date | str,
        end_date: date | str,
        include_inactive: bool = False,
    ) -> list[Client]:
        """
        Busca clientes creados en un rango de fechas específico.

        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            include_inactive: Si incluir clientes inactivos

        Returns:
            Lista de clientes en el rango de fechas
        """
        try:
            # Convertir strings a fechas si es necesario
            if isinstance(start_date, str):
                start_date = pendulum.parse(start_date).date()
            if isinstance(end_date, str):
                end_date = pendulum.parse(end_date).date()

            query = select(Client).where(
                and_(
                    Client.created_at >= start_date,
                    Client.created_at <= end_date,
                )
            )

            if not include_inactive:
                query = query.where(Client.is_active)

            query = query.order_by(desc(Client.created_at))

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes entre {start_date} y "
                f"{end_date}"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error buscando clientes por rango de fechas: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="find_by_date_range", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando clientes por rango de "
                f"fechas: {e}"
            )
            raise create_client_query_error(
                query_type="find_by_date_range",
                parameters={"start_date": start_date, "end_date": end_date},
                reason=f"Error inesperado: {e!s}",
            )

    async def find_by_project_count(
        self, min_projects: int = 0, max_projects: int | None = None
    ) -> list[dict[str, Any]]:
        """
        Busca clientes por número de proyectos asociados.

        Args:
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos (opcional)

        Returns:
            Lista de diccionarios con cliente y conteo de proyectos
        """
        try:
            query = (
                select(Client, func.count(Project.id).label("project_count"))
                .outerjoin(Project)
                .group_by(Client.id)
                .having(func.count(Project.id) >= min_projects)
            )

            if max_projects is not None:
                query = query.having(func.count(Project.id) <= max_projects)

            query = query.order_by(desc("project_count"))

            result = await self.session.execute(query)
            rows = result.all()

            clients_with_count = [
                {"client": row.Client, "project_count": row.project_count}
                for row in rows
            ]

            self._logger.debug(
                f"Encontrados {len(clients_with_count)} clientes con "
                f"{min_projects}+ proyectos"
            )
            return clients_with_count

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error buscando clientes por conteo de proyectos: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_by_project_count",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando clientes por conteo de "
                f"proyectos: {e}"
            )
            raise create_client_query_error(
                query_type="find_by_project_count",
                parameters={
                    "min_projects": min_projects,
                    "max_projects": max_projects,
                },
                reason=f"Error inesperado: {e!s}",
            )

    async def find_clients_for_display_summary(
        self, limit: int = 10, offset: int = 0
    ) -> list[dict[str, Any]]:
        """
        Obtiene clientes con información resumida para mostrar en interfaces.

        Args:
            limit: Número máximo de resultados
            offset: Número de resultados a omitir

        Returns:
            Lista de diccionarios con información resumida de clientes
        """
        try:
            query = (
                select(
                    Client.id,
                    Client.name,
                    Client.code,
                    Client.is_active,
                    Client.contact_person,
                    Client.email,
                    func.count(Project.id).label("project_count"),
                )
                .outerjoin(Project)
                .group_by(Client.id)
                .order_by(Client.name)
                .limit(limit)
                .offset(offset)
            )

            result = await self.session.execute(query)
            rows = result.all()

            summary_data = [
                {
                    "id": row.id,
                    "name": row.name,
                    "code": row.code,
                    "is_active": row.is_active,
                    "contact_person": row.contact_person,
                    "email": row.email,
                    "project_count": row.project_count,
                    "has_contact_info": bool(row.contact_person or row.email),
                }
                for row in rows
            ]

            self._logger.debug(
                f"Obtenido resumen de {len(summary_data)} clientes"
            )
            return summary_data

        except SQLAlchemyError as e:
            self._logger.error(f"Error obteniendo resumen de clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="find_clients_for_display_summary",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo resumen de "
                f"clientes: {e}"
            )
            raise create_client_query_error(
                query_type="find_clients_for_display_summary",
                parameters={"limit": limit, "offset": offset},
                reason=f"Error inesperado: {e!s}",
            )

    async def search_with_advanced_filters(
        self,
        name_pattern: str | None = None,
        code_pattern: str | None = None,
        has_contact_info: bool | None = None,
        is_active: bool | None = None,
        created_after: date | str | None = None,
        created_before: date | str | None = None,
        min_projects: int | None = None,
        max_projects: int | None = None,
        order_by: str = "name",
        order_desc: bool = False,
        limit: int | None = None,
        offset: int = 0,
    ) -> list[Client]:
        """
        Búsqueda avanzada de clientes con múltiples filtros.

        Args:
            name_pattern: Patrón para buscar en el nombre
            code_pattern: Patrón para buscar en el código
            has_contact_info: Si debe tener información de contacto
            is_active: Estado activo/inactivo
            created_after: Fecha mínima de creación
            created_before: Fecha máxima de creación
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos
            order_by: Campo por el cual ordenar
            order_desc: Si ordenar descendente
            limit: Límite de resultados
            offset: Desplazamiento de resultados

        Returns:
            Lista de clientes que cumplen los filtros
        """
        try:
            query = select(Client)

            # Filtros de texto
            if name_pattern:
                query = query.where(Client.name.ilike(f"%{name_pattern}%"))

            if code_pattern:
                query = query.where(Client.code.ilike(f"%{code_pattern}%"))

            # Filtro de estado
            if is_active is not None:
                query = query.where(Client.is_active == is_active)

            # Filtro de información de contacto
            if has_contact_info is not None:
                if has_contact_info:
                    query = query.where(
                        or_(
                            Client.contact_person.isnot(None),
                            Client.email.isnot(None),
                            Client.phone.isnot(None),
                        )
                    )
                else:
                    query = query.where(
                        and_(
                            Client.contact_person.is_(None),
                            Client.email.is_(None),
                            Client.phone.is_(None),
                        )
                    )

            # Filtros de fecha
            if created_after:
                if isinstance(created_after, str):
                    created_after = pendulum.parse(created_after).date()
                query = query.where(Client.created_at >= created_after)

            if created_before:
                if isinstance(created_before, str):
                    created_before = pendulum.parse(created_before).date()
                query = query.where(Client.created_at <= created_before)

            # Filtros de proyectos (requiere join)
            if min_projects is not None or max_projects is not None:
                query = query.outerjoin(Project).group_by(Client.id)

                if min_projects is not None:
                    query = query.having(
                        func.count(Project.id) >= min_projects
                    )

                if max_projects is not None:
                    query = query.having(
                        func.count(Project.id) <= max_projects
                    )

            # Ordenamiento
            if hasattr(Client, order_by):
                order_column = getattr(Client, order_by)
                if order_desc:
                    query = query.order_by(desc(order_column))
                else:
                    query = query.order_by(order_column)

            # Paginación
            if limit:
                query = query.limit(limit)
            if offset:
                query = query.offset(offset)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Búsqueda avanzada encontró {len(clients)} clientes"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(f"Error en búsqueda avanzada de clientes: {e}")
            raise convert_sqlalchemy_error(
                error=e,
                operation="search_with_advanced_filters",
                entity_type="Client",
            )
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda avanzada: {e}")
            raise create_client_query_error(
                query_type="search_with_advanced_filters",
                parameters={
                    "name_pattern": name_pattern,
                    "code_pattern": code_pattern,
                    "has_contact_info": has_contact_info,
                    "is_active": is_active,
                },
                reason=f"Error inesperado: {e!s}",
            ) from e

    # ========================================================================
    # MÉTODOS ABSTRACTOS REQUERIDOS POR IClientQueryBuilder
    # ========================================================================

    async def get_clients_by_filters(
        self,
        filters: dict[str, Any],
        limit: int | None = None,
        offset: int | None = None,
    ) -> list[Client]:
        """Obtiene clientes aplicando filtros específicos.

        Args:
            filters: Diccionario con los filtros a aplicar.
            limit: Número máximo de resultados.
            offset: Número de resultados a omitir.

        Returns:
            Lista de clientes que cumplen los filtros.
        """
        try:
            query = select(Client)

            # Aplicar filtros dinámicamente
            for key, value in filters.items():
                if hasattr(Client, key) and value is not None:
                    if isinstance(value, str) and key in ["name", "code"]:
                        # Búsqueda parcial para campos de texto
                        query = query.where(
                            getattr(Client, key).ilike(f"%{value}%")
                        )
                    else:
                        # Búsqueda exacta para otros campos
                        query = query.where(getattr(Client, key) == value)

            # Aplicar ordenamiento por defecto
            query = query.order_by(Client.name)

            # Aplicar paginación
            if offset:
                query = query.offset(offset)
            if limit:
                query = query.limit(limit)

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes con filtros: {filters}"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes por filtros "
                f"{filters}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="get_clients_by_filters", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes por filtros "
                f"{filters}: {e}"
            )
            raise create_client_query_error(
                query_type="get_clients_by_filters",
                parameters={"filters": filters, "limit": limit, "offset": offset},
                reason=f"Error inesperado: {e!s}",
            )

    async def search_clients_by_text(self, search_text: str) -> list[Client]:
        """Busca clientes por texto en nombre, código o email.

        Args:
            search_text: Texto a buscar.

        Returns:
            Lista de clientes que coinciden con la búsqueda.
        """
        try:
            # Búsqueda en múltiples campos usando OR
            search_pattern = f"%{search_text}%"
            query = (
                select(Client)
                .where(
                    or_(
                        Client.name.ilike(search_pattern),
                        Client.code.ilike(search_pattern),
                        Client.email.ilike(search_pattern),
                        Client.contact_person.ilike(search_pattern),
                    )
                )
                .order_by(Client.name)
            )

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(
                f"Encontrados {len(clients)} clientes con texto: {search_text}"
            )
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos buscando clientes por texto "
                f"'{search_text}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="search_clients_by_text", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado buscando clientes por texto "
                f"'{search_text}': {e}"
            )
            raise create_client_query_error(
                query_type="search_clients_by_text",
                parameters={"search_text": search_text},
                reason=f"Error inesperado: {e!s}",
            )

    async def get_active_clients(self) -> list[Client]:
        """Obtiene todos los clientes activos.

        Returns:
            Lista de clientes activos.
        """
        try:
            query = (
                select(Client)
                .where(Client.is_active == True)
                .order_by(Client.name)
            )

            result = await self.session.execute(query)
            clients = result.scalars().all()

            self._logger.debug(f"Encontrados {len(clients)} clientes activos")
            return list(clients)

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos obteniendo clientes activos: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="get_active_clients", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado obteniendo clientes activos: {e}"
            )
            raise create_client_query_error(
                query_type="get_active_clients",
                parameters={},
                reason=f"Error inesperado: {e!s}",
            )

    # Validaciones de Existencia

    async def name_exists(
        self, name: str, exclude_id: int | None = None
    ) -> bool:
        """
        Verifica si ya existe un cliente con el nombre especificado.

        Args:
            name: Nombre a verificar
            exclude_id: ID a excluir de la verificación (para actualizaciones)

        Returns:
            True si el nombre ya existe
        """
        try:
            query = select(func.count(Client.id)).where(Client.name == name)

            if exclude_id:
                query = query.where(Client.id != exclude_id)

            result = await self.session.execute(query)
            count = result.scalar_one()

            exists = count > 0
            self._logger.debug(
                f"Verificación de nombre '{name}': "
                f"{'existe' if exists else 'no existe'}"
            )
            return exists

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos verificando nombre "
                f"'{name}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="name_exists", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado verificando nombre "
                f"'{name}': {e}"
            )
            raise create_client_query_error(
                query_type="name_exists",
                parameters={"name": name, "exclude_id": exclude_id},
                reason=f"Error inesperado: {e!s}",
            )

    async def code_exists(
        self, code: str, exclude_id: int | None = None
    ) -> bool:
        """
        Verifica si ya existe un cliente con el código especificado.

        Args:
            code: Código a verificar
            exclude_id: ID a excluir de la verificación (para actualizaciones)

        Returns:
            True si el código ya existe
        """
        try:
            query = select(func.count(Client.id)).where(Client.code == code)

            if exclude_id:
                query = query.where(Client.id != exclude_id)

            result = await self.session.execute(query)
            count = result.scalar()

            exists = count > 0
            self._logger.debug(
                f"Verificación de código '{code}': "
                f"{'existe' if exists else 'no existe'}"
            )
            return exists

        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos verificando código "
                f"'{code}': {e}"
            )
            raise convert_sqlalchemy_error(
                error=e, operation="code_exists", entity_type="Client"
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado verificando código "
                f"'{code}': {e}"
            )
            raise create_client_query_error(
                query_type="code_exists",
                parameters={"code": code, "exclude_id": exclude_id},
                reason=f"Error inesperado: {e!s}",
            )
