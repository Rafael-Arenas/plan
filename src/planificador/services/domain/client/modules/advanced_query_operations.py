# src/planificador/services/domain/client/modules/advanced_query_operations.py

"""
Módulo de operaciones de consulta avanzada para el servicio de dominio de cliente.

Este módulo implementa consultas complejas y especializadas para la entidad Cliente,
incluyendo búsquedas con filtros dinámicos, paginación, ordenamiento y joins complejos.
"""

from typing import Any, Dict, List, Optional, Tuple
from datetime import datetime

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
        pagination: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None,
        include_relationships: bool = False
    ) -> Tuple[List[Client], int]:
        """
        Búsqueda avanzada de clientes con filtros dinámicos.
        
        Args:
            filters: Diccionario de filtros dinámicos
            pagination: Parámetros de paginación
            sorting: Lista de parámetros de ordenamiento
            include_relationships: Si incluir relaciones
            
        Returns:
            Tuple[List[Client], int]: (clientes, total_count)
        """
        try:
            self._logger.debug(f"Búsqueda avanzada con filtros: {filters}")
            
            # Procesar paginación
            limit = None
            offset = 0
            if pagination:
                limit = pagination.get("limit")
                offset = pagination.get("offset", 0)
            
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
            if sorting:
                result_clients = self._apply_sorting(result_clients, sorting)
            
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

    async def filter_clients_by_criteria(
        self,
        criteria: Dict[str, Any],
        operator: str = "AND",
        limit: Optional[int] = None
    ) -> List[Client]:
        """
        Filtra clientes usando criterios complejos.
        
        Args:
            criteria: Criterios de filtrado
            operator: Operador lógico (AND, OR)
            limit: Límite de resultados
            
        Returns:
            List[Client]: Lista de clientes filtrados
        """
        try:
            self._logger.debug(f"Filtrado por criterios complejos: {criteria}")
            
            # Procesar criterios y convertir a filtros del repositorio
            processed_filters = self._process_filter_criteria(criteria)
            
            clients = await self._client_repository.get_clients_by_filters(
                filters=processed_filters,
                limit=limit
            )
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

    async def get_clients_with_pagination(
        self,
        page: int = 1,
        page_size: int = 20,
        filters: Optional[Dict[str, Any]] = None,
        sorting: Optional[List[Dict[str, Any]]] = None
    ) -> Tuple[List[Client], int, int]:
        """
        Obtiene clientes con paginación.
        
        Args:
            page: Número de página (base 1)
            page_size: Tamaño de página
            filters: Filtros opcionales
            sorting: Ordenamiento opcional
            
        Returns:
            Tuple[List[Client], int, int]: (clientes, total_count, total_pages)
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
            
            # Usar filtros vacíos si no se proporcionan
            if filters is None:
                filters = {}
            
            # Obtener clientes paginados
            clients, total_count = await self.search_clients_advanced(
                filters=filters,
                pagination={"limit": page_size, "offset": offset},
                sorting=sorting
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
                operation="get_clients_with_pagination",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_by_date_range(
        self,
        start_date: datetime,
        end_date: datetime,
        date_field: str = "created_at",
        include_inactive: bool = False
    ) -> List[Client]:
        """
        Busca clientes por rango de fechas.
        
        Args:
            start_date: Fecha de inicio
            end_date: Fecha de fin
            date_field: Campo de fecha a usar
            include_inactive: Si incluir clientes inactivos
            
        Returns:
            List[Client]: Lista de clientes en el rango
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
            
            # Agregar filtro de estado si es necesario
            if not include_inactive:
                filters["is_active"] = True
            
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

    async def get_clients_by_multiple_filters(
        self,
        name_filter: Optional[str] = None,
        email_filter: Optional[str] = None,
        phone_filter: Optional[str] = None,
        status_filter: Optional[str] = None,
        type_filter: Optional[str] = None,
        combine_with_and: bool = True
    ) -> List[Client]:
        """
        Obtiene clientes aplicando múltiples filtros.
        
        Args:
            name_filter: Filtro por nombre
            email_filter: Filtro por email
            phone_filter: Filtro por teléfono
            status_filter: Filtro por estado
            type_filter: Filtro por tipo
            combine_with_and: Si combinar filtros con AND (True) o OR (False)
            
        Returns:
            List[Client]: Lista de clientes filtrados
        """
        try:
            self._logger.debug("Aplicando múltiples filtros")
            
            filters = {}
            
            # Construir filtros dinámicamente
            if name_filter:
                filters["name__icontains"] = name_filter
            if email_filter:
                filters["email__icontains"] = email_filter
            if phone_filter:
                filters["phone__icontains"] = phone_filter
            if status_filter:
                filters["is_active"] = status_filter.lower() == "active"
            if type_filter:
                filters["client_type"] = type_filter
            
            # Por ahora, solo soportamos AND (el repositorio maneja esto por defecto)
            # TODO: Implementar lógica OR cuando el repositorio lo soporte
            if not combine_with_and:
                self._logger.warning("Lógica OR no implementada aún, usando AND")
            
            clients = await self._client_repository.get_clients_by_filters(filters)
            result = [Client.model_validate(client) for client in clients]
            
            self._logger.debug(f"Múltiples filtros aplicados: {len(result)} clientes")
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error en múltiples filtros: {e}")
            raise RepositoryError(
                message=f"Error en múltiples filtros: {e}",
                operation="get_clients_by_multiple_filters",
                entity_type="Client",
                original_error=e
            )

    async def search_clients_fuzzy(
        self,
        search_term: str,
        similarity_threshold: float = 0.7,
        max_results: int = 50
    ) -> List[Client]:
        """
        Búsqueda difusa de clientes.
        
        Args:
            search_term: Término de búsqueda
            similarity_threshold: Umbral de similitud (0.0 - 1.0)
            max_results: Máximo número de resultados
            
        Returns:
            List[Client]: Lista de clientes con coincidencias difusas
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
            
            # Limitar resultados
            if len(clients) > max_results:
                clients = clients[:max_results]
            
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

    async def get_clients_sorted(
        self,
        sort_by: str,
        sort_order: str = "asc",
        include_inactive: bool = False,
        limit: Optional[int] = None
    ) -> List[Client]:
        """
        Obtiene clientes ordenados por un campo específico.
        
        Args:
            sort_by: Campo por el cual ordenar
            sort_order: Orden (asc, desc)
            include_inactive: Si incluir clientes inactivos
            limit: Límite de resultados
            
        Returns:
            List[Client]: Lista de clientes ordenados
        """
        try:
            self._logger.debug(f"Ordenando clientes por {sort_by} ({sort_order})")
            
            # Validar orden
            if sort_order not in ["asc", "desc"]:
                raise ValidationError(
                    message="El orden debe ser 'asc' o 'desc'",
                    field="sort_order",
                    value=sort_order
                )
            
            # Crear filtros
            filters = {}
            if not include_inactive:
                filters["is_active"] = True
            
            # Obtener clientes
            clients = await self._client_repository.get_clients_by_filters(
                filters=filters,
                limit=limit
            )
            
            result = [Client.model_validate(client) for client in clients]
            
            # Aplicar ordenamiento
            result = self._sort_clients(result, sort_by, sort_order)
            
            self._logger.debug(f"Ordenamiento completado: {len(result)} clientes")
            
            return result
            
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error en ordenamiento: {e}")
            raise RepositoryError(
                message=f"Error en ordenamiento: {e}",
                operation="get_clients_sorted",
                entity_type="Client",
                original_error=e
            )

    async def count_clients_by_criteria(
        self,
        criteria: Dict[str, Any],
        operator: str = "AND"
    ) -> int:
        """
        Cuenta clientes que cumplen criterios específicos.
        
        Args:
            criteria: Criterios de filtrado
            operator: Operador lógico (AND, OR)
            
        Returns:
            int: Número de clientes que cumplen los criterios
        """
        try:
            self._logger.debug(f"Contando clientes con criterios: {criteria}")
            
            # Procesar criterios
            processed_filters = self._process_filter_criteria(criteria)
            
            # Por ahora, solo soportamos AND
            if operator != "AND":
                self._logger.warning(f"Operador {operator} no implementado aún, usando AND")
            
            count = await self._client_repository.count_clients_by_filters(processed_filters)
            
            self._logger.debug(f"Conteo completado: {count} clientes")
            
            return count
            
        except Exception as e:
            self._logger.error(f"Error al contar clientes: {e}")
            raise RepositoryError(
                message=f"Error al contar clientes: {e}",
                operation="count_clients_by_criteria",
                entity_type="Client",
                original_error=e
            )

    async def get_clients_with_complex_joins(
        self,
        include_projects: bool = False,
        include_teams: bool = False,
        include_assignments: bool = False,
        filters: Optional[Dict[str, Any]] = None
    ) -> List[Client]:
        """
        Obtiene clientes con joins complejos a entidades relacionadas.
        
        Args:
            include_projects: Si incluir proyectos del cliente
            include_teams: Si incluir equipos del cliente
            include_assignments: Si incluir asignaciones del cliente
            filters: Filtros adicionales
            
        Returns:
            List[Client]: Lista de clientes con relaciones cargadas
        """
        try:
            self._logger.debug(f"Consulta con joins complejos (projects: {include_projects}, teams: {include_teams}, assignments: {include_assignments})")
            
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
                
            if include_assignments:
                self._logger.warning("Join con asignaciones no implementado aún")
            
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

    def _apply_sorting(
        self,
        clients: List[Client],
        sorting: List[Dict[str, Any]]
    ) -> List[Client]:
        """
        Aplica múltiples criterios de ordenamiento a una lista de clientes.
        
        Args:
            clients: Lista de clientes a ordenar
            sorting: Lista de criterios de ordenamiento
            
        Returns:
            List[Client]: Lista de clientes ordenada
        """
        try:
            result = clients.copy()
            
            # Aplicar ordenamientos en orden inverso (el último tiene prioridad)
            for sort_criteria in reversed(sorting):
                field = sort_criteria.get("field")
                order = sort_criteria.get("order", "asc")
                
                if field:
                    result = self._sort_clients(result, field, order)
            
            return result
            
        except Exception as e:
            self._logger.error(f"Error al aplicar ordenamiento múltiple: {e}")
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