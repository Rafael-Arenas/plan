# src/planificador/services/domain/team/modules/search_operations.py

"""
Módulo de Operaciones de Búsqueda del Dominio Team.

Este módulo implementa las operaciones de búsqueda y filtrado de equipos,
proporcionando funcionalidad avanzada para encontrar equipos basándose
en diferentes criterios como nombre, estado, departamento y búsquedas complejas.

Características:
    - Búsqueda por nombre con coincidencias parciales
    - Filtrado por estado y departamento
    - Búsquedas avanzadas con múltiples criterios
    - Optimización de consultas para performance
    - Logging detallado de operaciones de búsqueda

Principios de Diseño:
    - Single Responsibility: Solo operaciones de búsqueda
    - Performance: Consultas optimizadas y eficientes
    - Flexibility: Múltiples criterios de búsqueda
    - User Experience: Búsquedas intuitivas y útiles

Uso:
    ```python
    search_ops = TeamDomainSearchOperations(team_repo)
    teams = await search_ops.find_teams_by_name("desarrollo")
    active_teams = await search_ops.find_teams_by_status(TeamStatus.ACTIVE)
    ```
"""

from typing import List, Optional, Dict, Any
from loguru import logger

from planificador.schemas.team.team_advanced_schemas import (
    TeamSchema, TeamSearchCriteria, PaginatedResponse
)
from planificador.repositories.team import TeamRepositoryFacade
from planificador.services.domain.team.interfaces.search_operations_interface import (
    ITeamDomainSearchOperations, TeamStatus
)
from planificador.exceptions.domain import (
    TeamDomainError, ValidationError
)
from planificador.exceptions.repository import TeamRepositoryError


