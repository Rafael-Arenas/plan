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
    TeamSchema, TeamSearchCriteria
)
from planificador.repositories.team import TeamRepositoryFacade
from planificador.services.domain.team.interfaces.search_operations_interface import (
    ITeamDomainSearchOperations, TeamStatus
)
from planificador.exceptions.domain import (
    TeamDomainError
)
from planificador.exceptions.base import (
    ValidationError
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
        exact_match: bool = False
    ) -> List[TeamSchema]:
        """
        Busca equipos por nombre o patrón de nombre con opciones de filtrado.
        
        Args:
            name_pattern: Patrón de nombre a buscar
            exact_match: Si buscar coincidencia exacta o parcial
            
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
                teams = [team] if team and team.is_active else []
            else:
                # Búsqueda parcial usando criterios
                search_criteria = {
                    "name_pattern": name_pattern,
                    "partial_match": True,
                    "is_active": True
                }
                    
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
        include_details: bool = False
    ) -> List[TeamSchema]:
        """
        Obtiene equipos filtrados por estado.
        
        Args:
            status: Estado de los equipos a buscar
            include_details: Si incluir detalles adicionales del equipo
            
        Returns:
            List[TeamSchema]: Lista de equipos con el estado especificado
            
        Raises:
            ValidationError: Si el estado no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info(f"Obteniendo equipos por estado: {status}")
            
            # Validar estado
            if not isinstance(status, TeamStatus):
                raise ValidationError(
                    message="Estado de equipo no válido",
                    details={"status": str(status)}
                )
            
            # Buscar equipos por estado
            teams = await self._team_repo.get_teams_by_status(status)
            
            # Aplicar filtros adicionales si se requieren detalles
            if include_details:
                # Cargar detalles adicionales si es necesario
                for team in teams:
                    # Aquí se podrían cargar miembros, proyectos, etc.
                    pass
            
            return teams
            
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
        department_id: int,
        include_members: bool = False
    ) -> List[TeamSchema]:
        """
        Obtiene equipos filtrados por departamento.
        
        Args:
            department_id: ID del departamento
            include_members: Si incluir información de miembros del equipo
            
        Returns:
            List[TeamSchema]: Lista de equipos del departamento especificado
            
        Raises:
            ValidationError: Si el department_id no es válido
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.debug(
                f"Buscando equipos por departamento ID: {department_id}"
            )
            
            # Validar department_id
            if not isinstance(department_id, int) or department_id <= 0:
                raise ValidationError(
                    message="ID de departamento no válido",
                    details={"department_id": department_id}
                )
            
            # Buscar equipos por departamento
            teams = await self._team_repo.get_teams_by_department(department_id)
            
            # Incluir miembros si se solicita
            if include_members:
                for team in teams:
                    # Cargar miembros del equipo
                    team.members = await self._team_repo.get_team_members(team.id)
            
            self._logger.debug(
                f"Equipos encontrados por departamento {department_id}: {len(teams)}"
            )
            
            return teams
            
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
        search_criteria: Dict[str, Any],
        include_details: bool = False,
        include_members: bool = False
    ) -> List[TeamSchema]:
        """
        Búsqueda avanzada de equipos con múltiples criterios.
        
        Args:
            search_criteria: Diccionario con criterios de búsqueda
            include_details: Si incluir detalles adicionales del equipo
            include_members: Si incluir información de miembros del equipo
            
        Returns:
            List[TeamSchema]: Lista de equipos que cumplen los criterios
            
        Raises:
            ValidationError: Si los criterios de búsqueda no son válidos
            TeamDomainError: Si ocurre un error inesperado
        """
        try:
            self._logger.info("Realizando búsqueda avanzada de equipos")
            
            # Validar criterios de búsqueda
            if not isinstance(search_criteria, dict) or not search_criteria:
                raise ValidationError(
                    message="Los criterios de búsqueda son obligatorios",
                    details={"search_criteria": search_criteria}
                )
            
            # Realizar búsqueda avanzada
            teams = await self._team_repo.search_teams_by_criteria(search_criteria)
            
            # Aplicar filtros adicionales según las opciones
            if include_details or include_members:
                for team in teams:
                    if include_details:
                        # Cargar detalles adicionales del equipo
                        pass
                    if include_members:
                        # Cargar miembros del equipo
                        team.members = await self._team_repo.get_team_members(team.id)
            
            return teams
            
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