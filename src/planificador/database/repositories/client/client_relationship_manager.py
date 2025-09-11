# src/planificador/database/repositories/client/client_relationship_manager.py

from typing import Any

from loguru import logger
from sqlalchemy import and_, case, delete, func, or_, select
from sqlalchemy.exc import SQLAlchemyError
from sqlalchemy.ext.asyncio import AsyncSession
from sqlalchemy.orm import selectinload

from ....exceptions import (
    ConflictError,
    NotFoundError,
    ValidationError,
)
from ....exceptions.repository.client_repository_exceptions import (
    ClientRepositoryError,
    ClientRelationshipError,
)
from ....exceptions.repository.base_repository_exceptions import (
    RepositoryError,
    convert_sqlalchemy_error,
)
from ....models.client import Client
from ....models.project import Project
from ....utils.date_utils import get_current_time


class ClientRelationshipManager:
    """
    Gestor de relaciones entre clientes y proyectos.

    Maneja las operaciones relacionadas con la asociación
    entre clientes y sus proyectos, incluyendo validaciones
    de integridad referencial y operaciones en cascada.
    """

    def __init__(self, session: AsyncSession):
        self.session = session
        self._logger = logger.bind(component="ClientRelationshipManager")

    # ============================================================================
    # CONSULTAS DE RELACIONES BÁSICAS
    # ============================================================================

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

        Raises:
            NotFoundError: Si el cliente no existe
        """
        try:
            # Verificar que el cliente existe
            await self._validate_client_exists(client_id)

            # Construir consulta base
            query = select(Project).where(Project.client_id == client_id)

            # Aplicar filtros
            if status_filter:
                query = query.where(Project.status.in_(status_filter))

            if not include_inactive:
                query = query.where(Project.is_active)

            # Cargar detalles si se solicita
            if load_details:
                query = query.options(
                    selectinload(Project.tasks),
                    selectinload(Project.assignments),
                )

            # Ordenar por fecha de creación
            query = query.order_by(Project.created_at.desc())

            result = await self.session.execute(query)
            projects = result.scalars().all()

            self._logger.debug(
                f"Obtenidos {len(projects)} proyectos para cliente {client_id}"
            )
            return list(projects)

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(

                    f"Error de base de datos obteniendo proyectos del cliente "
                    f"{client_id}: {e}"

            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_projects",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            self._logger.error(

                    f"Error inesperado obteniendo proyectos del cliente "
                    f"{client_id}: {e}"

            )
            raise RepositoryError(
                message=(
                    f"Error inesperado obteniendo proyectos del cliente: {e}"
                ),
                operation="get_client_projects",
                entity_type="Client",
                entity_id=client_id,
                original_error=e,
            )

    # ============================================================================
    # GESTIÓN DE ASIGNACIONES
    # ============================================================================

    async def assign_project_to_client(
        self,
        project_id: int,
        client_id: int,
        validate_constraints: bool = True,
    ) -> Project:
        """
        Asigna un proyecto a un cliente.

        Args:
            project_id: ID del proyecto
            client_id: ID del cliente
            validate_constraints: Si validar restricciones de negocio

        Returns:
            Proyecto actualizado

        Raises:
            ProjectNotFoundError: Si el proyecto no existe
            ClientNotFoundError: Si el cliente no existe
            ClientRelationshipError: Si hay problemas con la asignación
        """
        try:
            # Validar que el proyecto existe
            project = await self._get_project_by_id(project_id)
            if not project:
                raise ValidationError(
                    f"Proyecto con ID {project_id} no encontrado"
                )

            # Validar que el cliente existe
            await self._validate_client_exists(client_id)

            # Validaciones de negocio
            if validate_constraints:
                await self._validate_project_assignment(project, client_id)

            # Actualizar la asignación
            project.client_id = client_id
            project.updated_at = get_current_time()

            await self.session.commit()
            await self.session.refresh(project)

            self._logger.info(

                    f"Proyecto {project_id} asignado exitosamente al cliente "
                    f"{client_id}"

            )
            return project

        except (ValidationError, NotFoundError):
            raise
        except SQLAlchemyError as e:
            self._logger.error(

                    f"Error de base de datos asignando proyecto {project_id} "
                    f"al cliente {client_id}: {e}"

            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="assign_project_to_client",
                entity_type="Project",
                entity_id=project_id,
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(
                f"Error inesperado asignando proyecto {project_id} al cliente {client_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado en la asignación del proyecto: {e}",
                operation="assign_project_to_client",
                entity_type="Project",
                entity_id=project_id,
                original_error=e,
            )

    # ============================================================================
    # GESTIÓN DE TRANSFERENCIAS
    # ============================================================================

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
            NotFoundError: Si algún cliente no existe
            ConflictError: Si hay problemas con la transferencia
        """
        try:
            # Validar que ambos clientes existen
            await self._validate_client_exists(source_client_id)
            await self._validate_client_exists(target_client_id)

            # Obtener proyectos a transferir
            if project_ids:
                # Transferir proyectos específicos
                query = select(Project).where(
                    and_(
                        Project.id.in_(project_ids),
                        Project.client_id == source_client_id,
                    )
                )
            else:
                # Transferir todos los proyectos del cliente origen
                query = select(Project).where(
                    Project.client_id == source_client_id
                )

            result = await self.session.execute(query)
            projects_to_transfer = result.scalars().all()

            if not projects_to_transfer:
                return {
                    "transferred_count": 0,
                    "projects": [],
                    "message": "No se encontraron proyectos para transferir",
                }

            # Validaciones de transferencia
            if validate_transfer:
                for project in projects_to_transfer:
                    await self._validate_project_assignment(
                        project, target_client_id
                    )

            # Realizar la transferencia
            transferred_projects = []
            current_time = get_current_time()

            for project in projects_to_transfer:
                project.client_id = target_client_id
                project.updated_at = current_time
                transferred_projects.append(
                    {
                        "id": project.id,
                        "name": project.name,
                        "status": project.status,
                    }
                )

            await self.session.commit()

            result_data = {
                "transferred_count": len(transferred_projects),
                "projects": transferred_projects,
                "source_client_id": source_client_id,
                "target_client_id": target_client_id,
                "transferred_at": current_time.isoformat(),
            }

            self._logger.info(
                f"Transferidos {len(transferred_projects)} proyectos "
                f"del cliente {source_client_id} al cliente {target_client_id}"
            )

            return result_data

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos transfiriendo proyectos del cliente {source_client_id} "
                f"al cliente {target_client_id}: {e}"
            )
            await self.session.rollback()
            raise convert_sqlalchemy_error(
                error=e,
                operation="transfer_projects_to_client",
                entity_type="Client",
                entity_id=source_client_id,
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(
                f"Error inesperado transfiriendo proyectos del cliente {source_client_id} "
                f"al cliente {target_client_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado en la transferencia de proyectos: {e}",
                operation="transfer_projects_to_client",
                entity_type="Client",
                entity_id=source_client_id,
                original_error=e,
            )

    # ============================================================================
    # RESÚMENES Y ANÁLISIS
    # ============================================================================

    async def get_client_project_summary(
        self, client_id: int
    ) -> dict[str, Any]:
        """
        Obtiene un resumen de proyectos de un cliente.

        Args:
            client_id: ID del cliente

        Returns:
            Diccionario con resumen de proyectos

        Raises:
            NotFoundError: Si el cliente no existe
        """
        try:
            # Verificar que el cliente existe
            client = await self._get_client_by_id(client_id)
            if not client:
                raise NotFoundError(
                    f"Cliente con ID {client_id} no encontrado"
                )

            # Obtener estadísticas de proyectos
            projects_query = select(
                func.count(Project.id).label("total"),
                func.sum(
                    case((Project.status == "planned", 1), else_=0)
                ).label("planned"),
                func.sum(
                    case((Project.status == "in_progress", 1), else_=0)
                ).label("in_progress"),
                func.sum(
                    case((Project.status == "completed", 1), else_=0)
                ).label("completed"),
                func.sum(
                    case((Project.status == "cancelled", 1), else_=0)
                ).label("cancelled"),
                func.sum(case((Project.is_active, 1), else_=0)).label(
                    "active"
                ),
                func.min(Project.created_at).label("first_project_date"),
                func.max(Project.created_at).label("last_project_date"),
            ).where(Project.client_id == client_id)

            result = await self.session.execute(projects_query)
            stats = result.first()

            # Obtener proyectos recientes (últimos 5)
            recent_projects_query = (
                select(Project)
                .where(Project.client_id == client_id)
                .order_by(Project.created_at.desc())
                .limit(5)
            )

            recent_result = await self.session.execute(recent_projects_query)
            recent_projects = recent_result.scalars().all()

            summary = {
                "client_id": client_id,
                "client_name": client.name,
                "client_code": client.code,
                "client_is_active": client.is_active,
                "project_statistics": {
                    "total_projects": stats.total or 0,
                    "by_status": {
                        "planned": stats.planned or 0,
                        "in_progress": stats.in_progress or 0,
                        "completed": stats.completed or 0,
                        "cancelled": stats.cancelled or 0,
                    },
                    "active_projects": stats.active or 0,
                    "inactive_projects": (stats.total or 0)
                    - (stats.active or 0),
                },
                "timeline": {
                    "first_project_date": (
                        stats.first_project_date.isoformat()
                        if stats.first_project_date
                        else None
                    ),
                    "last_project_date": (
                        stats.last_project_date.isoformat()
                        if stats.last_project_date
                        else None
                    ),
                },
                "recent_projects": [
                    {
                        "id": project.id,
                        "name": project.name,
                        "status": project.status,
                        "is_active": project.is_active,
                        "created_at": project.created_at.isoformat(),
                    }
                    for project in recent_projects
                ],
                "generated_at": get_current_time().isoformat(),
            }

            self._logger.debug(
                f"Resumen de proyectos generado para cliente {client_id}"
            )
            return summary

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos generando resumen de proyectos para cliente {client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="get_client_project_summary",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado generando resumen de proyectos para cliente {client_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado generando resumen de proyectos: {e}",
                operation="get_client_project_summary",
                entity_type="Client",
                entity_id=client_id,
                original_error=e,
            )

    # ============================================================================
    # VALIDACIONES DE INTEGRIDAD
    # ============================================================================

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
        """
        try:
            # Verificar que el cliente existe
            await self._validate_client_exists(client_id)

            issues = []
            warnings = []

            # Verificar proyectos huérfanos (sin cliente válido)
            orphaned_projects_query = select(Project).where(
                and_(
                    Project.client_id == client_id,
                    ~select(Client.id).where(Client.id == client_id).exists(),
                )
            )
            orphaned_result = await self.session.execute(
                orphaned_projects_query
            )
            orphaned_projects = orphaned_result.scalars().all()

            if orphaned_projects:
                issues.append(
                    {
                        "type": "orphaned_projects",
                        "count": len(orphaned_projects),
                        "description": "Proyectos que referencian un cliente inexistente",
                        "project_ids": [p.id for p in orphaned_projects],
                    }
                )

            # Verificar proyectos activos con cliente inactivo
            client = await self._get_client_by_id(client_id)
            if not client.is_active:
                active_projects_query = select(Project).where(
                    and_(
                        Project.client_id == client_id,
                        Project.is_active,
                    )
                )
                active_result = await self.session.execute(
                    active_projects_query
                )
                active_projects = active_result.scalars().all()

                if active_projects:
                    warnings.append(
                        {
                            "type": "active_projects_inactive_client",
                            "count": len(active_projects),
                            "description": "Proyectos activos asociados a cliente inactivo",
                            "project_ids": [p.id for p in active_projects],
                        }
                    )

            # Verificar proyectos en progreso sin fechas válidas
            invalid_dates_query = select(Project).where(
                and_(
                    Project.client_id == client_id,
                    Project.status == "in_progress",
                    or_(
                        Project.start_date.is_(None),
                        Project.start_date > get_current_time(),
                    ),
                )
            )
            invalid_dates_result = await self.session.execute(
                invalid_dates_query
            )
            invalid_dates_projects = invalid_dates_result.scalars().all()

            if invalid_dates_projects:
                warnings.append(
                    {
                        "type": "invalid_project_dates",
                        "count": len(invalid_dates_projects),
                        "description": "Proyectos en progreso con fechas inválidas",
                        "project_ids": [p.id for p in invalid_dates_projects],
                    }
                )

            validation_result = {
                "client_id": client_id,
                "is_valid": len(issues) == 0,
                "has_warnings": len(warnings) > 0,
                "issues": issues,
                "warnings": warnings,
                "validated_at": get_current_time().isoformat(),
            }

            self._logger.debug(
                f"Validación de integridad completada para cliente {client_id}: "
                f"{len(issues)} problemas, {len(warnings)} advertencias"
            )

            return validation_result

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            self._logger.error(
                f"Error de base de datos validando integridad del cliente {client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="validate_client_project_integrity",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            self._logger.error(
                f"Error inesperado validando integridad del cliente {client_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado en validación de integridad: {e}",
                operation="validate_client_project_integrity",
                entity_type="Client",
                entity_id=client_id,
                original_error=e,
            )

    # ============================================================================
    # LIMPIEZA DE RELACIONES
    # ============================================================================

    async def cleanup_client_relationships(
        self, client_id: int, action: str = "deactivate"
    ) -> dict[str, Any]:
        """
        Limpia las relaciones de un cliente antes de eliminación o desactivación.

        Args:
            client_id: ID del cliente
            action: Acción a realizar ('deactivate', 'transfer', 'delete')

        Returns:
            Diccionario con resultado de la limpieza

        Raises:
            NotFoundError: Si el cliente no existe
            ValidationError: Si hay problemas con la limpieza
        """
        try:
            # Verificar que el cliente existe
            await self._validate_client_exists(client_id)

            # Obtener proyectos del cliente
            projects = await self.get_client_projects(
                client_id, include_inactive=True
            )

            cleanup_result = {
                "client_id": client_id,
                "action": action,
                "projects_affected": len(projects),
                "actions_taken": [],
                "cleaned_at": get_current_time().isoformat(),
            }

            if not projects:
                cleanup_result["actions_taken"].append(
                    "No hay proyectos para limpiar"
                )
                return cleanup_result

            current_time = get_current_time()

            if action == "deactivate":
                # Desactivar todos los proyectos del cliente
                for project in projects:
                    if project.is_active:
                        project.is_active = False
                        project.updated_at = current_time

                cleanup_result["actions_taken"].append(
                    f"Desactivados {len([p for p in projects if not p.is_active])} proyectos"
                )

            elif action == "delete":
                # Eliminar todos los proyectos del cliente
                project_ids = [p.id for p in projects]
                delete_query = delete(Project).where(
                    Project.id.in_(project_ids)
                )
                await self.session.execute(delete_query)

                cleanup_result["actions_taken"].append(
                    f"Eliminados {len(project_ids)} proyectos"
                )

            elif action == "transfer":
                # Esta acción requiere un cliente destino específico
                cleanup_result["actions_taken"].append(
                    "Transferencia requiere cliente destino específico"
                )
                cleanup_result["requires_target_client"] = True
                return cleanup_result

            await self.session.commit()

            self._logger.info(
                f"Limpieza de relaciones completada para cliente {client_id}: {action}"
            )

            return cleanup_result

        except NotFoundError:
            raise
        except SQLAlchemyError as e:
            await self.session.rollback()
            self._logger.error(
                f"Error de base de datos limpiando relaciones del cliente {client_id}: {e}"
            )
            raise convert_sqlalchemy_error(
                error=e,
                operation="cleanup_client_relationships",
                entity_type="Client",
                entity_id=client_id,
            )
        except Exception as e:
            await self.session.rollback()
            self._logger.error(
                f"Error inesperado limpiando relaciones del cliente {client_id}: {e}"
            )
            raise RepositoryError(
                message=f"Error inesperado en limpieza de relaciones: {e}",
                operation="cleanup_client_relationships",
                entity_type="Client",
                entity_id=client_id,
                original_error=e,
            )

    # ============================================================================
    # FUNCIONES PRIVADAS
    # ============================================================================

    async def _validate_client_exists(self, client_id: int) -> None:
        """Valida que un cliente existe."""
        client = await self._get_client_by_id(client_id)
        if not client:
            raise NotFoundError(
                f"Cliente con ID {client_id} no encontrado"
            )

    async def _get_client_by_id(self, client_id: int) -> Client | None:
        """Obtiene un cliente por ID."""
        query = select(Client).where(Client.id == client_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _get_project_by_id(self, project_id: int) -> Project | None:
        """Obtiene un proyecto por ID."""
        query = select(Project).where(Project.id == project_id)
        result = await self.session.execute(query)
        return result.scalar_one_or_none()

    async def _validate_project_assignment(
        self, project: Project, client_id: int
    ) -> None:
        """
        Valida que un proyecto puede ser asignado a un cliente.

        Args:
            project: Proyecto a validar
            client_id: ID del cliente destino

        Raises:
            ConflictError: Si la asignación no es válida
        """
        # Verificar que el cliente está activo
        client = await self._get_client_by_id(client_id)
        if not client.is_active:
            raise ConflictError(
                f"No se puede asignar proyecto a cliente inactivo {client_id}"
            )

        # Verificar que el proyecto no está en estado final
        if project.status in ["completed", "cancelled"]:
            self._logger.warning(
                f"Asignando proyecto {project.id} en estado final '{project.status}' "
                f"al cliente {client_id}"
            )

        # Verificar que no hay conflictos de fechas (si aplica)
        if project.status == "in_progress" and not project.start_date:
            raise ValidationError(
                f"Proyecto {project.id} en progreso debe tener fecha de inicio"
            )