class TeamDomainSearchOperations(ITeamDomainSearchOperations):
    """
    Implementación de operaciones de búsqueda del dominio Team.
    
    Proporciona funcionalidad avanzada de búsqueda y filtrado de equipos
    con validaciones apropiadas y optimización de consultas.
    
    Attributes:
        _team_repo: Repositorio de equipos
        _logger: Logger para registro de eventos
    """

    def __init__(self, team_repo: TeamRepositoryFacade):
        """
        Inicializa las operaciones de búsqueda del dominio Team.
        
        Args:
            team_repo: Repositorio de equipos
        """
        self._team_repo = team_repo
        self._logger = logger.bind(module="TeamDomainSearchOperations")
        
        self._logger.debug("TeamDomainSearchOperations inicializado")

    async def find_teams_by_name(
        self,
        name_pattern: str,
        exact_match: bool = False,
        include_inactive: bool = False
    ) -> List[TeamSchema]:
        """
        Busca equipos por nombre o patrón de nombre con opciones de filtrado.
        
        Args:
            name_pattern: Patrón de nombre a buscar
            exact_match: Si buscar coincidencia exacta o parcial
            include_inactive: Si incluir equipos inactivos
            
        Returns:
            List[TeamSchema]: Lista de equipos encontrados
            
        Raises:
            ValidationError: Si el patrón de búsqueda no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Buscando equipos por nombre: '{name_pattern}' "
                f"({'exacto' if exact_match else 'parcial'})"
            )
            
            # Validar patrón de búsqueda
            if not name_pattern or not isinstance(name_pattern, str):
                raise ValidationError("El patrón de nombre es obligatorio")
            
            name_pattern = name_pattern.strip()
            if len(name_pattern) < 2:
                raise ValidationError(
                    "El patrón de búsqueda debe tener al menos 2 caracteres"
                )
            
            # Buscar equipos en el repositorio
            if exact_match:
                # Búsqueda exacta
                team = await self._team_repo.get_team_by_name(name_pattern)
                teams = [team] if team and (include_inactive or team.is_active) else []
            else:
                # Búsqueda parcial usando criterios
                search_criteria = {
                    "name_pattern": name_pattern,
                    "partial_match": True
                }
                if not include_inactive:
                    search_criteria["is_active"] = True
                    
                teams = await self._team_repo.search_teams_by_criteria(search_criteria)
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            self._logger.debug(
                f"Equipos encontrados por nombre: {len(team_schemas)}"
            )
            
            return team_schemas
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en búsqueda por nombre: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por nombre: {e.message}",
                operation="find_teams_by_name",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda por nombre: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por nombre: {str(e)}",
                operation="find_teams_by_name",
                entity_type="Team",
                original_error=e
            )

    async def get_teams_by_status(
        self,
        status: TeamStatus,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene equipos filtrados por estado con paginación.
        
        Args:
            status: Estado del equipo a filtrar
            page: Número de página (inicia en 1)
            page_size: Tamaño de página
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos
            
        Raises:
            ValidationError: Si los parámetros de paginación no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Obteniendo equipos por estado: {status}")
            
            # Validar parámetros de paginación
            if page < 1:
                raise ValidationError("El número de página debe ser mayor a 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("El tamaño de página debe estar entre 1 y 100")
            
            # Buscar equipos por estado con paginación
            is_active = status == TeamStatus.ACTIVE
            teams, total_count = await self._team_repo.get_teams_by_status(
                is_active=is_active,
                page=page,
                page_size=page_size
            )
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            # Crear respuesta paginada
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            paginated_response = PaginatedResponse(
                items=team_schemas,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
            self._logger.debug(
                f"Equipos encontrados por estado {status}: {len(team_schemas)}"
            )
            
            return paginated_response
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en búsqueda por estado: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por estado: {e.message}",
                operation="find_teams_by_status",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda por estado: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por estado: {str(e)}",
                operation="find_teams_by_status",
                entity_type="Team",
                original_error=e
            )

    async def get_teams_by_department(
        self,
        department: str,
        include_inactive: bool = False,
        page: int = 1,
        page_size: int = 10
    ) -> PaginatedResponse[TeamSchema]:
        """
        Obtiene equipos filtrados por departamento con paginación.
        
        Args:
            department: Nombre del departamento
            include_inactive: Si incluir equipos inactivos
            page: Número de página (inicia en 1)
            page_size: Tamaño de página
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos
            
        Raises:
            ValidationError: Si los parámetros no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Buscando equipos por departamento: '{department}' "
                f"({'activos' if active_only else 'todos'})"
            )
            
            # Validar departamento
            if not department or not isinstance(department, str):
                raise ValidationError("El departamento es obligatorio")
            
            department = department.strip()
            if len(department) < 2:
                raise ValidationError(
                    "El departamento debe tener al menos 2 caracteres"
                )
            
            # Validar parámetros de paginación
            if page < 1:
                raise ValidationError("El número de página debe ser mayor a 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("El tamaño de página debe estar entre 1 y 100")
            
            # Buscar equipos en el repositorio con paginación
            active_only = not include_inactive
            teams, total_count = await self._team_repo.get_teams_by_department(
                department, active_only=active_only, page=page, page_size=page_size
            )
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            # Crear respuesta paginada
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            paginated_response = PaginatedResponse(
                items=team_schemas,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
            self._logger.debug(
                f"Equipos encontrados por departamento '{department}': {len(team_schemas)}"
            )
            
            return paginated_response
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en búsqueda por departamento: {e}")
            raise TeamDomainError(
                f"Error al buscar equipos por departamento: {e.message}",
                operation="get_teams_by_department",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda por departamento: {e}")
            raise TeamDomainError(
                f"Error inesperado al buscar equipos por departamento: {str(e)}",
                operation="get_teams_by_department",
                entity_type="Team",
                original_error=e
            )

    async def search_teams_advanced(
        self,
        criteria: TeamSearchCriteria
    ) -> PaginatedResponse[TeamSchema]:
        """
        Búsqueda avanzada de equipos con múltiples criterios y paginación.
        
        Args:
            criteria: Criterios de búsqueda avanzada
            
        Returns:
            PaginatedResponse[TeamSchema]: Respuesta paginada con equipos
            
        Raises:
            ValidationError: Si los criterios de búsqueda no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info("Realizando búsqueda avanzada de equipos")
            
            # Validar criterios de búsqueda
            if not criteria:
                raise ValidationError("Los criterios de búsqueda son requeridos")
            
            # Validar parámetros de paginación
            page = getattr(criteria, 'page', 1)
            page_size = getattr(criteria, 'page_size', 10)
            
            if page < 1:
                raise ValidationError("El número de página debe ser mayor a 0")
            if page_size < 1 or page_size > 100:
                raise ValidationError("El tamaño de página debe estar entre 1 y 100")
            
            # Convertir criterios a diccionario para el repositorio
            search_dict = criteria.model_dump(exclude_unset=True)
            
            # Buscar equipos con criterios avanzados
            teams, total_count = await self._team_repo.search_teams_by_criteria(
                search_dict, page=page, page_size=page_size
            )
            
            # Convertir a schemas de salida
            team_schemas = [TeamSchema.model_validate(team) for team in teams]
            
            # Crear respuesta paginada
            total_pages = (total_count + page_size - 1) // page_size
            has_next = page < total_pages
            has_previous = page > 1
            
            paginated_response = PaginatedResponse(
                items=team_schemas,
                total_count=total_count,
                page=page,
                page_size=page_size,
                total_pages=total_pages,
                has_next=has_next,
                has_previous=has_previous
            )
            
            self._logger.debug(
                f"Equipos encontrados con búsqueda avanzada: {len(team_schemas)}"
            )
            
            return paginated_response
            
        except TeamRepositoryError as e:
            self._logger.error(f"Error de repositorio en búsqueda avanzada: {e}")
            raise TeamDomainError(
                f"Error en búsqueda avanzada: {e.message}",
                operation="search_teams_advanced",
                entity_type="Team",
                original_error=e
            )
        except ValidationError:
            raise
        except Exception as e:
            self._logger.error(f"Error inesperado en búsqueda avanzada: {e}")
            raise TeamDomainError(
                f"Error inesperado en búsqueda avanzada: {str(e)}",
                operation="search_teams_advanced",
                entity_type="Team",
                original_error=e
            )

    async def _validate_search_criteria(
        self,
        criteria: Dict[str, Any]
    ) -> Dict[str, Any]:
        """
        Valida y limpia los criterios de búsqueda.
        
        Args:
            criteria: Criterios de búsqueda a validar
            
        Returns:
            Dict[str, Any]: Criterios validados y limpios
            
        Raises:
            ValidationError: Si algún criterio no es válido
        """
        validated = {}
        
        # Validar nombre si está presente
        if 'name' in criteria:
            name = criteria['name']
            if name and isinstance(name, str):
                name = name.strip()
                if len(name) >= 2:
                    validated['name'] = name
                else:
                    raise ValidationError(
                        "El criterio de nombre debe tener al menos 2 caracteres"
                    )
        
        # Validar patrón de nombre si está presente
        if 'name_pattern' in criteria:
            pattern = criteria['name_pattern']
            if pattern and isinstance(pattern, str):
                pattern = pattern.strip()
                if len(pattern) >= 2:
                    validated['name_pattern'] = pattern
                else:
                    raise ValidationError(
                        "El patrón de nombre debe tener al menos 2 caracteres"
                    )
        
        # Validar departamento si está presente
        if 'department' in criteria:
            department = criteria['department']
            if department and isinstance(department, str):
                department = department.strip()
                if len(department) >= 2:
                    validated['department'] = department
                else:
                    raise ValidationError(
                        "El criterio de departamento debe tener al menos 2 caracteres"
                    )
        
        # Validar estado activo si está presente
        if 'is_active' in criteria:
            is_active = criteria['is_active']
            if isinstance(is_active, bool):
                validated['is_active'] = is_active
            else:
                raise ValidationError(
                    "El criterio 'is_active' debe ser booleano"
                )
        
        # Validar fechas si están presentes
        if 'created_after' in criteria:
            created_after = criteria['created_after']
            if created_after:
                validated['created_after'] = created_after
        
        if 'created_before' in criteria:
            created_before = criteria['created_before']
            if created_before:
                validated['created_before'] = created_before
        
        # Validar coincidencia parcial si está presente
        if 'partial_match' in criteria:
            partial_match = criteria['partial_match']
            if isinstance(partial_match, bool):
                validated['partial_match'] = partial_match
        
        # Validar que al menos hay un criterio válido
        if not validated:
            raise ValidationError(
                "Debe proporcionar al menos un criterio de búsqueda válido"
            )
        
        return validated