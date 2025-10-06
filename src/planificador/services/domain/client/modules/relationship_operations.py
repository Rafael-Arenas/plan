# src/planificador/services/domain/client/modules/relationship_operations.py

"""
Módulo de operaciones de relaciones para el servicio de dominio de cliente.

Este módulo implementa la gestión de relaciones entre clientes y otras entidades
del sistema como proyectos, equipos y asignaciones.
"""

from typing import Any, Dict, List, Optional
from uuid import UUID

from loguru import logger

from planificador.exceptions import RepositoryError, ValidationError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import Client
from planificador.services.domain.client.interfaces.relationship_interface import IRelationshipOperations


class RelationshipOperations(IRelationshipOperations):
    """
    Implementación de operaciones de relaciones para el dominio de cliente.
    
    Esta clase encapsula la gestión de relaciones entre clientes y otras entidades,
    proporcionando métodos para consultar y validar integridad referencial.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de relaciones.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def get_clients_with_projects(
        self,
        include_inactive_projects: bool = False,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que tienen proyectos asociados.
        
        Args:
            include_inactive_projects: Si incluir proyectos inactivos
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes con proyectos
        """
        try:
            self._logger.debug("Obteniendo clientes con proyectos")
            
            # TODO: Implementar cuando exista la entidad Project y su relación
            # Por ahora retornamos todos los clientes activos como placeholder
            self._logger.warning("Relación con proyectos no implementada aún")
            
            filters = {"is_active": True if not include_inactive_clients else None}
            if filters["is_active"] is None:
                del filters["is_active"]
                
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes con proyectos (placeholder): {len(result)}")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes con proyectos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes con proyectos: {e}",
                operation="get_clients_with_projects",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_without_projects(
        self,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que no tienen proyectos asociados.
        
        Args:
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes sin proyectos
        """
        try:
            self._logger.debug("Obteniendo clientes sin proyectos")
            
            # TODO: Implementar cuando exista la entidad Project y su relación
            # Por ahora retornamos clientes inactivos como placeholder
            self._logger.warning("Relación con proyectos no implementada aún")
            
            filters = {"is_active": False if not include_inactive_clients else None}
            if filters["is_active"] is None:
                del filters["is_active"]
                
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes sin proyectos (placeholder): {len(result)}")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes sin proyectos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes sin proyectos: {e}",
                operation="get_clients_without_projects",
                entity_type="Client",
                original_error=e
            )

    async def get_client_projects_count(
        self,
        client_id: UUID,
        include_inactive: bool = False
    ) -> int:
        """
        Obtiene el número de proyectos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            include_inactive: Si incluir proyectos inactivos
            
        Returns:
            int: Número de proyectos del cliente
        """
        try:
            self._logger.debug(f"Contando proyectos para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=str(client_id)
                )
            
            # TODO: Implementar conteo real cuando exista la entidad Project
            self._logger.warning("Conteo de proyectos no implementado aún")
            
            # Por ahora retornamos 0
            project_count = 0
            
            self._logger.debug(f"Proyectos para cliente {client_id}: {project_count}")
            
            return project_count
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al contar proyectos del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al contar proyectos: {e}",
                operation="get_client_projects_count",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_clients_with_teams(
        self,
        include_inactive_teams: bool = False,
        include_inactive_clients: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes que tienen equipos asociados.
        
        Args:
            include_inactive_teams: Si incluir equipos inactivos
            include_inactive_clients: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes con equipos
        """
        try:
            self._logger.debug("Obteniendo clientes con equipos")
            
            # TODO: Implementar cuando exista la entidad Team y su relación
            # Por ahora retornamos lista vacía
            self._logger.warning("Relación con equipos no implementada aún")
            
            return []
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes con equipos: {e}")
            raise RepositoryError(
                message=f"Error al obtener clientes con equipos: {e}",
                operation="get_clients_with_teams",
                entity_type="Client",
                original_error=e
            )

    async def get_client_teams_count(
        self,
        client_id: UUID,
        include_inactive: bool = False
    ) -> int:
        """
        Obtiene el número de equipos asociados a un cliente.
        
        Args:
            client_id: ID del cliente
            include_inactive: Si incluir equipos inactivos
            
        Returns:
            int: Número de equipos del cliente
        """
        try:
            self._logger.debug(f"Contando equipos para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=str(client_id)
                )
            
            # TODO: Implementar conteo real cuando exista la entidad Team
            self._logger.warning("Conteo de equipos no implementado aún")
            
            # Por ahora retornamos 0
            team_count = 0
            
            self._logger.debug(f"Equipos para cliente {client_id}: {team_count}")
            
            return team_count
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al contar equipos del cliente {client_id}: {e}")
            raise RepositoryError(
                message=f"Error al contar equipos: {e}",
                operation="get_client_teams_count",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )



    async def get_clients_by_project_count_range(
        self,
        min_projects: int,
        max_projects: Optional[int] = None,
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Obtiene clientes por rango de número de proyectos.
        
        Args:
            min_projects: Número mínimo de proyectos
            max_projects: Número máximo de proyectos (None = sin límite)
            include_inactive: Si incluir clientes/proyectos inactivos
            
        Returns:
            List[Client]: Lista de clientes en el rango especificado
        """
        try:
            self._logger.debug(f"Obteniendo clientes por rango de proyectos: {min_projects}-{max_projects}")
            
            if min_projects < 0:
                raise ValidationError(
                    message="El número mínimo de proyectos debe ser mayor o igual a 0",
                    field="min_projects",
                    value=min_projects
                )
            
            if max_projects is not None and max_projects < min_projects:
                raise ValidationError(
                    message="El número máximo debe ser mayor o igual al mínimo",
                    field="max_projects",
                    value=max_projects
                )
            
            # TODO: Implementar filtrado real cuando exista la entidad Project
            self._logger.warning("Filtrado por rango de proyectos no implementado aún")
            
            # Por ahora retornamos lista vacía
            return []
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener clientes por rango de proyectos: {e}")
            raise RepositoryError(
                message=f"Error al filtrar por proyectos: {e}",
                operation="get_clients_by_project_count_range",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_relationship_summary(
        self,
        client_id: Optional[UUID] = None
    ) -> Dict[str, Any]:
        """
        Obtiene un resumen de las relaciones de un cliente o todos los clientes.
        
        Args:
            client_id: ID específico del cliente (None para todos)
            
        Returns:
            Dict[str, Any]: Resumen detallado de relaciones
        """
        try:
            if client_id:
                self._logger.debug(f"Obteniendo resumen de relaciones para cliente {client_id}")
                
                # Verificar que el cliente existe
                client = await self._client_repository.get_client_by_id(client_id)
                if not client:
                    raise ValidationError(
                        message=f"Cliente con ID {client_id} no encontrado",
                        field="client_id",
                        value=str(client_id)
                    )
                
                # Obtener conteos de relaciones
                project_count = await self.get_client_projects_count(client_id)
                team_count = await self.get_client_teams_count(client_id)
                
                summary = {
                    "client_id": str(client_id),
                    "client_name": client.name,
                    "client_code": client.code,
                    "is_active": client.is_active,
                    "relationships": {
                        "projects": {
                            "count": project_count,
                            "has_projects": project_count > 0
                        },
                        "teams": {
                            "count": team_count,
                            "has_teams": team_count > 0
                        }
                    },
                    "total_relationships": project_count + team_count,
                    "relationship_score": self._calculate_relationship_score(project_count, team_count)
                }
            else:
                self._logger.debug("Obteniendo resumen de relaciones para todos los clientes")
                
                # TODO: Implementar resumen global cuando sea necesario
                summary = {
                    "total_clients": 0,
                    "clients_with_projects": 0,
                    "clients_with_teams": 0,
                    "average_projects_per_client": 0.0,
                    "average_teams_per_client": 0.0
                }
            
            self._logger.debug(f"Resumen de relaciones generado")
            
            return summary
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener resumen de relaciones: {e}")
            raise RepositoryError(
                message=f"Error en resumen de relaciones: {e}",
                operation="get_clients_relationship_summary",
                entity_type="Client",
                entity_id=str(client_id) if client_id else None,
                original_error=e
            )

    async def validate_client_relationships(
        self,
        client_id: UUID
    ) -> Dict[str, Any]:
        """
        Valida la integridad de las relaciones de un cliente.
        
        Args:
            client_id: ID del cliente a validar
            
        Returns:
            Dict[str, Any]: Resultado de la validación con detalles
        """
        try:
            self._logger.debug(f"Validando integridad de relaciones para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=str(client_id)
                )
            
            validation_result = {
                "client_id": str(client_id),
                "is_valid": True,
                "issues": [],
                "warnings": [],
                "checks_performed": []
            }
            
            # Verificar estado del cliente vs relaciones
            validation_result["checks_performed"].append("client_status_check")
            if not client.is_active:
                project_count = await self.get_client_projects_count(client_id)
                if project_count > 0:
                    validation_result["warnings"].append(
                        f"Cliente inactivo tiene {project_count} proyectos asociados"
                    )
            
            # TODO: Agregar más validaciones cuando existan las entidades relacionadas
            validation_result["checks_performed"].extend([
                "project_references_check",
                "team_references_check",
                "orphaned_relationships_check"
            ])
            
            # Determinar si hay problemas críticos
            validation_result["is_valid"] = len(validation_result["issues"]) == 0
            
            self._logger.debug(f"Validación de integridad completada para cliente {client_id}")
            
            return validation_result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al validar integridad de relaciones: {e}")
            raise RepositoryError(
                message=f"Error en validación de integridad: {e}",
                operation="validate_client_relationships",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    async def get_clients_with_active_assignments(
        self,
        assignment_type: Optional[str] = None
    ) -> List[Client]:
        """
        Obtiene clientes que tienen asignaciones activas.
        
        Args:
            assignment_type: Tipo específico de asignación (None para todos)
            
        Returns:
            List[Client]: Lista de clientes con asignaciones activas
        """
        try:
            self._logger.debug("Obteniendo clientes con asignaciones activas")
            
            # TODO: Implementar cuando existan las entidades de asignación
            self._logger.warning("Funcionalidad de asignaciones no implementada aún")
            
            # Por ahora retornamos clientes activos como placeholder
            filters = {"is_active": True}
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Clientes con asignaciones activas (placeholder): {len(result)}")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al obtener clientes con asignaciones activas: {e}")
            raise RepositoryError(
                message=f"Error al obtener asignaciones activas: {e}",
                operation="get_clients_with_active_assignments",
                entity_type="Client",
                original_error=e
            )

    async def get_client_dependency_tree(
        self,
        client_id: UUID,
        max_depth: int = 3
    ) -> Dict[str, Any]:
        """
        Obtiene el árbol de dependencias de un cliente.
        
        Args:
            client_id: ID del cliente
            max_depth: Profundidad máxima del árbol
            
        Returns:
            Dict[str, Any]: Árbol de dependencias estructurado
        """
        try:
            self._logger.debug(f"Obteniendo árbol de dependencias para cliente {client_id}")
            
            # Verificar que el cliente existe
            client = await self._client_repository.get_client_by_id(client_id)
            if not client:
                raise ValidationError(
                    message=f"Cliente con ID {client_id} no encontrado",
                    field="client_id",
                    value=str(client_id)
                )
            
            # Construir árbol de dependencias básico
            dependency_tree = {
                "client": {
                    "id": str(client.id),
                    "name": client.name,
                    "code": client.code,
                    "is_active": client.is_active
                },
                "dependencies": {
                    "projects": [],  # TODO: Llenar cuando exista la entidad Project
                    "teams": [],     # TODO: Llenar cuando exista la entidad Team
                    "assignments": []  # TODO: Llenar cuando existan asignaciones
                },
                "dependency_count": 0,
                "can_be_deleted": True,  # Se actualizará basado en dependencias
                "blocking_dependencies": [],
                "max_depth": max_depth
            }
            
            # TODO: Implementar lógica real de dependencias
            self._logger.warning("Árbol de dependencias básico - implementación completa pendiente")
            
            self._logger.debug(f"Árbol de dependencias generado para cliente {client_id}")
            
            return dependency_tree
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error al obtener árbol de dependencias: {e}")
            raise RepositoryError(
                message=f"Error en árbol de dependencias: {e}",
                operation="get_client_dependency_tree",
                entity_type="Client",
                entity_id=str(client_id),
                original_error=e
            )

    def _calculate_relationship_score(self, project_count: int, team_count: int) -> float:
        """
        Calcula un puntaje de relaciones basado en el número de conexiones.
        
        Args:
            project_count: Número de proyectos
            team_count: Número de equipos
            
        Returns:
            float: Puntaje de relaciones (0.0 a 100.0)
        """
        # Puntaje base
        base_score = 0.0
        
        # Puntaje por proyectos (máximo 60 puntos)
        project_score = min(60.0, project_count * 15.0)
        
        # Puntaje por equipos (máximo 40 puntos)
        team_score = min(40.0, team_count * 20.0)
        
        total_score = base_score + project_score + team_score
        
        return min(100.0, total_score)