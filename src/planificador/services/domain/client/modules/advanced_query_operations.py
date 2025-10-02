# src/planificador/services/domain/client/modules/advanced_query_operations.py

"""
Módulo de operaciones de consulta avanzada para el servicio de dominio de cliente.

Este módulo implementa consultas complejas y especializadas para la entidad Cliente,
incluyendo búsquedas con filtros dinámicos, paginación, ordenamiento y joins complejos.
"""

from typing import Any, Dict, List, Optional, Tuple

import pendulum
from loguru import logger

from planificador.exceptions import RepositoryError, ValidationError
from planificador.repositories.client.client_repository_facade import ClientRepositoryFacade
from planificador.schemas import Client
from planificador.services.domain.client.interfaces.advanced_query_interface import IAdvancedQueryOperations


class AdvancedQueryOperations(IAdvancedQueryOperations):
    """
    Implementación de operaciones de consulta avanzada para el dominio de cliente.
    
    Esta clase encapsula consultas complejas, búsquedas con filtros dinámicos,
    paginación avanzada y operaciones de análisis de datos.
    """

    def __init__(self, client_repository: ClientRepositoryFacade):
        """
        Inicializa el módulo de operaciones de consulta avanzada.
        
        Args:
            client_repository: Facade del repositorio de cliente
        """
        self._client_repository = client_repository
        self._logger = logger

    async def search_clients_advanced(
        self,
        filters: Dict[str, Any],
        sort_by: Optional[str] = None,
        sort_order: str = "asc",
        limit: Optional[int] = None,
        offset: int = 0
    ) -> Tuple[List[Client], int]:
        """
        Realiza una búsqueda avanzada con filtros dinámicos, ordenamiento y paginación.
        
        Args:
            filters: Diccionario de filtros a aplicar
            sort_by: Campo por el cual ordenar
            sort_order: Orden de clasificación ('asc' o 'desc')
            limit: Número máximo de resultados
            offset: Número de resultados a omitir
            
        Returns:
            Tuple[List[Client], int]: Lista de clientes y total de registros
        """
        try:
            self._logger.debug(f"Búsqueda avanzada con filtros: {filters}")
            
            # Validar parámetros de ordenamiento
            if sort_order not in ["asc", "desc"]:
                raise ValidationError(
                    message="El orden debe ser 'asc' o 'desc'",
                    field="sort_order",
                    value=sort_order
                )
            
            # Realizar búsqueda con filtros
            clients = await self._client_repository.get_clients_by_filters(
                filters=filters,
                limit=limit,
                offset=offset
            )
            
            # Obtener total de registros para paginación
            total_count = await self._client_repository.count_clients_by_filters(filters)
            
            # Convertir a esquemas de dominio
            result_clients = [Client.model_validate(client) for client in clients]
            
            # Aplicar ordenamiento si se especifica
            if sort_by:
                result_clients = self._sort_clients(result_clients, sort_by, sort_order)
            
            self._logger.debug(f"Búsqueda avanzada completada: {len(result_clients)} de {total_count}")
            
            return result_clients, total_count
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en búsqueda avanzada: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda avanzada: {e}",
                operation="search_clients_advanced",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_paginated(
        self,
        page: int = 1,
        page_size: int = 20,
        sort_by: Optional[str] = None,
        sort_order: str = "asc"
    ) -> Tuple[List[Client], int, int]:
        """
        Obtiene clientes con paginación avanzada.
        
        Args:
            page: Número de página (empezando en 1)
            page_size: Tamaño de página
            sort_by: Campo por el cual ordenar
            sort_order: Orden de clasificación
            
        Returns:
            Tuple[List[Client], int, int]: Clientes, total de registros, total de páginas
        """
        try:
            self._logger.debug(f"Paginación: página {page}, tamaño {page_size}")
            
            # Validar parámetros
            if page < 1:
                raise ValidationError(
                    message="El número de página debe ser mayor a 0",
                    field="page",
                    value=page
                )
            
            if page_size < 1 or page_size > 1000:
                raise ValidationError(
                    message="El tamaño de página debe estar entre 1 y 1000",
                    field="page_size",
                    value=page_size
                )
            
            # Calcular offset
            offset = (page - 1) * page_size
            
            # Obtener clientes paginados
            clients, total_count = await self.search_clients_advanced(
                filters={},
                sort_by=sort_by,
                sort_order=sort_order,
                limit=page_size,
                offset=offset
            )
            
            # Calcular total de páginas
            total_pages = (total_count + page_size - 1) // page_size
            
            self._logger.debug(f"Paginación completada: página {page} de {total_pages}")
            
            return clients, total_count, total_pages
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en paginación: {e}")
            raise RepositoryError(
                message=f"Error en paginación: {e}",
                operation="get_clients_paginated",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_by_date_range(
        self,
        start_date: pendulum.DateTime,
        end_date: pendulum.DateTime,
        date_field: str = "created_at"
    ) -> List[Client]:
        """
        Busca clientes en un rango de fechas específico.
        
        Args:
            start_date: Fecha de inicio del rango
            end_date: Fecha de fin del rango
            date_field: Campo de fecha a usar para el filtro
            
        Returns:
            List[Client]: Lista de clientes en el rango de fechas
        """
        try:
            self._logger.debug(f"Búsqueda por rango de fechas: {start_date} - {end_date}")
            
            # Validar rango de fechas
            if start_date > end_date:
                raise ValidationError(
                    message="La fecha de inicio debe ser anterior a la fecha de fin",
                    field="date_range",
                    value=f"{start_date} - {end_date}"
                )
            
            # Crear filtros de fecha
            filters = {
                f"{date_field}__gte": start_date,
                f"{date_field}__lte": end_date
            }
            
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Encontrados {len(result)} clientes en rango de fechas")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en búsqueda por rango de fechas: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda por fechas: {e}",
                operation="search_clients_by_date_range",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_fuzzy(
        self,
        search_term: str,
        similarity_threshold: float = 0.6
    ) -> List[Client]:
        """
        Realiza una búsqueda difusa (fuzzy) de clientes.
        
        Args:
            search_term: Término de búsqueda
            similarity_threshold: Umbral de similitud (0.0 a 1.0)
            
        Returns:
            List[Client]: Lista de clientes que coinciden con la búsqueda difusa
        """
        try:
            self._logger.debug(f"Búsqueda difusa: '{search_term}' (umbral: {similarity_threshold})")
            
            # Validar umbral de similitud
            if not 0.0 <= similarity_threshold <= 1.0:
                raise ValidationError(
                    message="El umbral de similitud debe estar entre 0.0 y 1.0",
                    field="similarity_threshold",
                    value=similarity_threshold
                )
            
            # Por ahora, implementamos búsqueda difusa básica usando LIKE
            # En el futuro se puede integrar con bibliotecas especializadas
            clients = await self._client_repository.search_clients_by_text(
                search_text=search_term,
                fields=["name", "email", "contact_person"]
            )
            
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Búsqueda difusa completada: {len(result)} resultados")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en búsqueda difusa: {e}")
            raise RepositoryError(
                message=f"Error en búsqueda difusa: {e}",
                operation="search_clients_fuzzy",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_with_complex_joins(
        self,
        include_projects: bool = False,
        include_teams: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """
        Obtiene clientes con joins complejos a entidades relacionadas.
        
        Args:
            include_projects: Incluir información de proyectos
            include_teams: Incluir información de equipos
            filters: Filtros adicionales a aplicar
            
        Returns:
            List[Client]: Lista de clientes con datos relacionados
        """
        try:
            self._logger.debug(f"Consulta con joins complejos (projects: {include_projects}, teams: {include_teams})")
            
            if filters is None:
                filters = {}
            
            # Por ahora, obtenemos clientes básicos
            # En el futuro se implementarán los joins reales cuando existan las entidades relacionadas
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            # TODO: Implementar joins reales cuando existan las entidades Project y Team
            if include_projects:
                self._logger.warning("Join con proyectos no implementado aún")
            
            if include_teams:
                self._logger.warning("Join con equipos no implementado aún")
            
            self._logger.debug(f"Consulta con joins completada: {len(result)} clientes")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en consulta con joins complejos: {e}")
            raise RepositoryError(
                message=f"Error en consulta con joins: {e}",
                operation="get_clients_with_complex_joins",
                entity_type="Client",
                original_error=e
            )

    async def filter_clients_by_criteria(
        self,
        criteria: Dict[str, Any]
    ) -> List[Client]:
        """
        Filtra clientes usando criterios complejos.
        
        Args:
            criteria: Diccionario de criterios de filtrado
            
        Returns:
            List[Client]: Lista de clientes que cumplen los criterios
        """
        try:
            self._logger.debug(f"Filtrado por criterios complejos: {criteria}")
            
            # Procesar criterios y convertir a filtros del repositorio
            processed_filters = self._process_filter_criteria(criteria)
            
            clients = await self._client_repository.get_clients_by_filters(processed_filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Filtrado completado: {len(result)} clientes")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en filtrado por criterios: {e}")
            raise RepositoryError(
                message=f"Error en filtrado: {e}",
                operation="filter_clients_by_criteria",
                entity_type="Client",
                original_error=e
            )

    async def count_clients_by_filters(self, filters: Dict[str, Any]) -> int:
        """
        Cuenta clientes que coinciden con los filtros especificados.
        
        Args:
            filters: Diccionario de filtros
            
        Returns:
            int: Número de clientes que coinciden
        """
        try:
            self._logger.debug(f"Contando clientes con filtros: {filters}")
            
            count = await self._client_repository.count_clients_by_filters(filters)
            
            self._logger.debug(f"Conteo completado: {count} clientes")
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error al contar clientes: {e}")
            raise RepositoryError(
                message=f"Error al contar clientes: {e}",
                operation="count_clients_by_filters",
                entity_type="Client",
                original_error=e
            )

    def _sort_clients(
        self,
        clients: List[Client],
        sort_by: str,
        sort_order: str
    ) -> List[Client]:
        """
        Ordena una lista de clientes por el campo especificado.
        
        Args:
            clients: Lista de clientes a ordenar
            sort_by: Campo por el cual ordenar
            sort_order: Orden de clasificación
            
        Returns:
            List[Client]: Lista de clientes ordenada
        """
        try:
            # Validar que el campo existe en el modelo
            valid_fields = ["id", "name", "code", "email", "is_active", "created_at", "updated_at"]
            
            if sort_by not in valid_fields:
                self._logger.warning(f"Campo de ordenamiento no válido: {sort_by}")
                return clients
            
            # Ordenar por el campo especificado
            reverse = sort_order == "desc"
            
            return sorted(
                clients,
                key=lambda x: getattr(x, sort_by, ""),
                reverse=reverse
            )
            
        except Exception as e:
            self._logger.error(f"Error al ordenar clientes: {e}")
            return clients

    def _process_filter_criteria(self, criteria: Dict[str, Any]) -> Dict[str, Any]:
        """
        Procesa criterios de filtrado complejos y los convierte a filtros del repositorio.
        
        Args:
            criteria: Criterios de filtrado originales
            
        Returns:
            Dict[str, Any]: Filtros procesados para el repositorio
        """
        processed = {}
        
        for key, value in criteria.items():
            # Procesar operadores especiales
            if key.endswith("__contains"):
                # Búsqueda que contiene texto
                processed[key] = value
            elif key.endswith("__icontains"):
                # Búsqueda que contiene texto (case insensitive)
                processed[key] = value
            elif key.endswith("__gte"):
                # Mayor o igual que
                processed[key] = value
            elif key.endswith("__lte"):
                # Menor o igual que
                processed[key] = value
            elif key.endswith("__in"):
                # Valor en lista
                processed[key] = value
            elif key.endswith("__not"):
                # No igual a
                processed[key] = value
            else:
                # Filtro directo
                processed[key] = value
        
        return processed